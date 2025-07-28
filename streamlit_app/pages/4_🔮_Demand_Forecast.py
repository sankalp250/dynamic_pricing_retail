# streamlit_app/pages/4_🔮_Demand_Forecast.py

import streamlit as st
import pandas as pd
import sys
import os

# --- Path setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- Corrected Imports (Reads from Parquet file, NO database) ---
from src.analysis.forecasting import generate_forecast
from streamlit_app.components.plots import fetch_data_from_parquet
from prophet.plot import plot_plotly, plot_components_plotly

st.set_page_config(page_title="Demand Forecast", layout="wide")
st.title("🔮 Demand Forecast Dashboard")
st.markdown("Predict future sales revenue for the entire business or a specific product category.")

# --- Corrected Data Fetching ---
df = fetch_data_from_parquet()

if df.empty:
    st.warning("Data file not found. Please run the `scripts/3_create_parquet_export.py` script first.")
    st.stop()

# --- Sidebar for user input ---
st.sidebar.header("Forecast Options")
forecast_days = st.sidebar.slider("Days to Forecast:", 30, 365, 90, 30)
categories = ['All Products'] + sorted(df['product_category_name_english'].unique().tolist())
selected_category = st.sidebar.selectbox("Select Product Category", categories)

# --- Generate Forecast ---
title_category = "All Products" if selected_category == 'All Products' else selected_category
with st.spinner(f"Generating a forecast for '{title_category}'..."):
    model, forecast = generate_forecast(df, periods=forecast_days, product_category=selected_category)

if model is None or forecast is None:
    st.error(f"Could not generate a forecast for '{title_category}'. The dataset may not have enough consistent sales data (at least 60 days required).")
    st.stop()

# --- Display Forecast Plot ---
st.header(f"Revenue Forecast: {title_category}")
st.success(f"Forecast generated successfully for the next {forecast_days} days.")
fig_forecast = plot_plotly(model, forecast)
fig_forecast.update_layout(xaxis_title='Date', yaxis_title='Predicted Revenue (R$)')
st.plotly_chart(fig_forecast, use_container_width=True)

# --- Display Seasonality Components ---
st.header("Forecast Components")
fig_components = plot_components_plotly(model, forecast)
st.plotly_chart(fig_components, use_container_width=True)

# --- Key Takeaways & Numbers ---
st.header("Forecasted Metrics")
col1, col2 = st.columns(2)
with col1:
    last_historical_date = model.history_dates.max()
    last_historical_value = model.history['y'].iloc[-1]
    st.metric(
        "Last Recorded Daily Revenue",
        f"R${last_historical_value:,.2f}",
        f"on {last_historical_date.strftime('%Y-%m-%d')}"
    )
with col2:
    future_date = forecast['ds'].iloc[-1]
    projected_value = forecast['yhat'].iloc[-1]
    st.metric(
        f"Projected Revenue in {forecast_days} Days",
        f"R${projected_value:,.2f}",
        f"for {future_date.strftime('%Y-%m-%d')}"
    )