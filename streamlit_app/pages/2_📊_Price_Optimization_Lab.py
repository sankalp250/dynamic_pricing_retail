# streamlit_app/pages/2_📊_Price_Optimization_Lab.py

import streamlit as st
import sys, os, numpy as np, pandas as pd, plotly.express as px

# --- Path adjustments and imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.database.utils import get_db_engine
from src.analysis.elasticity import calculate_elasticity_and_model
from src.analysis.cross_elasticity import calculate_cross_price_elasticity
from streamlit_app.components.plots import fetch_data_from_db, create_price_elasticity_scatter_plot

st.set_page_config(page_title="Price Optimization Lab", layout="wide")
st.title("📊 Price Optimization Lab")
st.markdown("Analyze both own-price and cross-price elasticity to inform your pricing strategy.")

# --- Load Data ---
engine = get_db_engine()
if engine is None: st.error("Database connection failed."); st.stop()
df = fetch_data_from_db(engine)
if df.empty: st.warning("Dataframe empty."); st.stop()


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
        # (The rest of the simulation code is the same as before)
        with sim_col1:
            st.info(f"Historical Avg. Price: R${df[df['product_category_name_english'] == selected_category_own]['price'].mean():.2f}")
            st.metric(label="Calculated Price Elasticity", value=f"{elasticity:.2f}")

            default_price = df[df['product_category_name_english'] == selected_category_own]['price'].mean()
            if pd.isna(default_price): default_price = 1.0

            new_price = st.number_input("Enter a new price to simulate:", min_value=0.01, value=default_price, step=1.0, format="%.2f", key="price_sim")
            
            intercept, log_price_coeff = model.params['const'], model.params['log_price']
            pred_demand = np.exp(intercept + log_price_coeff * np.log(new_price))

            if pd.isna(pred_demand):
                st.warning("Model unstable, could not produce demand prediction.")
            else:
                proj_revenue = new_price * pred_demand
                st.success(f"Projected Revenue: **R${proj_revenue:,.2f}**")
                st.write(f"At this price, we predict selling **{int(round(pred_demand))}** units.")
        
        with sim_col2:
            st.subheader("Automated Price Recommendation")

if st.button("Find Revenue-Maximizing Price", key="find_optimal"):
    with st.spinner("Simulating revenues within a realistic price range..."):
        # Get historical price stats for this category
        price_stats = df[df['product_category_name_english'] == selected_category_own]['price'].describe()
        
        min_realistic_price = price_stats.get('25%', price_stats.get('mean', 1) * 0.7)
        max_realistic_price = price_stats.get('75%', price_stats.get('mean', 1) * 1.3)
        
        price_range = np.linspace(min_realistic_price, max_realistic_price, 100)

        # Run the simulation on this tighter, more realistic range
        revenues = [p * np.exp(intercept + log_price_coeff * np.log(p)) for p in price_range]
        simulation_df = pd.DataFrame({'Price': price_range, 'Projected_Revenue': revenues})

        # --- The rest of the logic can now work safely ---
        if simulation_df['Projected_Revenue'].isnull().all():
            st.error("Model failed to produce valid revenue predictions for this category.")
        else:
            optimal_idx = simulation_df['Projected_Revenue'].idxmax()
            optimal_price = simulation_df.loc[optimal_idx, 'Price']
            max_revenue = simulation_df.loc[optimal_idx, 'Projected_Revenue']

            # Display the smarter recommendation
            st.success(f"💡 Recommended Price (within realistic range): **R${optimal_price:.2f}**")
            st.info(f"This price is projected to generate the maximum revenue of **R${max_revenue:,.2f}** from a plausible price range.")
            
            fig_rev = px.line(simulation_df, x='Price', y='Projected_Revenue', title="Projected Revenue Curve (Realistic Range)")
            fig_rev.add_vline(x=optimal_price, line_dash="dash", line_color="red", annotation_text="Optimal Price")
            fig_rev.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rev, use_container_width=True)

# ========================= TAB 2: CROSS-PRICE ELASTICITY =========================
with tab2:
    st.header("Discover Product Relationships")
    st.markdown("Analyze how changing the price of one product category impacts the sales of another.")

    cat_list_no_all = sorted(df['product_category_name_english'].unique().tolist())
    
    col1, col2 = st.columns(2)
    with col1:
        demand_cat = st.selectbox(
            "Product with Changing DEMAND (Product A)",
            cat_list_no_all, index=0, key="demand_cat"
        )
    with col2:
        price_cat = st.selectbox(
            "Product with Changing PRICE (Product B)",
            cat_list_no_all, index=1, key="price_cat"
        )
        
    if st.button("Calculate Cross-Price Elasticity", key="calc_cross"):
        if demand_cat == price_cat:
            st.error("Please select two different product categories to analyze.")
        else:
            with st.spinner(f"Analyzing relationship between '{demand_cat}' and '{price_cat}'..."):
                score = calculate_cross_price_elasticity(df, demand_category=demand_cat, price_category=price_cat)
                
                st.metric("Cross-Price Elasticity Score", value=f"{score:.2f}" if score is not None else "N/A")

                if score is not None:
                    if score > 0.1:
                        st.success(f"**Conclusion: These products are SUBSTITUTES.**\n\nAn increase in the price of '{price_cat}' is likely to **increase** the demand for '{demand_cat}'. Consider this when planning promotions.")
                    elif score < -0.1:
                        st.warning(f"**Conclusion: These products are COMPLEMENTS.**\n\nAn increase in the price of '{price_cat}' is likely to **decrease** the demand for '{demand_cat}'. They are often bought together.")
                    else:
                        st.info(f"**Conclusion: These products are UNRELATED.**\n\nChanging the price of '{price_cat}' has little to no predictable effect on the demand for '{demand_cat}'.")
                else:
                    st.error("Could not calculate a reliable score. There may not be enough overlapping sales data for these two categories on a weekly basis.")