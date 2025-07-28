# streamlit_app/pages/2_📊_Price_Optimization_Lab.py

import streamlit as st
import sys, os, numpy as np, pandas as pd, plotly.express as px

# --- Path setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- Corrected Imports (Reads from Parquet file, NO database) ---
from src.analysis.elasticity import calculate_elasticity_and_model
from src.analysis.cross_elasticity import calculate_cross_price_elasticity
from streamlit_app.components.plots import fetch_data_from_parquet, create_price_elasticity_scatter_plot

st.set_page_config(page_title="Price Optimization Lab", layout="wide")
st.title("📊 Price Optimization Lab")
st.markdown("Analyze both own-price and cross-price elasticity to inform your pricing strategy.")

# --- Corrected Data Fetching ---
df = fetch_data_from_parquet()
if df.empty:
    st.warning("Data file not found. Please run the `scripts/3_create_parquet_export.py` script.")
    st.stop()

# --- Create Tabs ---
tab1, tab2 = st.tabs(["📈 Own-Price Elasticity & Profit Simulation", "🔄 Cross-Price Elasticity Analysis"])

# ========================= TAB 1: OWN-PRICE ELASTICITY =========================
with tab1:
    st.header("Profit Forecasting Simulator")
    
    cat_list = ['All Products'] + sorted(df['product_category_name_english'].unique().tolist())
    selected_category_own = st.selectbox("Select a Product Category to Analyze", cat_list, key="own_price_cat")

    elasticity, model = calculate_elasticity_and_model(df, product_category=selected_category_own if selected_category_own != 'All Products' else 'all')

    if model is None:
        st.error(f"Could not build a model for '{selected_category_own}'. Insufficient data.")
    else:
        fig_scatter = create_price_elasticity_scatter_plot(df, selected_category_own if selected_category_own != 'All Products' else 'All Products')
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("---")
        
        sim_col1, sim_col2 = st.columns([1, 2])
        with sim_col1:
            st.metric(label="Calculated Price Elasticity", value=f"{elasticity:.2f}")

            default_price = df[df['product_category_name_english'] == selected_category_own]['price'].mean()
            if pd.isna(default_price): default_price = 1.0

            new_price = st.number_input("Enter a new price to simulate:", min_value=0.01, value=default_price, step=1.0, format="%.2f")
            
            intercept, log_price_coeff = model.params['const'], model.params['log_price']
            pred_demand = np.exp(intercept + log_price_coeff * np.log(new_price))

            if pd.isna(pred_demand):
                st.warning("Model unstable, cannot produce demand prediction.")
            else:
                proj_revenue = new_price * pred_demand
                st.success(f"Projected Revenue: **R${proj_revenue:,.2f}**")
        
        with sim_col2:
            st.subheader("Automated Price Recommendation")
            if st.button("Find Revenue-Maximizing Price", key="find_optimal"):
                with st.spinner("Simulating..."):
                    price_stats = df[df['product_category_name_english'] == selected_category_own]['price'].describe()
                    min_realistic_price = price_stats.get('25%', price_stats.get('mean', 1) * 0.7)
                    max_realistic_price = price_stats.get('75%', price_stats.get('mean', 1) * 1.3)
                    price_range = np.linspace(min_realistic_price, max_realistic_price, 100)
                    revenues = [p * np.exp(intercept + log_price_coeff * np.log(p)) for p in price_range]
                    sim_df = pd.DataFrame({'Price': price_range, 'Projected_Revenue': revenues})

                    if sim_df['Projected_Revenue'].isnull().all():
                        st.error("Model failed to produce valid revenue predictions.")
                    else:
                        optimal_idx = sim_df['Projected_Revenue'].idxmax()
                        optimal_price = sim_df.loc[optimal_idx, 'Price']
                        max_revenue = sim_df.loc[optimal_idx, 'Projected_Revenue']
                        st.success(f"💡 Recommended Price: R${optimal_price:.2f}")
                        st.info(f"Projected Max Revenue: R${max_revenue:,.2f}")
                        fig_rev = px.line(sim_df, x='Price', y='Projected_Revenue', title="Projected Revenue Curve")
                        fig_rev.add_vline(x=optimal_price, line_dash="dash", line_color="red")
                        st.plotly_chart(fig_rev, use_container_width=True)

# ========================= TAB 2: CROSS-PRICE ELASTICITY =========================
with tab2:
    st.header("Discover Product Relationships")
    st.markdown("Analyze how changing the price of one product category impacts the sales of another.")

    cat_list_no_all = sorted(df['product_category_name_english'].unique().tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        demand_cat = st.selectbox("Product A (Demand changes)", cat_list_no_all, index=0)
    with col2:
        price_cat = st.selectbox("Product B (Price changes)", cat_list_no_all, index=1)
        
    if st.button("Calculate Cross-Price Elasticity", key="calc_cross"):
        if demand_cat == price_cat:
            st.error("Please select two different product categories to analyze.")
        else:
            with st.spinner(f"Analyzing relationship between '{demand_cat}' and '{price_cat}'..."):
                score = calculate_cross_price_elasticity(df, demand_category=demand_cat, price_category=price_cat)
                
                st.metric("Cross-Price Elasticity Score", value=f"{score:.2f}" if score is not None else "N/A")

                if score is not None:
                    if score > 0.1:
                        st.success(f"**Conclusion: These products are SUBSTITUTES.**\n\nAn increase in the price of '{price_cat}' is likely to **increase** the demand for '{demand_cat}'.")
                    elif score < -0.1:
                        st.warning(f"**Conclusion: These products are COMPLEMENTS.**\n\nAn increase in the price of '{price_cat}' is likely to **decrease** the demand for '{demand_cat}'.")
                    else:
                        st.info(f"**Conclusion: These products are UNRELATED.**\n\nChanging the price of '{price_cat}' has little to no effect on the demand for '{demand_cat}'.")
                else:
                    st.error("Could not calculate a reliable score due to insufficient overlapping sales data.")