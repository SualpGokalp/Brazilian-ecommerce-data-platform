# Airflow 3.0.0 imajını temel al
FROM apache/airflow:3.0.0

# git: dbt'nin paket/deps işlemleri ve "dbt debug" için gerekli
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# dbt'yi Airflow'un Python ortamından İZOLE bir venv'e kur.
# Neden: dbt-postgres 1.10.2 -> click>=8.3 ister; Airflow 3.0 ise click 8.1.x'e
# bağlıdır ve click 8.2+ celery worker CLI'sini bozar (nodesplit None hatası).
# Ayrı venv ile iki dünyanın bağımlılıkları çakışmaz.
RUN python -m venv /opt/dbt-venv \
    && /opt/dbt-venv/bin/pip install --no-cache-dir dbt-postgres==1.10.2 \
    && chown -R airflow:0 /opt/dbt-venv

USER airflow
