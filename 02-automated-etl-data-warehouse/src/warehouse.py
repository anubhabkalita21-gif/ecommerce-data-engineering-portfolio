from pathlib import Path
from datetime import datetime,timezone
import uuid, duckdb, pandas as pd

def build(data_dir,db_path):
    d=Path(data_dir); o=pd.read_csv(d/"orders.csv"); c=pd.read_csv(d/"customers.csv"); p=pd.read_csv(d/"products.csv")
    o["order_date"]=pd.to_datetime(o.order_date,errors="coerce")
    for x in ["quantity","unit_price","discount_amount"]: o[x]=pd.to_numeric(o[x],errors="coerce")
    o=o.dropna(subset=["order_date","quantity","unit_price"]).drop_duplicates("order_id")
    o=o[(o.quantity>0)&(o.unit_price>=0)]
    o["gross_sales"]=o.quantity*o.unit_price; o["discount_amount"]=o.discount_amount.fillna(0).clip(lower=0)
    o["net_sales"]=(o.gross_sales-o.discount_amount).clip(lower=0); o["date_key"]=o.order_date.dt.strftime("%Y%m%d").astype(int)
    dates=pd.DataFrame({"date":pd.date_range(o.order_date.min().date(),o.order_date.max().date())})
    dates["date_key"]=dates.date.dt.strftime("%Y%m%d").astype(int); dates["year"]=dates.date.dt.year; dates["month"]=dates.date.dt.month; dates["quarter"]=dates.date.dt.quarter
    fact=o.merge(c[["customer_id"]].drop_duplicates(),on="customer_id").merge(p[["product_id"]].drop_duplicates(),on="product_id")
    fact=fact[["order_id","customer_id","product_id","date_key","quantity","unit_price","gross_sales","discount_amount","net_sales","order_status"]]
    con=duckdb.connect(db_path); rid=str(uuid.uuid4()); started=datetime.now(timezone.utc).isoformat()
    try:
        con.execute("CREATE TABLE IF NOT EXISTS etl_run_log(run_id VARCHAR,started_at VARCHAR,status VARCHAR,rows_loaded BIGINT)")
        for n,df in [("dim_customer",c.drop_duplicates("customer_id")),("dim_product",p.drop_duplicates("product_id")),("dim_date",dates),("fact_sales",fact)]:
            con.register("incoming",df); con.execute(f"CREATE OR REPLACE TABLE {n} AS SELECT * FROM incoming"); con.unregister("incoming")
        con.execute("""CREATE OR REPLACE TABLE mart_monthly_sales AS SELECT d.year,d.month,COUNT(DISTINCT f.order_id) orders,
          SUM(f.quantity) units,SUM(f.net_sales) revenue,SUM(f.net_sales)/NULLIF(COUNT(DISTINCT f.order_id),0) aov
          FROM fact_sales f JOIN dim_date d USING(date_key) WHERE f.order_status NOT IN ('cancelled','returned') GROUP BY d.year,d.month""")
        con.execute("INSERT INTO etl_run_log VALUES (?,?,?,?)",[rid,started,"SUCCESS",len(fact)])
    finally: con.close()
    return {"run_id":rid,"rows_loaded":len(fact),"status":"SUCCESS"}
