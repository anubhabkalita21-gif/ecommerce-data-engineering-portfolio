import json
from pathlib import Path
import pandas as pd

def check(df,r):
    t,n=r["type"],r["name"]; c=r.get("column")
    if t=="required_columns":
        missing=sorted(set(r["columns"])-set(df.columns)); failures=len(missing); detail=f"Missing columns: {missing}" if missing else "All columns present"
    elif c not in df.columns: failures=len(df); detail=f"Missing column: {c}"
    elif t=="not_null": failures=int(df[c].isna().sum()); detail=f"{failures} null values"
    elif t=="unique": failures=int(df[c].duplicated(keep=False).sum()); detail=f"{failures} duplicate rows"
    elif t=="accepted_values": failures=int((~df[c].isin(r["values"]) & df[c].notna()).sum()); detail=f"{failures} invalid values"
    elif t in ("greater_than","greater_equal"):
        s=pd.to_numeric(df[c],errors="coerce"); bad=s.isna() | (s<=r["value"] if t=="greater_than" else s<r["value"])
        failures=int(bad.sum()); detail=f"{failures} threshold violations"
    else: raise ValueError(f"Unknown rule type {t}")
    return {"rule":n,"passed":failures==0,"failed_records":failures,"detail":detail}

def validate(df,rules):
    results=[check(df,r) for r in rules]
    return {"row_count":len(df),"check_count":len(results),"passed_checks":sum(x["passed"] for x in results),
      "failed_checks":sum(not x["passed"] for x in results),"status":"PASS" if all(x["passed"] for x in results) else "FAIL","results":results}

def run(data_dir,config,report_dir):
    config=json.loads(Path(config).read_text()); out={"datasets":{}}; report=Path(report_dir); report.mkdir(parents=True,exist_ok=True)
    for name,rules in config.items():
        f=Path(data_dir)/f"{name}.csv"
        out["datasets"][name]=validate(pd.read_csv(f),rules) if f.exists() else {"row_count":0,"check_count":1,"passed_checks":0,"failed_checks":1,"status":"FAIL","results":[{"rule":"file_exists","passed":False,"failed_records":1,"detail":str(f)}]}
    out["overall_status"]="PASS" if all(x["status"]=="PASS" for x in out["datasets"].values()) else "FAIL"
    (report/"quality_report.json").write_text(json.dumps(out,indent=2)); return out
