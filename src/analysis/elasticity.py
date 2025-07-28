# src/analysis/elasticity.py

import pandas as pd
import statsmodels.api as sm
import numpy as np

def calculate_elasticity_and_model(df: pd.DataFrame, product_category: str = 'all'):
    """
    Calculates price elasticity using a log-log model and returns the trained model.

    Args:
        df (pd.DataFrame): The master dataframe.
        product_category (str): The category to analyze. 'all' for the whole dataset.

    Returns:
        tuple: (elasticity_score, trained_model). Returns (None, None) if calculation fails.
    """
    if product_category != 'all':
        df_filtered = df[df['product_category_name_english'] == product_category].copy()
    else:
        df_filtered = df.copy()

    # Aggregate to get price vs. demand (quantity sold)
    agg_df = df_filtered.groupby('price').agg(
        demand=('order_item_id', 'count')
    ).reset_index()

    # Need at least 10 unique price points for a meaningful regression
    if len(agg_df) < 10:
        print(f"Warning: Not enough unique price points for '{product_category}' to build a model.")
        return None, None

    # Apply the log-log transformation
    agg_df['log_price'] = np.log(agg_df['price'])
    agg_df['log_demand'] = np.log(agg_df['demand'])

    # Build and fit the regression model
    X = agg_df['log_price']
    y = agg_df['log_demand']
    X = sm.add_constant(X)  # Add intercept
    
    model = sm.OLS(y, X).fit()

    # The coefficient for log_price is our elasticity
    price_elasticity = model.params.get('log_price', None)

    return price_elasticity, model