# Automated ETL Data Warehouse

An end-to-end data engineering project that transforms raw e-commerce data into a structured dimensional data warehouse using Python, Pandas, SQL and DuckDB.

## Architecture
### Dimensional Warehouse Schema

```text
             DIM_CUSTOMER
             ------------
             customer_id (PK)
             email
             city
                  |
                  | 1 : Many
                  |
DIM_PRODUCT ------ FACT_SALES ------ DIM_DATE
-----------       ----------        --------
product_id (PK)   order_id (PK)     date_key (PK)
product_name      customer_id (FK)  date
category          product_id (FK)   year
unit_price        date_key (FK)     month
                  quantity          quarter
                  unit_price
                  gross_sales
                  discount_amount
                  net_sales
                  order_status
                       |
                       v
              MART_MONTHLY_SALES
              ------------------
              year
              month
              orders
              units
              revenue
              aov

              ETL_RUN_LOG
              -----------
              run_id
              started_at
              status
              rows_loaded
```## Incremental ETL Processing

The warehouse supports full-refresh and incremental loading.

### Full Refresh

```powershell
python run_warehouse.py --data-dir ..\datasets --db-path warehouse.duckdb
```

### Incremental Loading

```powershell
python run_warehouse.py --data-dir ..\datasets --db-path warehouse.duckdb --incremental
```

Features:
- Loads only previously unseen orders.
- Prevents duplicate order IDs.
- Preserves historical fact records.
- Updates dimension tables.
- Rebuilds monthly sales analytics.
- Logs every successful execution.

Note: Incremental loading is append-only. Updates to existing orders are not detected.

## Automated Testing

Tests cover:
- Warehouse creation.
- Net sales calculations.
- Incremental order loading.
- Duplicate prevention.