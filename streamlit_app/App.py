# streamlit_app/App.py

import streamlit as st

st.set_page_config(
    page_title="Retail Insights Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar ---
with st.sidebar:
    st.title("🛒 Retail Insights Engine")
    st.markdown("---")
    st.info("Select a dashboard from the pages above to begin your analysis.")

# Function to load local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply the CSS
local_css("streamlit_app/assets/style.css")


# --- Main Page ---
st.title("Dynamic Pricing & Retail Analysis")
st.markdown("Welcome! This interactive dashboard uses machine learning to transform raw sales data into strategic intelligence.")
st.markdown("---")

# --- Feature Columns using your local images ---
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.image("streamlit_app/assets/images/dashboard.png", width=110)
    st.subheader("📈 Executive Dashboard")
    st.write("Get a high-level view of your business. Track core KPIs like revenue, order volume, and customer growth in real-time.")

with col2:
    st.image("streamlit_app/assets/images/seo-tag.png", width=110)
    st.subheader("📊 Price Optimization Lab")
    st.write("Unlock pricing power by analyzing demand elasticity. Discover opportunities for price adjustments and promotions.")

with col3:
    st.image("streamlit_app/assets/images/virtual-assistant.png", width=100)
    st.subheader("👥 Customer Intelligence")
    st.write("Understand customer buying habits with RFM-based segmentation and tailor your marketing for maximum engagement.")

st.markdown("---")

with st.expander("Showcased Technology & Methodology"):
    st.markdown("""
    This project demonstrates a professional, end-to-end data workflow:
    - **Data Ingestion & ETL:** Raw relational data is extracted, cleaned, and loaded into a **MySQL** database.
    - **Price Elasticity Modeling:** A **Log-Log Linear Regression** model (**Statsmodels**) quantifies the relationship between price and demand.
    - **Customer Segmentation:** Customers are segmented using **RFM Analysis** and **K-Means Clustering** (**Scikit-learn**).
    - **Interactive Frontend:** The application is built with **Streamlit** and features visualizations by **Plotly**.
    - **Professional Structure:** Code is separated into modules for database logic, analysis, and frontend components.
    """)