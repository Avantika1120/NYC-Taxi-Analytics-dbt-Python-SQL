PYTHON=python
DBT_DIR=dbt_taxi

.PHONY: download load dbt-debug dbt-build dbt-docs dashboard eda clean

download:
	$(PYTHON) ingestion/download_data.py --year 2024 --month 1

load:
	$(PYTHON) ingestion/load_raw.py

dbt-debug:
	cd $(DBT_DIR) && dbt debug --profiles-dir .

dbt-build:
	cd $(DBT_DIR) && dbt build --profiles-dir .

dbt-docs:
	cd $(DBT_DIR) && dbt docs generate --profiles-dir .

eda:
	$(PYTHON) analysis/eda.py

dashboard:
	streamlit run dashboard/app.py

clean:
	rm -rf dbt_taxi/target dbt_taxi/logs warehouse/*.duckdb data/*.parquet data/*.csv
