# Project Case Study — NYC Taxi Analytics Engineering

## Executive summary

This project was built to demonstrate how raw operational data can be converted into a reliable analytics product using **Python, SQL, dbt, DuckDB, and Streamlit**.

The source data is intentionally realistic: NYC Yellow Taxi trip records contain millions of rows, operational timestamps, location IDs, fare components, payment types, distance, tips, and surcharge fields. Instead of analyzing the raw file directly in a notebook, the project treats the data as an analytics-engineering problem.

The result is a reproducible pipeline that:

1. downloads public source data,
2. loads a raw warehouse,
3. standardizes and cleans source records,
4. creates reusable business features,
5. builds tested facts, dimensions, and analytical marts,
6. answers business questions in SQL/Python, and
7. exposes the trusted mart layer through an interactive dashboard.

---

## 1. Business problem

A transportation operator has detailed transaction-level ride data, but raw trip records are not immediately useful for decision-making. Analysts and operations teams need consistent answers to questions such as:

- Where is demand concentrated?
- Which zones drive the most revenue?
- What hours require the most operational capacity?
- How different are airport trips from standard rides?
- Which areas have strong or weak revenue efficiency?
- How do tipping and payment behavior vary?
- Are trends changing over time?

Answering these questions directly from raw files creates repeated SQL logic, inconsistent metric definitions, and weak data-quality controls.

### Project goal

Create a **trusted analytics layer** that standardizes the underlying trip data once and makes consistent metrics reusable across analysis and reporting.

---

## 2. Source data

### NYC Yellow Taxi trip records

The pipeline pulls monthly Parquet files from the NYC Taxi & Limousine Commission public data distribution endpoint.

Typical fields include:

- pickup and dropoff timestamps
- passenger count
- trip distance
- pickup / dropoff location IDs
- payment type
- fare amount
- tip amount
- tolls
- total amount
- congestion surcharge
- airport fee

### Taxi zone lookup

The zone file converts numerical location IDs into:

- borough
- zone
- service zone

This enables geographic performance analysis without embedding labels into trip records.

---

## 3. Data ingestion with Python

The ingestion layer has two jobs.

### Download

`ingestion/download_data.py`

The script accepts a year and month, constructs the source URL, streams the files to disk, and prevents unnecessary repeat downloads.

Example:

```bash
python ingestion/download_data.py --year 2024 --month 1
```

### Load

`ingestion/load_raw.py`

The loader:

- discovers downloaded monthly trip files,
- creates a DuckDB warehouse,
- loads all matching Parquet files into `raw.yellow_tripdata`,
- loads the zone lookup into `raw.taxi_zones`, and
- reports loaded row counts.

A key design decision is that Python does **not** define analytical business rules. It only handles acquisition and loading. Transformations remain visible and version-controlled in dbt SQL.

---

## 4. Transformation strategy with dbt

The warehouse is modeled in layers.

### Staging layer

The staging layer mirrors source concepts but improves reliability.

`stg_yellow_trips`
- standardizes column names
- casts source fields into explicit types
- generates a deterministic `trip_id`
- removes impossible timestamp ordering
- removes negative distance / revenue records

`stg_taxi_zones`
- standardizes zone metadata
- preserves `location_id` as the dimensional key

### Intermediate layer

`int_trips_enriched` centralizes derived business logic.

It calculates:

- trip duration in minutes
- average speed in miles per hour
- tip rate
- revenue per mile
- pickup hour
- weekday
- month
- daypart
- airport-trip indicator
- trip-quality classification

Centralizing these calculations avoids copying the same CASE statements into multiple reports.

### Mart layer

The final analytical layer contains reusable facts, dimensions, and aggregated marts.

**`fct_trips`**  
One row per modeled trip. The model is incremental so additional months can be processed efficiently.

**`dim_zones`**  
Reusable zone dimension.

**`mart_daily_kpis`**  
Daily metrics for executive trend reporting.

**`mart_zone_performance`**  
Zone-level demand, revenue, trip value, tip, and revenue-efficiency metrics.

**`mart_hourly_demand`**  
Weekday/hour metrics for identifying demand peaks.

---

## 5. Data quality

A warehouse is only useful when users can trust its outputs.

This project uses dbt tests for:

- primary-key uniqueness
- required values
- accepted payment codes
- fact-to-dimension relationships
- non-negative KPI logic

A deterministic CI fixture creates a tiny but representative taxi dataset. GitHub Actions then runs the **entire warehouse build and test graph** against that data on every push or pull request.

This is preferable to running CI against a large remote dataset because it keeps validation fast, repeatable, and independent of source availability.

---

## 6. Analytical questions

`analysis/business_analysis.sql` contains reusable SQL for questions including:

### Revenue concentration
Rank pickup zones by total revenue and calculate how much revenue is concentrated in the top locations.

### Demand peaks
Identify weekday/hour combinations with the highest trip volume.

### Airport economics
Compare airport and non-airport rides across:
- average ticket
- distance
- duration
- tip rate
- revenue

### Payment behavior
Compare trip economics and tipping by payment type.

### Daypart economics
Understand whether morning, midday, evening, or overnight rides differ in volume and revenue efficiency.

### Operational exceptions
Surface longer-distance trips moving at unusually low average speeds as potential congestion or operational-efficiency cases.

The repository does not hard-code business findings before the dataset is run. Results are produced directly from the chosen monthly source files, preserving metric integrity.

---

## 7. Dashboard

The Streamlit dashboard is the consumption layer of the project.

It connects only to dbt's `marts` schema and includes:

- date and borough filters
- total trip count
- total revenue
- average trip value
- average tip rate
- average distance
- daily revenue trend
- daily demand trend
- top pickup zones
- airport vs non-airport economics
- weekday × hour demand heatmap
- zone efficiency table

This makes the project useful both to a technical reviewer and to a stakeholder who wants to understand business performance visually.

---

## 8. Why dbt matters here

Without dbt, the project could still clean data using one Python notebook or one long SQL script. That approach would be faster initially but weaker as an analytics system.

dbt adds:

- explicit dependencies through `ref()`
- reusable source definitions
- modular transformations
- automatic lineage
- integrated tests
- documentation generation
- incremental materialization
- consistent environments

The project therefore demonstrates not only SQL ability, but the engineering practices required to maintain analytical data products.

---

## 9. Reproducibility

A reviewer can reproduce the workflow using:

```bash
pip install -r requirements.txt
make download
make load
make dbt-build
streamlit run dashboard/app.py
```

To inspect dbt documentation and lineage:

```bash
cd dbt_taxi
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

---

## 10. Production extension

The portfolio version uses DuckDB so anyone can run it without credentials or cloud costs.

A production version could replace the local components with:

- S3 or GCS for raw storage
- Airflow / Dagster for orchestration
- Snowflake / BigQuery / Redshift for the warehouse
- dbt Cloud for managed transformations
- Great Expectations / Elementary for additional observability
- Tableau / Power BI / Looker as the enterprise BI layer

The logical data model would remain largely unchanged.

---

## Skills demonstrated

**Analytics engineering:** dbt modeling, facts/dimensions, marts, incremental models, lineage  
**SQL:** transformations, window functions, aggregation, business metrics  
**Python:** public API/file ingestion, DuckDB loading, analytical validation  
**Data quality:** schema tests, relationship tests, singular tests, CI fixtures  
**BI:** Streamlit, Plotly, interactive filtering, stakeholder-focused metrics  
**Engineering:** reproducibility, modular code, GitHub Actions, documentation

---

## Portfolio story

The strongest way to describe this project is:

> Built an end-to-end analytics engineering pipeline on NYC taxi trip data using Python, SQL, dbt, and DuckDB; modeled tested staging/intermediate/mart layers, implemented incremental fact processing and CI data-quality validation, and delivered an interactive Streamlit dashboard for demand, revenue, airport, and zone-performance analysis.
