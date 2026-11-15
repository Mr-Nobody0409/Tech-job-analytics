from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator # type: ignore


with DAG(
    dag_id="tech_job_analytics_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["tech-jobs", "etl"],
) as dag:

    run_etl = BashOperator(
        task_id="run_etl_pipeline",
        bash_command="python /app/src/pipeline.py",
    )

    run_etl