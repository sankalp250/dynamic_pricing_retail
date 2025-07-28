# streamlit_app/pages/1_📈_Executive_Dashboard.py

import streamlit as st
import sys
import os

# --- Path setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- Corrected Imports (Reads from Parquet file, NO database) ---
from streamlit_app.components.plots import (
    fetch_data_from_parquet,
    create_sales_overview_line_chart,
    create_segment_distribution_pie_chart,
    create_category_sales_bar_chart
)
from streamlit_app.components.kpi_cards import create_kpi_card

st.set_page_config(page_title="Executive Dashboard", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
css_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'style.css')
local_css(css_path)

st.title("📈 Executive Dashboard")
st.markdown("A high-level overview of key business metrics and performance indicators.")

# --- Corrected Data Fetching ---
df = fetch_data_from_parquet()

if df.empty:
    st.warning("Data file not found. Please run the `scripts/3_create_parquet_export.py` script.")
    st.stop()

# --- Display KPIs ---
st.markdown("### Key Performance Indicators")
total_revenue = df['price'].sum()
total_orders = df['order_id'].nunique()
unique_customers = df['customer_unique_id'].nunique()
avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1: create_kpi_card("Total Revenue", f"R${total_revenue:,.2f}")
with col2: create_kpi_card("Total Orders", f"{total_orders:,}")
with col3: create_kpi_card("Unique Customers", f"{unique_customers:,}")
with col4: create_kpi_card("Avg. Order Value", f"R${avg_order_value:,.2f}")

st.markdown("<hr>", unsafe_allow_html=True)

# --- Display Charts ---
col_left, col_right = st.columns(2, gap="large")
with col_left:
    st.plotly_chart(create_sales_overview_line_chart(df), use_container_width=True)
    st.plotly_chart(create_category_sales_bar_chart(df), use_container_width=True)
with col_right:
    st.plotly_chart(create_segment_distribution_pie_chart(df), use_container_width=True)