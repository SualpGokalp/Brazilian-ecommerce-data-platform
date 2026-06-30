import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env'den bağlantı bilgilerini oku
load_dotenv()

user = os.getenv("POSTGRES_USER", "dbt_user")
password = os.getenv("POSTGRES_PASSWORD", "dbt_password")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "ecommerce")

# Veritabanı bağlantısı
engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

# FastAPI uygulaması
app = FastAPI(
    title="E-Commerce Analytics API",
    description="Olist veri platformu - Gold katmanı metrikleri",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "E-Commerce Analytics API çalışıyor"}


@app.get("/health")
def health():
    # Veritabanı bağlantısını test et
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/summary")
def order_summary():
    """Genel sipariş özeti: toplam sipariş, gelir, ortalama tutar."""
    query = text("""
        select
            count(*)                          as total_orders,
            round(sum(total_price), 2)        as total_revenue,
            round(avg(total_price), 2)        as avg_order_value,
            round(sum(total_freight), 2)      as total_freight
        from gold.fct_orders
        where total_price is not null
    """)
    with engine.connect() as conn:
        row = conn.execute(query).mappings().first()
    return dict(row)


@app.get("/revenue-by-state")
def revenue_by_state():
    """Eyalet bazında sipariş sayısı ve gelir."""
    query = text("""
        select
            c.customer_state,
            count(*)                    as order_count,
            round(sum(f.total_price), 2) as revenue
        from gold.fct_orders f
        join gold.dim_customers c
            on f.customer_id = c.customer_id
        where f.total_price is not null
        group by c.customer_state
        order by revenue desc
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


@app.get("/order-status")
def order_status_distribution():
    """Sipariş durumlarının dağılımı (delivered, shipped, vb.)."""
    query = text("""
        select
            order_status,
            count(*) as order_count
        from gold.fct_orders
        group by order_status
        order by order_count desc
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]

@app.get("/top-categories")
def top_categories(limit: int = 10):
    """En çok satan ürün kategorileri (sipariş kalemi sayısına göre)."""
    query = text("""
        select
            p.product_category_name_english as category,
            count(*)                        as items_sold,
            round(sum(i.price), 2)          as revenue
        from silver.stg_order_items i
        join gold.dim_products p
            on i.product_id = p.product_id
        where p.product_category_name_english is not null
        group by p.product_category_name_english
        order by items_sold desc
        limit :limit
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]


@app.get("/monthly-orders")
def monthly_orders():
    """Aylara göre sipariş sayısı ve gelir (zaman trendi)."""
    query = text("""
        select
            to_char(order_purchase_timestamp, 'YYYY-MM') as month,
            count(*)                                      as order_count,
            round(sum(total_price), 2)                    as revenue
        from gold.fct_orders
        where order_purchase_timestamp is not null
          and total_price is not null
        group by to_char(order_purchase_timestamp, 'YYYY-MM')
        order by month
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


@app.get("/avg-delivery-time")
def avg_delivery_time():
    """Eyalet bazında ortalama teslimat süresi (gün)."""
    query = text("""
        select
            c.customer_state,
            round(avg(
                extract(epoch from (
                    f.order_delivered_customer_date - f.order_purchase_timestamp
                )) / 86400
            )::numeric, 1) as avg_delivery_days,
            count(*) as delivered_orders
        from gold.fct_orders f
        join gold.dim_customers c
            on f.customer_id = c.customer_id
        where f.order_delivered_customer_date is not null
          and f.order_purchase_timestamp is not null
        group by c.customer_state
        order by avg_delivery_days desc
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


@app.get("/order-value-distribution")
def order_value_distribution():
    """Sipariş tutarlarının dağılımı (fiyat aralıklarına göre)."""
    query = text("""
        select
            case
                when total_price < 50  then '0-50'
                when total_price < 100 then '50-100'
                when total_price < 200 then '100-200'
                when total_price < 500 then '200-500'
                else '500+'
            end as price_range,
            count(*) as order_count
        from gold.fct_orders
        where total_price is not null
        group by price_range
        order by min(total_price)
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(r) for r in rows]


@app.get("/top-cities")
def top_cities(limit: int = 15):
    """En çok sipariş veren şehirler."""
    query = text("""
        select
            c.customer_city,
            c.customer_state,
            count(*)                     as order_count,
            round(sum(f.total_price), 2) as revenue
        from gold.fct_orders f
        join gold.dim_customers c
            on f.customer_id = c.customer_id
        where f.total_price is not null
        group by c.customer_city, c.customer_state
        order by order_count desc
        limit :limit
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"limit": limit}).mappings().all()
    return [dict(r) for r in rows]