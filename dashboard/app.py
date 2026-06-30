import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="E-Commerce Analytics", layout="wide")
st.title("📊 Olist E-Commerce Analytics Dashboard")
st.caption("Brezilya e-ticaret verisi · dbt + Airflow + FastAPI ile beslenir")


# Yardımcı: API'den veri çek
def fetch(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API hatası ({endpoint}): {e}")
        return None


# === ÜST SATIR: Genel özet metrikleri ===
summary = fetch("/summary")
if summary:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam Sipariş", f"{summary['total_orders']:,}")
    col2.metric("Toplam Gelir", f"R$ {summary['total_revenue']:,.0f}")
    col3.metric("Ort. Sipariş Tutarı", f"R$ {summary['avg_order_value']:,.2f}")
    col4.metric("Toplam Kargo", f"R$ {summary['total_freight']:,.0f}")

st.divider()

# === İKİNCİ SATIR: Aylık trend + Sipariş durumu ===
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Aylık Sipariş Trendi")
    monthly = fetch("/monthly-orders")
    if monthly:
        df = pd.DataFrame(monthly)
        fig = px.line(df, x="month", y="order_count", markers=True)
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Sipariş Durumu Dağılımı")
    status = fetch("/order-status")
    if status:
        df = pd.DataFrame(status)
        fig = px.pie(df, names="order_status", values="order_count")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# === ÜÇÜNCÜ SATIR: Top kategoriler + Eyalet gelir ===
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("En Çok Satan Kategoriler")
    cats = fetch("/top-categories")
    if cats:
        df = pd.DataFrame(cats)
        fig = px.bar(df, x="items_sold", y="category", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Eyalet Bazında Gelir")
    states = fetch("/revenue-by-state")
    if states:
        df = pd.DataFrame(states).head(10)
        fig = px.bar(df, x="customer_state", y="revenue")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# === DÖRDÜNCÜ SATIR: Teslimat süresi + Fiyat dağılımı ===
col_x, col_y = st.columns(2)

with col_x:
    st.subheader("Eyalet Bazında Ort. Teslimat Süresi (gün)")
    delivery = fetch("/avg-delivery-time")
    if delivery:
        df = pd.DataFrame(delivery).head(10)
        fig = px.bar(df, x="customer_state", y="avg_delivery_days")
        st.plotly_chart(fig, use_container_width=True)

with col_y:
    st.subheader("Sipariş Tutarı Dağılımı")
    dist = fetch("/order-value-distribution")
    if dist:
        df = pd.DataFrame(dist)
        fig = px.bar(df, x="price_range", y="order_count")
        st.plotly_chart(fig, use_container_width=True)
