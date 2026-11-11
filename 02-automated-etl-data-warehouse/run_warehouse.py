import argparse
from src.warehouse import build
p=argparse.ArgumentParser(); p.add_argument("--data-dir",default="../datasets"); p.add_argument("--db-path",default="warehouse.duckdb")
a=p.parse_args(); print(build(a.data_dir,a.db_path))
