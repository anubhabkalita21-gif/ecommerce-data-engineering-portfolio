import argparse
from src.pipeline import run
p=argparse.ArgumentParser(); p.add_argument("--data-dir",default="../datasets"); p.add_argument("--output",default="data")
a=p.parse_args()
for name,df in run(a.data_dir,a.output).items(): print(f"{name}: {len(df)} rows")
