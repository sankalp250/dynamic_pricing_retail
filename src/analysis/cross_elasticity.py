# src/analysis/cross_elasticity.py

import pandas as pd
import statsmodels.api as sm
import numpy as np

def calculate_cross_price_elasticity(df: pd.DataFrame, demand_category: str, price_category: str):
    """
    Calculates the cross-price elasticity between two product categories.
    This measures the effect of the price of 'price_category' on the demand for 'demand_category'.

    Args:
        df (pd.DataFrame): The master dataframe.
        demand_category (str): The product category whose demand is being measured.
        price_category (str): The product category whose price is changing.

    Returns:
        float: The calculated cross-price elasticity coefficient. Returns None if fails.
    """
    if demand_category == price_category:
        return None # This is own-price elasticity, not cross-price.

    # 1. Isolate the data for each category
    df_demand_cat = df[df['product_category_name_english'] == demand_category]
    df_price_cat = df[df['product_category_name_english'] == price_category]

    if df_demand_cat.empty or df_price_cat.empty:
        print(f"Warning: Not enough data for one of the categories.")
        return None
    
    # 2. Aggregate data by week to align them
    # For demand category: sum of quantity sold (demand) per week
    weekly_demand = df_demand_cat.set_index('order_purchase_timestamp') \
                                 .resample('W') \
                                 .agg(demand=('order_item_id', 'count'))

    # For price category: average price per week
    weekly_price = df_price_cat.set_index('order_purchase_timestamp') \
                               .resample('W') \
                               .agg(avg_price=('price', 'mean'))

    # 3. Merge the two weekly datasets
    merged_weekly = pd.merge(weekly_demand, weekly_price, on='order_purchase_timestamp', how='inner')
    
    # Drop any weeks where there were no sales or prices recorded
    merged_weekly.dropna(inplace=True)
    merged_weekly = merged_weekly[(merged_weekly['demand'] > 0) & (merged_weekly['avg_price'] > 0)]

    # Need at least 15 weeks of overlapping data for a meaningful regression
    if len(merged_weekly) < 15:
        print("Warning: Not enough overlapping weekly data to calculate cross-price elasticity reliably.")
        return None

    # 4. Apply Log-Log model
    merged_weekly['log_demand'] = np.log(merged_weekly['demand'])
    merged_weekly['log_price'] = np.log(merged_weekly['avg_price'])
    
    y = merged_weekly['log_demand']
    X = merged_weekly['log_price']
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X).fit()
    
    # The coefficient of the log_price is our cross-price elasticity
    cross_elasticity_score = model.params.get('log_price', None)
    
    return cross_elasticity_score