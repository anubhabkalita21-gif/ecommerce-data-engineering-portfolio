# Automated ETL Data Warehouse

An end-to-end data engineering project that transforms raw e-commerce data into a structured dimensional data warehouse using Python, Pandas, SQL and DuckDB.

## Architecture

```text
CSV Source Data
      |
      v
Data Extraction
      |
      v
Data Transformation (Python + Pandas)
      |
      v
Dimensional Data Modeling
      |
      v
DuckDB Data Warehouse
      |
      v
SQL Analytics & Reporting
```

## Technology Stack

- Python 3.13
- Pandas
- DuckDB
- SQL
- Pytest
- Apache Airflow (optional orchestration)

## Source Datasets

| Dataset | Description |
|---|---|
| orders.csv | E-commerce transactions |
| customers.csv | Customer information |
| products.csv | Product catalogue |

## Warehouse Architecture

The warehouse uses dimensional modelling.

### Dimension Tables

- `dim_customer` — Customer information
- `dim_product` — Product information
- `dim_date` — Calendar attributes

### Fact Table

- `fact_sales` — Order-level sales transactions and measures

### Analytics Mart

- `mart_monthly_sales` — Monthly revenue, order counts, units sold and average order value

### ETL Monitoring

- `etl_run_log` — Records successful pipeline executions

## Pipeline Features

- Automated CSV data ingestion
- Data type conversion
- Data cleaning
- Duplicate order removal
- Gross and net sales calculations
- Dimensional data modelling
- Fact and dimension table generation
- Monthly sales aggregation
- ETL execution logging
- SQL analytical queries

## Project Structure

```text
02-automated-etl-data-warehouse/
|
├── airflow/
│   └── dags/
│       └── warehouse_dag.py
|
├── sql/
│   └── warehouse_queries.sql
|
├── src/
│   ├── __init__.py
│   └── warehouse.py
|
├── tests/
│   └── test_warehouse.py
|
├── pytest.ini
├── requirements.txt
├── run_warehouse.py
└── README.md
```

## Installation

Run commands from the repository root.

### 1. Create virtual environment

```bash
python -m venv .venv
```

### 2. Activate environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r 02-automated-etl-data-warehouse/requirements.txt
```

## Run the Pipeline

```bash
python 02-automated-etl-data-warehouse/run_warehouse.py --data-dir datasets --db-path 02-automated-etl-data-warehouse/warehouse.duckdb
```

## SQL Analytics

Example monthly revenue analysis:

```sql
SELECT
    year,
    month,
    orders,
    units,
    ROUND(revenue, 2) AS revenue,
    ROUND(aov, 2) AS average_order_value
FROM mart_monthly_sales
ORDER BY year, month;
```

## Run Automated Tests

```bash
python -m pytest -v 02-automated-etl-data-warehouse
```

## Future Improvements

- Incremental ETL processing
- Slowly Changing Dimensions (SCD Type 2)
- Apache Airflow scheduling
- PostgreSQL or Amazon Redshift integration
- Automated failure alerts
- Cloud data warehouse deployment

## Dataset Information

This project uses synthetic e-commerce datasets for educational and portfolio purposes.