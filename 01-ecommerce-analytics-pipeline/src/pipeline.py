from pathlib import Path
import shutil, duckdb, pandas as pd

FILES=["orders","customers","products","payments"]
def load_sources(folder):
    data={}
    for name in FILES:
        path=Path(folder)/f"{name}.csv"
        if not path.exists(): raise FileNotFoundError(path)
        data[name]=pd.read_csv(path)
    return data

def transform(d):
    o=d["orders"].copy()
    o["order_date"]=pd.to_datetime(o.order_date,errors="coerce")
    for c in ["quantity","unit_price","discount_amount"]: o[c]=pd.to_numeric(o[c],errors="coerce")
    o=o.dropna(subset=["order_id","customer_id","product_id","order_date","quantity","unit_price"]).drop_duplicates("order_id")
    o=o[(o.quantity>0)&(o.unit_price>=0)]
    o["gross_sales"]=o.quantity*o.unit_price
    o["net_sales"]=(o.gross_sales-o.discount_amount.fillna(0).clip(lower=0)).clip(lower=0)
    o["month"]=o.order_date.dt.to_period("M").astype(str)
    paid=d["payments"].query("payment_status == 'paid'")[["order_id","payment_method"]].drop_duplicates("order_id")
    f=o[~o.order_status.isin(["cancelled","returned"])].merge(paid,on="order_id")
    f=f.merge(d["customers"][["customer_id","city"]],on="customer_id",how="left").merge(d["products"][["product_id","product_name","category"]],on="product_id",how="left")
    monthly=f.groupby("month",as_index=False).agg(orders=("order_id","nunique"),revenue=("net_sales","sum"),units=("quantity","sum"),customers=("customer_id","nunique"))
    monthly["aov"]=monthly.revenue/monthly.orders
    category=f.groupby(["month","category"],as_index=False).net_sales.sum()
    city=f.groupby("city",as_index=False).net_sales.sum().sort_values("net_sales",ascending=False)
    return {"fact_orders":f,"monthly_kpis":monthly,"category_revenue":category,"city_revenue":city}

def run(data_dir,output="data"):
    out=Path(output); (out/"raw").mkdir(parents=True,exist_ok=True); (out/"processed").mkdir(parents=True,exist_ok=True)
    for n in FILES: shutil.copy2(Path(data_dir)/f"{n}.csv",out/"raw"/f"{n}.csv")
    result=transform(load_sources(data_dir)); con=duckdb.connect(str(out/"analytics.duckdb"))
    try:
        for n,df in result.items():
            df.to_parquet(out/"processed"/f"{n}.parquet",index=False)
            con.register("incoming",df); con.execute(f"CREATE OR REPLACE TABLE {n} AS SELECT * FROM incoming"); con.unregister("incoming")
    finally: con.close()
    return result
