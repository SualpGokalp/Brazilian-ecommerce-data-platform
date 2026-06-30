import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# 1. .env dosyasındaki bağlantı bilgilerini yükle
load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

# 2. PostgreSQL bağlantısı oluştur (SQLAlchemy "engine")
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

# 3. bronze schema'sını oluştur (yoksa)
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze"))
    conn.commit()
    print("bronze schema hazır.")

# 4. CSV dosya adı  ->  sade tablo adı eşlemesi
csv_to_table = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

# 5. Her CSV'yi oku ve bronze schema'sına yaz
for csv_file, table_name in csv_to_table.items():
    csv_path = os.path.join(data_dir, csv_file)
    print(f"Yükleniyor: {csv_file} -> bronze.{table_name}")

    df = pd.read_csv(csv_path)

    # Tablo zaten varsa DROP (if_exists="replace") kullanmıyoruz: üstüne kurulu
    # dbt silver view'ları DROP'u engeller (DependentObjectsStillExist).
    # Bunun yerine TRUNCATE + append yapıyoruz; TRUNCATE view'ları etkilemez.
    if inspect(engine).has_table(table_name, schema="bronze"):
        with engine.begin() as conn:
            conn.execute(text(f'TRUNCATE TABLE bronze."{table_name}"'))
        if_exists = "append"
    else:
        if_exists = "replace"   # ilk yüklemede tabloyu oluştur

    df.to_sql(
        table_name,
        engine,
        schema="bronze",
        if_exists=if_exists,
        index=False,           # pandas'ın satır numarasını ekleme
        chunksize=10000,       # büyük dosyaları parça parça yaz (bellek dostu)
    )
    print(f"   {len(df):,} satır yüklendi.")

print("\nTüm tablolar bronze schema'sına yüklendi.")