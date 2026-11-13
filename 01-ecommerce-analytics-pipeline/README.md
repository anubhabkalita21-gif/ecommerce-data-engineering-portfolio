# E-Commerce Analytics Pipeline

An end-to-end batch data engineering pipeline that ingests
e-commerce data, transforms raw records, generates Parquet
files, and loads analytical datasets into DuckDB.

## Architecture
```mermaid
flowchart TD
    A["E-Commerce CSV Sources"] --> B["Data Ingestion<br/>Python + Pandas"]
    B --> C["Raw Data Storage"]
    C --> D["Data Cleaning & Transformation"]
    D --> E["Processed Parquet Files"]
    E --> F["DuckDB Analytical Database"]
    F --> G["SQL Analytics"]
    G --> H["Business Insights & Reporting"]

    style A fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    style F fill:#dcfce7,stroke:#16a34a,color:#14532d
    style H fill:#fef3c7,stroke:#d97706,color:#78350f
```