from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# dbt projesi container içinde /opt/airflow/dbt'ye bağlandı (volume).
# DBT_PROFILES_DIR ortam değişkeni /opt/airflow/dbt_profiles'i gösteriyor,
# o yüzden ayrıca --profiles-dir vermeye gerek yok.
DBT_PROJECT_DIR = "/opt/airflow/dbt"
# dbt, Airflow'la çakışmaması için izole bir venv'e kuruldu (bkz. Dockerfile).
DBT = "/opt/dbt-venv/bin/dbt"

with DAG(
    dag_id="dbt_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,        # otomatik zamanlama yok, elle tetiklenir
    catchup=False,        # geçmiş tarihler için çalıştırma yapma
    tags=["dbt"],
) as dag:

    # dbt modellerini çalıştır (silver + gold)
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT} run",
    )

    # dbt testlerini çalıştır
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT} test",
    )

    # Sıralama: önce run, sonra test
    dbt_run >> dbt_test
