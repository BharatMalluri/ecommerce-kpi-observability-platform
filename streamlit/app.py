import os
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="E-Commerce Pipeline Dashboard", page_icon="📊", layout="wide")

@st.cache_resource
def get_engine():
    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER','admin')}:"
        f"{os.getenv('POSTGRES_PASSWORD','changeme')}@"
        f"{os.getenv('POSTGRES_HOST','localhost')}:"
        f"{os.getenv('POSTGRES_PORT','5432')}/"
        f"{os.getenv('POSTGRES_DB','ecommerce')}"
    )
    return create_engine(url)

@st.cache_data(ttl=300)
def load_daily_kpis():
    return pd.read_sql("SELECT * FROM public_marts.agg_daily_kpis ORDER BY date DESC LIMIT 90", get_engine())

@st.cache_data(ttl=300)
def load_anomaly_log():
    return pd.read_sql("SELECT * FROM monitoring.anomaly_log ORDER BY detected_at DESC LIMIT 100", get_engine())

@st.cache_data(ttl=300)
def load_pipeline_runs():
    return pd.read_sql("SELECT * FROM monitoring.pipeline_runs ORDER BY finished_at DESC LIMIT 20", get_engine())

@st.cache_data(ttl=300)
def load_customer_segments():
    return pd.read_sql(
        "SELECT customer_segment, count(*) as customers, sum(lifetime_value) as total_ltv "
        "FROM public_marts.dim_customers GROUP BY customer_segment",
        get_engine()
    )

st.title("📊 E-Commerce Pipeline — Data Quality & KPI Status")
st.caption("Powered by dbt · Great Expectations · PostgreSQL · Airflow")

try:
    kpis = load_daily_kpis()
    latest = kpis.iloc[0] if not kpis.empty else {}

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Today's Revenue",   f"€{latest.get('total_revenue', 0):,.0f}")
    col2.metric("Orders Today",      f"{latest.get('total_orders', 0):,.0f}")
    col3.metric("Unique Customers",  f"{latest.get('unique_customers', 0):,.0f}")
    col4.metric("Avg Order Value",   f"€{latest.get('avg_order_value', 0):,.2f}")
    col5.metric("Cancellation Rate", f"{latest.get('cancellation_rate_pct', 0):.1f}%")

    st.divider()

    st.subheader("📈 Daily Revenue — Last 90 Days")
    fig = px.line(
        kpis.sort_values("date"),
        x="date", y=["total_revenue", "revenue_7d_avg"],
        labels={"value": "Revenue (€)", "variable": "Metric"},
        color_discrete_map={"total_revenue": "#2563eb", "revenue_7d_avg": "#f59e0b"},
    )
    st.plotly_chart(fig, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📦 Daily Orders")
        fig2 = px.bar(
            kpis.sort_values("date").tail(30),
            x="date", y="total_orders", color="cancellation_rate_pct",
            color_continuous_scale="RdYlGn_r",
            labels={"total_orders": "Orders", "cancellation_rate_pct": "Cancel %"},
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        st.subheader("👥 Customer Segments by LTV")
        try:
            segments = load_customer_segments()
            fig3 = px.pie(
                segments, names="customer_segment", values="customers",
                color_discrete_map={"high": "#16a34a", "medium": "#f59e0b", "low": "#dc2626"},
            )
            st.plotly_chart(fig3, use_container_width=True)
        except Exception:
            st.info("Customer segment data not yet available.")

except Exception as e:
    st.error(f"Could not load KPI data: {e}")

st.divider()

st.subheader("🔍 Data Quality — Anomaly Log")
try:
    anomalies = load_anomaly_log()
    if anomalies.empty:
        st.success("✅ No anomalies detected.")
    else:
        fails = anomalies[anomalies["status"] == "fail"]
        passes = anomalies[anomalies["status"] == "pass"]
        st.metric("Checks Passed", len(passes), delta=f"-{len(fails)} failed", delta_color="inverse")
        st.dataframe(anomalies, use_container_width=True)
except Exception as e:
    st.warning(f"Anomaly log not available: {e}")

st.divider()

st.subheader("🔄 Recent Pipeline Runs")
try:
    runs = load_pipeline_runs()
    if runs.empty:
        st.info("No pipeline runs recorded yet.")
    else:
        st.dataframe(runs, use_container_width=True)
except Exception as e:
    st.warning(f"Pipeline run log not available: {e}")

st.caption("Refresh every 5 minutes · Data from PostgreSQL marts schema")