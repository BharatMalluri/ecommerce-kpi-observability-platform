"""
run_dbt.py
Airflow DAG: run dbt build (staging → intermediate → marts) after ingestion.
Triggered by: ingest_orders DAG (or run manually)
"""
from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
    "email_on_failure": False,
}

DBT_DIR = "/opt/airflow/dbt"
DBT_CMD = f"cd {DBT_DIR} && dbt"

with DAG(
    dag_id="run_dbt",
    default_args=default_args,
    description="Run dbt build: staging → intermediate → marts + tests",
    schedule_interval="0 3 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["dbt", "transformation", "marts"],
) as dag:

    wait_for_ingest = ExternalTaskSensor(
        task_id="wait_for_ingest",
        external_dag_id="ingest_orders",
        external_task_id="log_pipeline_run",
        timeout=3600,
        mode="reschedule",
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"{DBT_CMD} deps --profiles-dir {DBT_DIR}",
    )

    dbt_staging = BashOperator(
        task_id="dbt_staging",
        bash_command=f"{DBT_CMD} run --select staging --profiles-dir {DBT_DIR}",
    )

    dbt_intermediate = BashOperator(
        task_id="dbt_intermediate",
        bash_command=f"{DBT_CMD} run --select intermediate --profiles-dir {DBT_DIR}",
    )

    dbt_marts = BashOperator(
        task_id="dbt_marts",
        bash_command=f"{DBT_CMD} run --select marts --profiles-dir {DBT_DIR}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{DBT_CMD} test --profiles-dir {DBT_DIR}",
    )

    dbt_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"{DBT_CMD} docs generate --profiles-dir {DBT_DIR}",
    )

    wait_for_ingest >> dbt_deps >> dbt_staging >> dbt_intermediate >> dbt_marts >> dbt_test >> dbt_docs
