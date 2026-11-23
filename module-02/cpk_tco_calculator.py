"""
CPK / TCO Calculator — Fleet Ops OS, Module 2
Single-file, no dependencies. Run: python3 cpk_tco_calculator.py
"""

def cost_per_km(fuel, maintenance, tyres, driver, insurance,
                depreciation, overheads, tolls_permits, km):
    total = (fuel + maintenance + tyres + driver + insurance +
             depreciation + overheads + tolls_permits)
    if km <= 0:
        raise ValueError("km must be > 0")
    return total, total / km


def annual_tco(fixed_costs, variable_costs, downtime_cost):
    return fixed_costs + variable_costs + downtime_cost


def repair_vs_replace(annual_repair_cost, current_market_value,
                      utilisation_pct, threshold_pct=45.0):
    repair_ratio = (annual_repair_cost / current_market_value) * 100 if current_market_value else 0
    if repair_ratio > threshold_pct and utilisation_pct < 60:
        return f"REPLACE (repair={repair_ratio:.1f}% of value, utilisation={utilisation_pct}%)"
    if repair_ratio > threshold_pct:
        return f"WATCH (repair={repair_ratio:.1f}% of value)"
    return f"KEEP (repair={repair_ratio:.1f}% of value)"


def main():
    fuel = 18_000_000
    maintenance = 6_500_000
    tyres = 2_200_000
    driver = 9_600_000
    insurance = 2_400_000
    depreciation = 7_500_000
    overheads = 1_800_000
    tolls_permits = 900_000
    km = 120_000

    fixed_costs = insurance + depreciation + overheads + tolls_permits
    variable_costs = fuel + maintenance + tyres + driver
    downtime_days = 6
    revenue_per_day = 450_000
    downtime_cost = downtime_days * revenue_per_day

    annual_repair_cost = maintenance
    current_market_value = 85_000_000
    utilisation_pct = 72

    total, cpk = cost_per_km(fuel, maintenance, tyres, driver, insurance,
                             depreciation, overheads, tolls_permits, km)
    tco = annual_tco(fixed_costs, variable_costs, downtime_cost)
    flag = repair_vs_replace(annual_repair_cost, current_market_value, utilisation_pct)

    print("=" * 55)
    print("CPK / TCO REPORT — single vehicle")
    print("=" * 55)
    print(f"Total cost (period)         : TZS {total:,.0f}")
    print(f"Kilometres                  : {km:,} km")
    print(f"Cost per km                 : TZS {cpk:,.0f} / km")
    print(f"Fixed costs                 : TZS {fixed_costs:,.0f}")
    print(f"Variable costs              : TZS {variable_costs:,.0f}")
    print(f"Downtime cost               : TZS {downtime_cost:,.0f}")
    print(f"Annual TCO                  : TZS {tco:,.0f}")
    print(f"Repair-vs-replace           : {flag}")
    print("=" * 55)


if __name__ == "__main__":
    main()
