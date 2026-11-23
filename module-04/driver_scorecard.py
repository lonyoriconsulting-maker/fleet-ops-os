"""
driver_scorecard.py
Module 4 — Driver Behaviour Scorecards
Reads per-driver weekly telematics metrics + km + fuel, computes a weighted
composite score (0-100), ranks drivers, flags the bottom quartile.

Input: driver_scorecard_input.csv with columns:
  driver_id, route_id, km, fuel_litres, expected_litres,
  harsh_braking, harsh_accel, overspeed_events, idling_pct, incidents

Benchmarks (good, bad) per KPI — adjust once you have 4-8 weeks of fleet data.
"""

import csv
import sys

# --- Benchmark bands: (good, bad). Sub-score = 100*(bad-actual)/(bad-good), clamped 0-100.
BENCHMARKS = {
    "harsh_braking_per_1k": (2.0, 20.0),
    "harsh_accel_per_1k":   (2.0, 20.0),
    "overspeed_per_1k":     (1.0, 15.0),
    "idling_pct":           (8.0, 35.0),
    "fuel_variance_pct":    (2.0, 25.0),   # absolute value used
    "incidents_per_1k":     (0.0, 3.0),
}

# --- Weights (must sum to 100). Re-weight to the business's current constraint.
WEIGHTS = {
    "harsh_braking_per_1k": 20,
    "harsh_accel_per_1k":   15,
    "overspeed_per_1k":     20,
    "idling_pct":           15,
    "fuel_variance_pct":    20,
    "incidents_per_1k":     10,
}

def sub_score(actual, good, bad):
    if bad == good:
        return 100.0
    s = 100.0 * (bad - actual) / (bad - good)
    return max(0.0, min(100.0, s))

def compute_row(row):
    km = float(row["km"])
    fuel = float(row["fuel_litres"])
    expected = float(row["expected_litres"])
    # Guard against zero km / zero expected
    km = max(km, 1e-9)
    expected = max(expected, 1e-9)

    metrics = {
        "harsh_braking_per_1k": float(row["harsh_braking"]) / km * 1000.0,
        "harsh_accel_per_1k":   float(row["harsh_accel"])   / km * 1000.0,
        "overspeed_per_1k":     float(row["overspeed_events"]) / km * 1000.0,
        "idling_pct":           float(row["idling_pct"]),
        "fuel_variance_pct":    abs((fuel - expected) / expected * 100.0),
        "incidents_per_1k":     float(row["incidents"]) / km * 1000.0,
    }

    composite = 0.0
    worst = []
    for k, w in WEIGHTS.items():
        good, bad = BENCHMARKS[k]
        ss = sub_score(metrics[k], good, bad)
        composite += w * ss
        worst.append((k, metrics[k], ss, w))
    composite /= sum(WEIGHTS.values())

    # Two worst KPIs by weighted loss (weight * (100 - sub_score))
    worst.sort(key=lambda x: x[3] * (100.0 - x[2]), reverse=True)
    worst_two = ", ".join(f"{k}={v:.2f} (ss={ss:.0f})" for k, v, ss, w in worst[:2])

    return {
        "driver_id": row["driver_id"],
        "route_id": row["route_id"],
        "km": km,
        "fuel_litres": fuel,
        "expected_litres": expected,
        "fuel_variance_pct": metrics["fuel_variance_pct"],
        "composite": composite,
        "worst_two": worst_two,
    }

def main(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("No rows in input file.")
        sys.exit(1)

    scored = [compute_row(r) for r in rows]
    scored.sort(key=lambda r: r["composite"], reverse=True)

    n = len(scored)
    q = max(1, n // 4)  # bottom quartile size (at least 1)

    print(f"{'Rank':<5}{'Driver':<12}{'Route':<12}{'Score':<8}{'FuelVar%':<10}{'Flag':<8}Worst two KPIs")
    print("-" * 120)
    for i, r in enumerate(scored, 1):
        flag = "COACH" if i > n - q else ""
        print(f"{i:<5}{r['driver_id']:<12}{r['route_id']:<12}"
              f"{r['composite']:<8.1f}{r['fuel_variance_pct']:<10.2f}{flag:<8}{r['worst_two']}")

    print("-" * 120)
    print(f"Drivers: {n}  |  Fleet median score: {sorted(r['composite'] for r in scored)[n//2]:.1f}  |  Bottom quartile size: {q}")
    print("NOTE: bottom quartile = coaching list, not punishment list. Manager applies judgement.")
    print("A new driver, a route change, or a return from leave is not a chronic pattern.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "driver_scorecard_input.csv")
