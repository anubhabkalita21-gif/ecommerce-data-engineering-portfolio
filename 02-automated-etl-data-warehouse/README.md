# 02 — Automated ETL Data Warehouse
Builds a dimensional warehouse: `dim_customer`, `dim_product`, `dim_date`, `fact_sales`, and `mart_monthly_sales`. Each run writes an operational record to `etl_run_log`.

Run:
```bash
pip install -r requirements.txt
python run_warehouse.py --data-dir ../datasets --db-path warehouse.duckdb
```
DuckDB is used for a zero-infrastructure local demo. Production extensions: PostgreSQL/Redshift adapter, incremental watermarks, SCD Type 2, retries and alerting.
