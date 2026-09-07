from datetime import datetime, timedelta
from pathlib import Path
from subprocess import run

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def run_extractors() -> None:
    root = Path(__file__).resolve().parents[2]
    script = root / "extractors" / "generate_raw_sources.py"
    run(["python", str(script)], check=True)


def run_dbt() -> None:
    root = Path(__file__).resolve().parents[2]
    dbt_dir = root / "dbt"
    result = run(
        ["dbt", "run", "--profiles-dir", str(dbt_dir), "--project-dir", str(dbt_dir)],
        capture_output=True
    )
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr.decode()}")


def run_quality_checks() -> None:
    root = Path(__file__).resolve().parents[2]
    script = root / "data_quality" / "check_quality.py"
    run(["python", str(script)], check=True)


default_args = {
    'owner': 'data-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id="modern_elt_platform",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["elt", "dbt", "demo"],
    default_args=default_args,
) as dag:
    extract = PythonOperator(task_id="extract_sources", python_callable=run_extractors)
    transform = PythonOperator(task_id="run_dbt", python_callable=run_dbt)
    validate = PythonOperator(task_id="validate_raw_data", python_callable=run_quality_checks)

    extract >> transform >> validate
