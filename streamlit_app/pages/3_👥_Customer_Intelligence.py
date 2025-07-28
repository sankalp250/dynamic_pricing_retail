# streamlit_app/pages/3_👥_Customer_Intelligence.py

import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px

# --- Path setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- Corrected Imports (Reads from Parquet file, NO database) ---
from streamlit_app.components.plots import fetch_data_from_parquet
from streamlit_app.components.kpi_cards import create_kpi_card

st.set_page_config(page_title="Customer Intelligence", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
css_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'style.css')
local_css(css_path)

st.title("👥 Customer Intelligence")
st.markdown("Select a tab below for a detailed breakdown of each customer segment.")

# --- Corrected Data Fetching ---
df = fetch_data_from_parquet()

if df.empty or 'customer_segment' not in df.columns or df['customer_segment'].isnull().all():
    st.warning("Customer segment data not found in the data file. Please run `scripts/3_create_parquet_export.py` to generate it.")
    st.stop()
st.markdown("<hr>", unsafe_allow_html=True)

# --- Segment Tabs for individual details ---
st.header("Segment-Level Deep-Dive")
segment_names = {0: 'Best Customers', 1: 'Loyal Customers', 2: 'At-Risk Customers', 3: 'New/Infrequent'}
segment_descriptions = {
    0: "Your champions. Most recent, frequent, and highest-spending customers. Nurture with loyalty programs and exclusive offers.",
    1: "Consistent buyers. Purchase frequently but may not be the highest spenders. Engage with personalized recommendations.",
    2: "Customers at risk of churning. Haven't purchased recently. Re-engage with targeted marketing and special discounts.",
    3: "New or one-time buyers. The goal is to encourage a second purchase with follow-up engagement."
}
tab_names = [segment_names[i] for i in sorted(segment_names.keys())]
tabs = st.tabs(tab_names)

for i, tab in enumerate(tabs):
    segment_id = sorted(segment_names.keys())[i]
    with tab:
        st.subheader(f"Profile: {segment_names[segment_id]}")
        st.markdown(f"*{segment_descriptions[segment_id]}*")
        
        segment_df = df[df['customer_segment'] == segment_id]
        
        st.markdown("#### Segment KPIs")
        num_customers = segment_df['customer_unique_id'].nunique()
        segment_revenue = segment_df['price'].sum()
        avg_revenue_per_customer = segment_revenue / num_customers if num_customers > 0 else 0
        
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1: create_kpi_card("Number of Customers", f"{num_customers:,}")
        with kpi_col2: create_kpi_card("Total Revenue from Segment", f"R${segment_revenue:,.2f}")
        with kpi_col3: create_kpi_card("Avg. Revenue per Customer", f"R${avg_revenue_per_customer:,.2f}")
            
        st.markdown("#### Top 5 Products Purchased")
        if not segment_df.empty:
            top_products = segment_df['product_category_name_english'].value_counts().nlargest(5).reset_index()
            top_products.columns = ['Product Category', 'Number of Purchases']
            fig_bar = px.bar(top_products, x='Number of Purchases', y='Product Category', orientation='h', title=f"Most Popular Categories for {segment_names[segment_id]}")
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No data available for this segment.")