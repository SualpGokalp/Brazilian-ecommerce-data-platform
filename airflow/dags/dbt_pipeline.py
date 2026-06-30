from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator

from airflow import DAG

# --- Yollar (hepsi container içi) ---
# dbt projesi volume ile /opt/airflow/dbt'ye bağlandı.
# DBT_PROFILES_DIR env'i /opt/airflow/dbt_profiles'i gösterdiği için --profiles-dir gerekmez.
DBT_PROJECT_DIR = "/opt/airflow/dbt"
# dbt, Airflow ile çakışmaması için izole bir venv'e kuruldu (bkz. Dockerfile).
DBT = "/opt/dbt-venv/bin/dbt"
# ingestion bağımlılıkları (pandas/sqlalchemy) da ayrı bir izole venv'de.
INGESTION_PY = "/opt/ingestion-venv/bin/python"
INGESTION_SCRIPT = "/opt/airflow/ingestion/load_to_bronze.py"

# Tüm görevlere uygulanan ortak ayarlar.
default_args = {
    "owner": "sualp",
    "retries": 2,                              # hata olursa görevi 2 kez daha dene
    "retry_delay": timedelta(minutes=5),       # denemeler arası 5 dk bekle
    "execution_timeout": timedelta(minutes=30),  # 30 dk'yı aşan görev iptal edilsin
}

with DAG(
    dag_id="dbt_pipeline",
    description="Bronze ingestion -> dbt run -> dbt test -> dbt docs uçtan uca pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,        # otomatik zamanlama yok, elle tetiklenir
    catchup=False,        # geçmiş tarihler için çalıştırma yapma
    tags=["dbt", "ingestion", "ecommerce", "bronze"],
) as dag:

    # 1) Ham CSV'leri PostgreSQL'in bronze şemasına yükle.
    #    İzole ingestion venv'inin python'u ile çalışır; POSTGRES_* env'leri
    #    compose'dan gelir (host=ecommerce_db).
    ingestion = BashOperator(
        task_id="ingestion",
        bash_command=f"{INGESTION_PY} {INGESTION_SCRIPT}",
    )
    ingestion.doc_md = """
    ### Bronze Ingestion
    `load_to_bronze.py` ile ham Olist CSV dosyalarını PostgreSQL'deki **bronze**
    şemasına yükler. İzole `ingestion-venv` (pandas + SQLAlchemy) kullanır.
    Bağlantı bilgileri `POSTGRES_*` ortam değişkenlerinden okunur.
    """

    # 2) dbt modellerini çalıştır (silver + gold).
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT} run",
    )
    dbt_run.doc_md = """
    ### dbt run
    bronze verisi üzerine **silver** (staging view) ve **gold** (tablo) modellerini
    inşa eder. İzole `dbt-venv` kullanır.
    """

    # 3) dbt testlerini çalıştır (veri kalitesi).
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT} test",
    )
    dbt_test.doc_md = """
    ### dbt test
    Modeller üzerindeki veri kalitesi testlerini (not_null, unique, ilişkiler vb.)
    çalıştırır. Başarısız test pipeline'ı durdurur.
    """

    # 4) dbt dokümantasyonunu üret.
    dbt_docs = BashOperator(
        task_id="dbt_docs",
        bash_command=f"cd {DBT_PROJECT_DIR} && {DBT} docs generate",
    )
    dbt_docs.doc_md = """
    ### dbt docs generate
    Modellerin/şemaların dokümantasyon ve soyağacı (lineage) çıktısını
    (`target/` altında) üretir.
    """

    # Görev zinciri: önce yükleme, sonra dönüşüm, test ve dokümantasyon.
    ingestion >> dbt_run >> dbt_test >> dbt_docs
