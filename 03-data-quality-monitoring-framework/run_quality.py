import argparse
from src.quality import run
p=argparse.ArgumentParser(); p.add_argument("--data-dir",default="../datasets"); p.add_argument("--config",default="config/rules.json"); p.add_argument("--report-dir",default="reports")
a=p.parse_args(); r=run(a.data_dir,a.config,a.report_dir)
for n,x in r["datasets"].items(): print(n,x["status"],f'{x["passed_checks"]}/{x["check_count"]} checks')
print("Overall:",r["overall_status"]); raise SystemExit(0 if r["overall_status"]=="PASS" else 1)
