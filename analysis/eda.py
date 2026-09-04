from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

WAREHOUSE = Path("warehouse/nyc_taxi.duckdb")


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> None:
    if not WAREHOUSE.exists():
        raise FileNotFoundError("Warehouse not found. Run ingestion + dbt build first.")

    con = duckdb.connect(str(WAREHOUSE), read_only=True)

    print_section("Warehouse tables")
    tables = con.execute(
        """
        select table_schema, table_name
        from information_schema.tables
        where table_schema in ('raw', 'staging', 'intermediate', 'marts')
        order by 1, 2
        """
    ).df()
    print(tables.to_string(index=False))

    print_section("Daily KPI summary")
    daily = con.execute(
        """
        select
            min(pickup_date) as first_date,
            max(pickup_date) as last_date,
            sum(total_trips) as total_trips,
            round(sum(total_revenue), 2) as total_revenue,
            round(avg(avg_trip_value), 2) as mean_daily_avg_trip_value
        from marts.mart_daily_kpis
        """
    ).df()
    print(daily.to_string(index=False))

    print_section("Top 10 pickup zones by revenue")
    zones = con.execute(
        """
        select zone, borough, total_trips, total_revenue, avg_trip_value
        from marts.mart_zone_performance
        order by total_revenue desc
        limit 10
        """
    ).df()
    print(zones.to_string(index=False))

    print_section("Quality-flag distribution")
    quality = con.execute(
        """
        select trip_quality_flag, count(*) as trips
        from marts.fct_trips
        group by 1
        order by trips desc
        """
    ).df()
    print(quality.to_string(index=False))

    # Lightweight validation that can be reused in notebooks or CI investigations.
    assert pd.notna(daily.loc[0, "total_trips"])
    assert float(daily.loc[0, "total_revenue"]) >= 0

    con.close()


if __name__ == "__main__":
    main()
