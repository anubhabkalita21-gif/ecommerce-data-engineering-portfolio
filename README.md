# E-Commerce Data Engineering Portfolio

[![CI](https://github.com/anubhabkalita21-gif/ecommerce-data-engineering-portfolio/actions/workflows/tests.yml/badge.svg)](https://github.com/anubhabkalita21-gif/ecommerce-data-engineering-portfolio/actions)

A collection of three end-to-end data engineering projects demonstrating data ingestion, ETL development, dimensional modelling, data quality monitoring, SQL analytics and automated testing.

Built using Python, Pandas, SQL, DuckDB, Parquet and GitHub Actions.

---

## Projects

### 01. E-Commerce Analytics Pipeline

**Technologies:** Python · Pandas · Parquet · DuckDB

An end-to-end batch data pipeline that processes raw e-commerce CSV files into analytical datasets.

**Key Features**
- CSV data ingestion and immutable raw snapshots.
- Data cleaning and transformation using Pandas.
- Sales metrics and calculated business KPIs.
- Parquet data storage.
- DuckDB analytical tables.
- Monthly revenue, category revenue and city performance analysis.
- Automated pipeline testing.

[View Project 01](./01-ecommerce-analytics-pipeline/README.md)

---

### 02. Automated ETL Data Warehouse

**Technologies:** Python · Pandas · SQL · DuckDB · Pytest

A dimensional data warehouse that transforms e-commerce data into structured analytical tables.

**Key Features**
- Dimensional modelling with fact and dimension tables.
- Customer, product and date dimensions.
- Automated ETL execution logging.
- Full-refresh and incremental loading.
- Duplicate prevention using order IDs.
- Monthly sales reporting mart.
- SQL analytics and automated testing.

[View Project 02](./02-automated-etl-data-warehouse/README.md)

---

### 03. Data Quality Monitoring Framework

**Technologies:** Python · Pandas · JSON · HTML · Pytest

A configuration-driven framework for monitoring data reliability across multiple e-commerce datasets.

**Key Features**
- Configurable JSON validation rules.
- Required-column and null-value checks.
- Duplicate record detection.
- Accepted-value validation.
- Numeric threshold validation.
- Dataset-level quality metrics.
- JSON reports and HTML dashboard.
- CI-friendly execution status.

**Current validation results:** 24/24 checks passed across four synthetic datasets.

[View Project 03](./03-data-quality-monitoring-framework/README.md)

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Data Processing | Pandas |
| Database | DuckDB |
| Query Language | SQL |
| Storage | CSV, Parquet |
| Data Quality | Python, JSON |
| Testing | Pytest |
| Automation | GitHub Actions |
| Version Control | Git, GitHub |

---

## Repository Structure

```text
ecommerce-data-engineering-portfolio/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── 01-ecommerce-analytics-pipeline/
│
├── 02-automated-etl-data-warehouse/
│
├── 03-data-quality-monitoring-framework/
│
├── datasets/
│   ├── orders.csv
│   ├── customers.csv
│   ├── products.csv
│   └── payments.csv
│
├── .gitignore
└── README.md