"""
fuel_variance_monitor.py
Module 3 artifact — Fleet Ops OS
Computes fuel variance % per vehicle per period, flags >2% for 2 consecutive periods.
Single-file, stdlib only (csv, collections). No pandas needed for this version.
"""

import csv
from collections import defaultdict

# --- Benchmark km/L per vehicle class (tune to your fleet baseline) ---
BENCHMARK_KMPL = {
    "pickup":   10.5,
    "3-5t":      6.0,
    "10-15t":    3.5,
    "prime":     2.3,
    "bus":       6.0,
}

# --- Thresholds ---
VARIANCE_THRESHOLD_PCT = 2.0   # flag if abs(variance) > 2%
CONSECUTIVE_PERIODS    = 2     # ...for 2 consecutive periods

# --- Input data: vehicle_id, period, vehicle_class, km, litres ---
# In real life this comes from telematics export + fuel card export.
# Here we embed a small sample so the script runs standalone.
ROWS = [
    # vehicle_id, period,  class,    km,   litres
    ("T123", "2026-W01", "3-5t",   620,   98.0),
    ("T123", "2026-W02", "3-5t",   610,  101.5),   # 2 weeks over -> FLAG
    ("T124", "2026-W01", "pickup", 480,   46.0),
    ("T124", "2026-W02", "pickup", 500,   47.5),   # normal
    ("T125", "2026-W01", "10-15t", 410,  118.0),
    ("T125", "2026-W02", "10-15t", 395,  121.0),   # 2 weeks over -> FLAG
    ("T125", "2026-W03", "10-15t", 405,  119.0),   # 3rd week over -> FLAG
    ("T126", "2026-W01", "prime",  880,  382.0),
    ("T126", "2026-W02", "prime",  910,  400.0),   # borderline, see output
]

def expected_litres(km, vehicle_class):
    kmpl = BENCHMARK_KMPL[vehicle_class]
    return km / kmpl

def variance_pct(actual_l, expected_l):
    if expected_l == 0:
        return 0.0
    return (actual_l - expected_l) / expected_l * 100.0

def build_records():
    """Return list of dicts with per-row variance."""
    recs = []
    for vid, period, vclass, km, litres in ROWS:
        exp = expected_litres(km, vclass)
        var = variance_pct(litres, exp)
        recs.append({
            "vehicle_id": vid,
            "period": period,
            "class": vclass,
            "km": km,
            "actual_l": litres,
            "expected_l": round(exp, 1),
            "variance_pct": round(var, 1),
        })
    return recs

def flag_consecutive(recs):
    """
    Flag a vehicle if it exceeds |threshold| in >= CONSECUTIVE_PERIODS
    consecutive periods. Periods are sorted as strings (ISO week format sorts correctly).
    """
    by_vehicle = defaultdict(list)
    for r in recs:
        by_vehicle[r["vehicle_id"]].append(r)

    flags = []
    for vid, rows in by_vehicle.items():
        rows.sort(key=lambda r: r["period"])
        streak = 0
        for r in rows:
            if abs(r["variance_pct"]) > VARIANCE_THRESHOLD_PCT:
                streak += 1
                if streak >= CONSECUTIVE_PERIODS:
                    flags.append(r)
            else:
                streak = 0
    return flags

def print_table(recs):
    print(f"{'Vehicle':<8} {'Period':<10} {'Class':<7} {'Km':>5} "
          f"{'Actual L':>9} {'Exp L':>7} {'Var %':>7}")
    print("-" * 62)
    for r in recs:
        marker = "  <-- FLAG" if r in FLAGS else ""
        print(f"{r['vehicle_id']:<8} {r['period']:<10} {r['class']:<7} "
              f"{r['km']:>5} {r['actual_l']:>9.1f} {r['expected_l']:>7.1f} "
              f"{r['variance_pct']:>7.1f}{marker}")

if __name__ == "__main__":
    records = build_records()
    FLAGS = flag_consecutive(records)
    print("\nFUEL VARIANCE MONITOR — weekly view")
    print(f"Threshold: |variance| > {VARIANCE_THRESHOLD_PCT}% for "
          f"{CONSECUTIVE_PERIODS}+ consecutive periods\n")
    print_table(records)
    print(f"\nFlagged rows: {len(FLAGS)}")
    if FLAGS:
        print("Action: investigate each flagged vehicle — siphoning, fault, "
              "driver behaviour, route, load, weather, or measurement error.")
