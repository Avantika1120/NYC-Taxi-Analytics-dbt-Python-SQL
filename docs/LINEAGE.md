# Data Lineage

The project uses dbt references so dependencies are explicit and visible in dbt docs.

```text
source: raw.yellow_tripdata
        |
        v
stg_yellow_trips -----------┐
                            |
source: raw.taxi_zones      |
        |                   |
        v                   |
stg_taxi_zones -------------+
        |                   |
        +---------> int_trips_enriched
                          |
                          v
                     fct_trips
                    /    |    \
                   /     |     \
                  v      v      v
       mart_daily_kpis   |   mart_hourly_demand
                         |
                         v
               mart_zone_performance

stg_taxi_zones -> dim_zones
                     ^
                     |
         relationship tests from fct_trips
```

## Dependency explanation

### Raw sources

`raw.yellow_tripdata`
: Trip records loaded directly from downloaded Parquet files.

`raw.taxi_zones`
: Zone lookup loaded from the official CSV.

### Staging

`stg_yellow_trips`
: Source-level cleaning, typing, filtering, and trip-key generation.

`stg_taxi_zones`
: Standardized zone dimension source.

### Intermediate

`int_trips_enriched`
: Joins trip records to pickup/dropoff zone labels and centralizes derived fields used across the warehouse.

### Core marts

`fct_trips`
: Trip grain. Incremental fact table.

`dim_zones`
: Location grain. One row per taxi location ID.

### Aggregate marts

`mart_daily_kpis`
: One row per pickup date.

`mart_zone_performance`
: One row per pickup zone.

`mart_hourly_demand`
: One row per weekday/hour pair.

## Generating interactive lineage

After the warehouse has been built:

```bash
cd dbt_taxi
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

Open the generated dbt documentation site and select a model to see its upstream and downstream lineage graph.

## Why lineage matters

If a source field changes or a metric looks incorrect, lineage answers two questions quickly:

1. **Where did this field come from?**
2. **Which downstream assets could be affected?**

That traceability is one of the main reasons transformations live in dbt rather than inside a dashboard or notebook.
