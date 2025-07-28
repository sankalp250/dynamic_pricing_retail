# src/analysis/forecasting.py

import pandas as pd
from prophet import Prophet

# Make sure your function definition looks EXACTLY like this line:
def generate_forecast(df: pd.DataFrame, periods: int = 90, freq: str = 'D', product_category: str = 'all'):
    """
    Generates a future sales forecast using Prophet, for either all products or a specific category.
    """
    # Filter by product category if specified
    if product_category != 'all':
        df_filtered = df[df['product_category_name_english'] == product_category].copy()
        if df_filtered.empty:
            print(f"Warning: No data found for category '{product_category}'.")
            return None, None
    else:
        df_filtered = df.copy()

    # Prepare data for Prophet
    daily_sales = df_filtered.set_index('order_purchase_timestamp').groupby(pd.Grouper(freq='D'))['price'].sum().reset_index()
    daily_sales.rename(columns={'order_purchase_timestamp': 'ds', 'price': 'y'}, inplace=True)
    
    if len(daily_sales) < 60:
        print(f"Warning: Not enough historical data for '{product_category}' to generate a reliable forecast.")
        return None, None
        
    # Initialize and fit the Prophet model
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False, interval_width=0.95)
    model.fit(daily_sales)
    
    # Create a future dataframe and make predictions
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    
    print(f"Forecast generated for '{product_category}' for the next {periods} days.")
    
    return model, forecast