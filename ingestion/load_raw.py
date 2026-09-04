from __future__ import annotations

from pathlib import Path

import duckdb

DATA_DIR = Path("data")
WAREHOUSE = Path("warehouse/nyc_taxi.duckdb")


def main() -> None:
    trip_files = sorted(DATA_DIR.glob("yellow_tripdata_*.parquet"))
    zone_file = DATA_DIR / "taxi_zone_lookup.csv"

    if not trip_files:
        raise FileNotFoundError("No yellow_tripdata_*.parquet files found. Run ingestion/download_data.py first.")
    if not zone_file.exists():
        raise FileNotFoundError("taxi_zone_lookup.csv not found. Run ingestion/download_data.py first.")

    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    con.execute("create schema if not exists raw")

    parquet_list = ", ".join(f"'{p.as_posix()}'" for p in trip_files)
    con.execute(
        f"""
        create or replace table raw.yellow_tripdata as
        select *
        from read_parquet([{parquet_list}], union_by_name=true)
        """
    )

    con.execute(
        f"""
        create or replace table raw.taxi_zones as
        select *
        from read_csv_auto('{zone_file.as_posix()}', header=true)
        """
    )

    trip_count = con.execute("select count(*) from raw.yellow_tripdata").fetchone()[0]
    zone_count = con.execute("select count(*) from raw.taxi_zones").fetchone()[0]
    print(f"Loaded {trip_count:,} trips and {zone_count:,} taxi zones into {WAREHOUSE}")
    con.close()


if __name__ == "__main__":
    main()
