from datetime import datetime
from pathlib import Path
from subprocess import run

from airflow import DAG
from airflow.operators.python import PythonOperator


def run_extractors() -> None:
    root = Path(__file__).resolve().parents[2]
    script = root / "extractors" / "generate_raw_sources.py"
    run(["python", str(script)], check=True)


def run_quality_checks() -> None:
    root = Path(__file__).resolve().parents[2]
    script = root / "data_quality" / "check_quality.py"
    run(["python", str(script)], check=True)


with DAG(
    dag_id="modern_elt_platform",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["elt", "dbt", "demo"],
) as dag:
    extract = PythonOperator(task_id="extract_sources", python_callable=run_extractors)
    validate = PythonOperator(task_id="validate_raw_data", python_callable=run_quality_checks)

    extract >> validate
