import pandas as pd
import duckdb
from src.warehouse import build


def test_warehouse_builds_successfully(tmp_path):

    data = tmp_path / "input"
    data.mkdir()

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
        {"product_id": "P1", "product_name": "Widget", "category": "Home"}
    ]).to_csv(data / "products.csv", index=False)

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