from pathlib import Path
from datetime import datetime, timezone
import uuid

import duckdb
import pandas as pd


def _update_dimension(con, table, incoming, key, incremental, existing_tables):
    incoming = incoming.drop_duplicates(subset=[key], keep="last")

    if incremental and table in existing_tables:
        existing = con.execute(f"SELECT * FROM {table}").fetchdf()
        incoming = pd.concat(
            [existing, incoming],
            ignore_index=True
        ).drop_duplicates(subset=[key], keep="last")

    con.register("dimension_incoming", incoming)
    con.execute(
        f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM dimension_incoming"
    )
    con.unregister("dimension_incoming")


def build(data_dir, db_path, incremental=False):
    data = Path(data_dir)

    orders = pd.read_csv(data / "orders.csv")
    customers = pd.read_csv(data / "customers.csv")
    products = pd.read_csv(data / "products.csv")

    # Transform orders
    orders["order_date"] = pd.to_datetime(
        orders["order_date"], errors="coerce"
    )

    for column in ["quantity", "unit_price", "discount_amount"]:
        orders[column] = pd.to_numeric(
            orders[column], errors="coerce"
        )

    orders = orders.dropna(
        subset=[
            "order_id",
            "customer_id",
            "product_id",
            "order_date",
            "quantity",
            "unit_price"
        ]
    ).drop_duplicates("order_id")

    orders = orders[
        (orders["quantity"] > 0) &
        (orders["unit_price"] >= 0)
    ].copy()

    if orders.empty:
        raise ValueError("No valid orders found in the source dataset.")

    orders["discount_amount"] = (
        orders["discount_amount"].fillna(0).clip(lower=0)
    )

    orders["gross_sales"] = (
        orders["quantity"] * orders["unit_price"]
    )

    orders["net_sales"] = (
        orders["gross_sales"] - orders["discount_amount"]
    ).clip(lower=0)

    orders["date_key"] = (
        orders["order_date"].dt.strftime("%Y%m%d").astype(int)
    )

    # Build date dimension
    dates = pd.DataFrame({
        "date": pd.date_range(
            orders["order_date"].min().date(),
            orders["order_date"].max().date()
        )
    })

    dates["date_key"] = dates["date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["date"].dt.year
    dates["month"] = dates["date"].dt.month
    dates["quarter"] = dates["date"].dt.quarter

    # Build fact dataset
    fact = (
        orders
        .merge(
            customers[["customer_id"]].drop_duplicates(),
            on="customer_id"
        )
        .merge(
            products[["product_id"]].drop_duplicates(),
            on="product_id"
        )
    )

    fact = fact[
        [
            "order_id",
            "customer_id",
            "product_id",
            "date_key",
            "quantity",
            "unit_price",
            "gross_sales",
            "discount_amount",
            "net_sales",
            "order_status"
        ]
    ]

    # Connect to DuckDB
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))

    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    rows_loaded = 0

    try:
        con.execute("BEGIN TRANSACTION")

        con.execute("""
            CREATE TABLE IF NOT EXISTS etl_run_log (
                run_id VARCHAR,
                started_at VARCHAR,
                status VARCHAR,
                rows_loaded BIGINT
            )
        """)

        existing_tables = {
            row[0] for row in con.execute("SHOW TABLES").fetchall()
        }

        # Update dimensions while preserving historical dimension records
        _update_dimension(
            con, "dim_customer", customers,
            "customer_id", incremental, existing_tables
        )

        _update_dimension(
            con, "dim_product", products,
            "product_id", incremental, existing_tables
        )

        # Preserve historical dates in incremental mode
        if incremental and "dim_date" in existing_tables:
            old_dates = con.execute(
                "SELECT * FROM dim_date"
            ).fetchdf()

            dates = pd.concat(
                [old_dates, dates],
                ignore_index=True
            ).drop_duplicates("date_key", keep="last")

        con.register("date_incoming", dates)

        con.execute("""
            CREATE OR REPLACE TABLE dim_date
            AS SELECT * FROM date_incoming
        """)

        con.unregister("date_incoming")

        # Full refresh or incremental fact loading
        if incremental and "fact_sales" in existing_tables:
            existing_ids = con.execute(
                "SELECT order_id FROM fact_sales"
            ).fetchdf()["order_id"]

            new_fact = fact[
                ~fact["order_id"].isin(existing_ids)
            ].copy()

            con.register("fact_incoming", new_fact)

            con.execute("""
                INSERT INTO fact_sales
                SELECT * FROM fact_incoming
            """)

            con.unregister("fact_incoming")

        else:
            new_fact = fact.copy()

            con.register("fact_incoming", fact)

            con.execute("""
                CREATE OR REPLACE TABLE fact_sales
                AS SELECT * FROM fact_incoming
            """)

            con.unregister("fact_incoming")

        rows_loaded = len(new_fact)

        # Rebuild reporting mart using all historical fact records
        con.execute("""
            CREATE OR REPLACE TABLE mart_monthly_sales AS
            SELECT
                d.year,
                d.month,
                COUNT(DISTINCT f.order_id) AS orders,
                SUM(f.quantity) AS units,
                SUM(f.net_sales) AS revenue,
                SUM(f.net_sales) /
                    NULLIF(COUNT(DISTINCT f.order_id), 0) AS aov
            FROM fact_sales f
            JOIN dim_date d USING (date_key)
            WHERE LOWER(TRIM(COALESCE(f.order_status, '')))
                NOT IN ('cancelled', 'returned')
            GROUP BY d.year, d.month
        """)

        con.execute(
            "INSERT INTO etl_run_log VALUES (?, ?, ?, ?)",
            [run_id, started_at, "SUCCESS", rows_loaded]
        )

        con.execute("COMMIT")

    except Exception:
        con.execute("ROLLBACK")
        raise

    finally:
        con.close()

    return {
        "run_id": run_id,
        "rows_loaded": rows_loaded,
        "status": "SUCCESS",
        "mode": "incremental" if incremental else "full_refresh"
    }