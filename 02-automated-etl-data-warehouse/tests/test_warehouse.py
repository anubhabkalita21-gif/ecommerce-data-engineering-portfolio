import pandas as pd
import duckdb

from src.warehouse import build


def create_test_data(data):
    data.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([{
        "order_id": "O1",
        "customer_id": "C1",
        "product_id": "P1",
        "order_date": "2025-01-02",
        "quantity": 2,
        "unit_price": 10,
        "discount_amount": 1,
        "order_status": "delivered"
    }]).to_csv(data / "orders.csv", index=False)

    pd.DataFrame([
        {"customer_id": "C1", "city": "Guwahati"}
    ]).to_csv(data / "customers.csv", index=False)

    pd.DataFrame([
        {
            "product_id": "P1",
            "product_name": "Widget",
            "category": "Home"
        }
    ]).to_csv(data / "products.csv", index=False)


def test_warehouse_builds_successfully(tmp_path):

    data = tmp_path / "input"
    create_test_data(data)

    db = str(tmp_path / "warehouse.duckdb")

    result = build(str(data), db)

    assert result["status"] == "SUCCESS"
    assert result["rows_loaded"] == 1

    con = duckdb.connect(db, read_only=True)

    assert con.execute(
        "SELECT COUNT(*) FROM fact_sales"
    ).fetchone()[0] == 1

    assert con.execute(
        "SELECT net_sales FROM fact_sales"
    ).fetchone()[0] == 19

    con.close()


def test_incremental_load_and_duplicate_prevention(tmp_path):

    data = tmp_path / "input"
    create_test_data(data)

    db = str(tmp_path / "warehouse.duckdb")

    # Initial full load
    initial = build(str(data), db)

    assert initial["rows_loaded"] == 1
    assert initial["status"] == "SUCCESS"

    # Add one new order to the source CSV
    new_order = pd.DataFrame([{
        "order_id": "O2",
        "customer_id": "C1",
        "product_id": "P1",
        "order_date": "2025-01-03",
        "quantity": 3,
        "unit_price": 10,
        "discount_amount": 2,
        "order_status": "delivered"
    }])

    new_order.to_csv(
        data / "orders.csv",
        mode="a",
        header=False,
        index=False
    )

    # Incremental load
    incremental = build(
        str(data),
        db,
        incremental=True
    )

    assert incremental["rows_loaded"] == 1
    assert incremental["mode"] == "incremental"

    con = duckdb.connect(db, read_only=True)

    assert con.execute(
        "SELECT COUNT(*) FROM fact_sales"
    ).fetchone()[0] == 2

    assert con.execute(
        "SELECT COUNT(DISTINCT order_id) FROM fact_sales"
    ).fetchone()[0] == 2

    assert con.execute(
        "SELECT net_sales FROM fact_sales WHERE order_id = 'O2'"
    ).fetchone()[0] == 28

    con.close()

    # Repeat incremental load to verify duplicate prevention
    repeated = build(
        str(data),
        db,
        incremental=True
    )

    assert repeated["rows_loaded"] == 0

    con = duckdb.connect(db, read_only=True)

    assert con.execute(
        "SELECT COUNT(*) FROM fact_sales"
    ).fetchone()[0] == 2

    con.close()