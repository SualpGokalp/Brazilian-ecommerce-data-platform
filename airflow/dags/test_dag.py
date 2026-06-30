from datetime import datetime

from airflow.operators.bash import BashOperator

from airflow import DAG

# DAG tanımı
with DAG(
    dag_id="test_dag",                          # DAG'ın adı (arayüzde görünür)
    start_date=datetime(2026, 1, 1),            # ne zamandan itibaren geçerli
    schedule=None,                              # otomatik zamanlama yok, elle tetikle
    catchup=False,                              # geçmiş tarihleri çalıştırma
    tags=["test"],                              # arayüzde etiket
) as dag:

    # Görev 1: ekrana yazı yaz
    gorev1 = BashOperator(
        task_id="merhaba",
        bash_command="echo 'Merhaba Airflow! İlk gorevim calisiyor.'"
    )

    # Görev 2: tarihi yaz
    gorev2 = BashOperator(
        task_id="tarih_yaz",
        bash_command="date"
    )

    # Sıralama: önce görev1, sonra görev2
    gorev1 >> gorev2