# Architecture

## Objective

Build a reproducible analytics-engineering workflow that starts with public transportation data and ends with trusted, decision-ready metrics in an interactive dashboard.

The design deliberately separates **ingestion**, **storage**, **transformation**, **quality**, **analysis**, and **presentation** so each layer has one responsibility.

## End-to-end flow

```text
┌──────────────────────────────┐
│ NYC TLC Public Data          │
│ Yellow Taxi Parquet + Zones  │
└──────────────┬───────────────┘
               │ HTTPS
               v
┌──────────────────────────────┐
│ Python ingestion             │
│ download_data.py             │
│ load_raw.py                  │
└──────────────┬───────────────┘
               │
               v
┌──────────────────────────────┐
│ DuckDB                       │
│ raw.yellow_tripdata          │
│ raw.taxi_zones               │
└──────────────┬───────────────┘
               │ source()
               v
┌──────────────────────────────┐
│ dbt staging                  │
│ stg_yellow_trips             │
│ stg_taxi_zones               │
└──────────────┬───────────────┘
               │ ref()
               v
┌──────────────────────────────┐
│ dbt intermediate             │
│ int_trips_enriched           │
└──────────────┬───────────────┘
               │
               v
┌───────────────────────────────────────────┐
│ dbt marts                                 │
│ dim_zones                                 │
│ fct_trips (incremental)                   │
│ mart_daily_kpis                           │
│ mart_zone_performance                     │
│ mart_hourly_demand                        │
└──────────────┬────────────────────────────┘
               │
        ┌──────┴─────────┐
        v                v
┌───────────────┐  ┌──────────────────┐
│ SQL / Python  │  │ Streamlit        │
│ analysis      │  │ dashboard        │
└───────────────┘  └──────────────────┘
```

## Layer 1 — Public source data

The project uses NYC Taxi & Limousine Commission trip-record data. The ingestion script downloads a monthly Yellow Taxi Parquet file plus the taxi-zone lookup.

Why Parquet:
- columnar format
- smaller than CSV for large trip datasets
- efficient analytical scans
- native DuckDB support

## Layer 2 — Python ingestion

`ingestion/download_data.py`
- builds the monthly public URL from year/month arguments
- streams downloads to disk
- skips already-downloaded files
- keeps raw source files unchanged

`ingestion/load_raw.py`
- discovers all local monthly Parquet files
- creates the DuckDB warehouse if needed
- creates the `raw` schema
- loads trips with `union_by_name=true` so multiple months can be combined
- loads the taxi-zone CSV into a dimension source

The Python layer does **transport and loading**, not business transformation. Business logic stays in dbt.

## Layer 3 — DuckDB warehouse

The local warehouse lives at:

`warehouse/nyc_taxi.duckdb`

Schemas:
- `raw` — source-shaped data
- `staging` — cleaned dbt views
- `intermediate` — enriched reusable logic
- `marts` — analytics-ready tables

DuckDB makes the repository easy to reproduce locally while preserving warehouse-style modeling patterns.

## Layer 4 — dbt staging

### `stg_yellow_trips`
Responsibilities:
- standardize column names
- enforce types
- generate a deterministic trip key
- remove impossible timestamp ordering
- remove negative distance / total amount records
- preserve financial components separately

### `stg_taxi_zones`
Responsibilities:
- normalize zone metadata
- establish a unique `location_id`
- provide borough and service-zone labels

## Layer 5 — dbt intermediate

### `int_trips_enriched`
Adds reusable business features:
- pickup and dropoff zone names
- trip duration
- average speed
- tip rate
- revenue per mile
- pickup hour / weekday / month
- daypart
- airport-trip flag
- quality flag for zero-distance, unusually long, or unusually high-value records

This prevents downstream marts from duplicating complex calculations.

## Layer 6 — dbt marts

### `fct_trips`
The central trip-level fact table. It is incremental so new monthly data can be appended without rebuilding all historical records.

### `dim_zones`
Reusable taxi-zone dimension.

### `mart_daily_kpis`
Executive daily performance:
- trips
- revenue
- average ticket
- average distance
- average duration
- tip rate
- airport share
- card-payment share

### `mart_zone_performance`
Pickup-zone demand and economics:
- trip volume
- revenue
- average trip value
- revenue per mile
- tip rate
- airport share

### `mart_hourly_demand`
Weekday/hour demand profile for operational scheduling analysis.

## Data quality strategy

Quality is checked at several points:

1. **Staging filters** remove logically invalid records.
2. **dbt generic tests** validate uniqueness, non-null fields, accepted values, and relationships.
3. **Custom singular tests** ensure mart metrics cannot become negative.
4. **CI fixture data** lets the full transformation graph run on every push without downloading a large external dataset.
5. **Python analytical checks** provide a second validation surface outside dbt.

## CI/CD design

GitHub Actions performs:

```text
checkout
  -> install dependencies
  -> generate small deterministic input fixture
  -> load raw DuckDB tables
  -> dbt debug
  -> dbt build (models + tests)
  -> dbt docs generate
  -> Python analytical validation
```

The CI pipeline deliberately uses deterministic local fixture data. Production-scale public data is used by the normal local workflow, while CI stays fast and reproducible.

## Presentation layer

The Streamlit application reads from `marts.fct_trips`, never directly from raw data. This enforces the same semantic layer for both ad-hoc analysis and visual reporting.

The dashboard supports:
- date filtering
- borough filtering
- KPI summaries
- revenue and demand trends
- top-zone ranking
- airport economics
- weekday/hour demand heatmap
- zone efficiency review

## How this would scale in production

The architecture can migrate with minimal conceptual changes:

```text
NYC TLC / S3
  -> Python/Airflow ingestion
  -> Snowflake/BigQuery/Redshift
  -> dbt Cloud/Core
  -> scheduled tests + observability
  -> BI layer (Tableau/Power BI/Looker)
```

DuckDB is used here for reproducibility, not because the modeling design depends on a local database.
