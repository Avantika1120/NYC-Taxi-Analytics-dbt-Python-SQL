# NYC Taxi Analytics Engineering

**Python · SQL · dbt · DuckDB · Streamlit · Data Quality · Analytics Engineering**

An end-to-end analytics engineering project that turns raw NYC Yellow Taxi trip data into a tested analytical warehouse and an interactive business dashboard.

## 🚀 View the Dashboard

### [Open the standalone HTML dashboard](https://htmlpreview.github.io/?https://github.com/Avantika1120/NYC-Taxi-Analytics-dbt-Python-SQL/blob/main/dashboard/index.html)

The standalone HTML dashboard is designed for quick portfolio/recruiter review and includes KPI cards, revenue trends, zone performance, demand-by-hour analysis, airport-vs-non-airport economics, key business insights, and a visual architecture/dbt-lineage section.

> The HTML page uses representative portfolio values so it can be opened instantly in a browser. The Python + dbt pipeline in this repository computes the real warehouse-backed metrics, and the Streamlit application reads from those modeled tables for live analysis.

## What this project demonstrates

- Automated public-data ingestion with **Python**
- Local analytical warehouse design with **DuckDB**
- Modular transformations with **dbt**
- Staging, intermediate, fact, dimension, and mart layers
- Incremental modeling and reusable SQL macros
- Data quality tests and source freshness assumptions
- Business analysis with SQL
- Interactive **Streamlit + Plotly** dashboard
- Standalone **HTML portfolio dashboard**
- GitHub Actions CI for reproducible dbt builds
- Architecture, lineage, and business case-study documentation

## Business questions

This project is designed to answer questions such as:

- Which pickup zones generate the most trips and revenue?
- When does taxi demand peak by hour and weekday?
- How do airport trips differ from regular trips?
- Which zones have the strongest revenue per mile and tip behavior?
- How are trip volume, fare revenue, and average ticket changing over time?
- Where do unusually long, expensive, or low-efficiency trips occur?

## Architecture

```text
NYC TLC public Parquet + zone lookup
              |
              v
      Python ingestion scripts
              |
              v
      DuckDB RAW schema
              |
              v
     dbt staging models
              |
              v
   dbt intermediate models
              |
              v
  Fact + dimension + marts
              |
       +------+------+
       |             |
       v             v
 SQL analysis   Streamlit dashboard
```

## Repository structure

```text
ingestion/
  download_data.py
  load_raw.py

dbt_taxi/
  dbt_project.yml
  profiles.yml.example
  macros/
  models/
    staging/
    intermediate/
    marts/
  tests/

analysis/
  business_analysis.sql
  eda.py

dashboard/
  app.py
  index.html

docs/
  ARCHITECTURE.md
  PROJECT_CASE_STUDY.md
  LINEAGE.md

.github/workflows/
  ci.yml

requirements.txt
Makefile
.gitignore
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

make download
make load
make dbt-build
make dashboard
```

The default configuration downloads **January 2024 Yellow Taxi data** plus the official taxi-zone lookup. You can change the month/year in `ingestion/download_data.py` or pass CLI arguments.

## dbt model layers

### Staging
- `stg_yellow_trips` — renamed, typed, filtered trip records
- `stg_taxi_zones` — cleaned zone metadata

### Intermediate
- `int_trips_enriched` — trip duration, speed, revenue, daypart, airport flags, data-quality logic

### Marts
- `dim_zones` — taxi-zone dimension
- `fct_trips` — incremental trip-level fact table
- `mart_daily_kpis` — daily executive metrics
- `mart_zone_performance` — zone demand/revenue/efficiency metrics
- `mart_hourly_demand` — weekday/hour demand profile

## Dashboard

### Standalone HTML portfolio dashboard

[Open HTML dashboard](https://htmlpreview.github.io/?https://github.com/Avantika1120/NYC-Taxi-Analytics-dbt-Python-SQL/blob/main/dashboard/index.html)

### Warehouse-backed Streamlit dashboard

Run:

```bash
streamlit run dashboard/app.py
```

The dashboard includes:

- KPI cards: trips, revenue, average fare, average tip rate
- Daily revenue and trip trends
- Top pickup zones by revenue
- Demand heatmap by weekday/hour
- Airport vs non-airport comparison
- Zone-level efficiency table

## Data quality

Built-in tests validate:

- non-null primary business fields
- unique trip IDs in the fact table
- accepted payment types
- positive distance and duration logic
- zone relationships
- non-negative mart metrics

Run all tests with:

```bash
cd dbt_taxi
dbt build --profiles-dir .
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Project case study](docs/PROJECT_CASE_STUDY.md)
- [Data lineage](docs/LINEAGE.md)

Generate dbt docs locally:

```bash
cd dbt_taxi
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Tech stack

**Python:** pandas, requests, DuckDB  
**SQL / Analytics Engineering:** dbt-core, dbt-duckdb  
**Dashboard:** Streamlit, Plotly, HTML/CSS/JavaScript, Chart.js  
**DevOps:** GitHub Actions

## Why DuckDB?

DuckDB keeps the project fully reproducible without requiring a cloud warehouse account. The dbt structure is intentionally warehouse-agnostic, so the same modeling pattern can be migrated to Snowflake, BigQuery, or Redshift.

## Data source

NYC Taxi & Limousine Commission (TLC) public trip-record data and taxi-zone lookup files.

---

### Portfolio takeaway

This project shows the complete analytics-engineering lifecycle: **ingest raw data → model it with dbt → test data quality → create decision-ready marts → analyze with SQL/Python → expose insights through a dashboard**.
