# E-Commerce Analytics Pipeline

An end-to-end batch data engineering pipeline that ingests
e-commerce data, transforms raw records, generates Parquet
files, and loads analytical datasets into DuckDB.

## Architecture

```text
CSV Sources
    |
    v
Data Ingestion (Python + Pandas)
    |
    v
Raw Data Storage
    |
    v
Data Cleaning & Transformation
    |
    v
Parquet Files
    |
    v
DuckDB Analytics Database
    |
    v
SQL Business Analytics