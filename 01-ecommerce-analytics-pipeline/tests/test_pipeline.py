import pandas as pd
from src.pipeline import transform
def test_pipeline_calculates_net_sales():
 d={"orders":pd.DataFrame([{"order_id":"O1","customer_id":"C1","product_id":"P1","order_date":"2025-01-01","quantity":2,"unit_price":10,"discount_amount":2,"order_status":"delivered"}]),
 "payments":pd.DataFrame([{"order_id":"O1","payment_status":"paid","payment_method":"UPI"}]),
 "customers":pd.DataFrame([{"customer_id":"C1","city":"Guwahati"}]),
 "products":pd.DataFrame([{"product_id":"P1","product_name":"Thing","category":"Home"}])}
 assert transform(d)["fact_orders"].iloc[0].net_sales==18
