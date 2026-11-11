# Optional: install Apache Airflow in a dedicated Airflow environment.
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
with DAG("ecommerce_warehouse",start_date=datetime(2025,1,1),schedule="@daily",catchup=False) as dag:
    build_warehouse=BashOperator(task_id="build_warehouse",bash_command="cd /opt/airflow/project && python run_warehouse.py --data-dir /opt/airflow/data --db-path /opt/airflow/warehouse.duckdb")
