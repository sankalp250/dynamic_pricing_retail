# src/data_processing/loader.py

import pandas as pd
import os

def load_and_prepare_data(data_path):
    """
    Loads all Olist CSVs, merges them into a single master dataframe,
    and performs cleaning and type conversions.

    Args:
        data_path (str): The path to the directory containing raw CSV files.

    Returns:
        pandas.DataFrame: The cleaned and merged master dataframe.
    """
    # 1. Load all necessary CSVs into pandas DataFrames
    files = {
        'customers': 'olist_customers_dataset.csv',
        'orders': 'olist_orders_dataset.csv',
        'order_items': 'olist_order_items_dataset.csv',
        'products': 'olist_products_dataset.csv',
        'translation': 'product_category_name_translation.csv'
    }

    data = {}
    for name, filename in files.items():
        data[name] = pd.read_csv(os.path.join(data_path, filename))

    # 2. Merge the dataframes
    # Merge orders with order_items
    df = pd.merge(data['orders'], data['order_items'], on='order_id', how='inner')
    
    # Merge with customers data
    df = pd.merge(df, data['customers'], on='customer_id', how='inner')
    
    # Merge with products data
    df = pd.merge(df, data['products'], on='product_id', how='inner')
    
    # Merge with category name translations for English names
    df = pd.merge(df, data['translation'], on='product_category_name', how='left')

    # 3. Clean and Transform the data
    # Select only the columns defined in our schema
    columns_to_keep = [
        'order_id', 'order_item_id', 'product_id', 'price', 'freight_value',
        'customer_id', 'order_purchase_timestamp', 'customer_unique_id',
        'customer_zip_code_prefix', 'customer_city', 'customer_state',
        'product_category_name_english'
    ]
    df = df[columns_to_keep]

    # Convert timestamp to datetime objects
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Handle missing product categories
    df['product_category_name_english'] = df['product_category_name_english'].fillna('Unknown')
    
    # Filter out orders with invalid prices
    df = df[df['price'] > 0]
    
    # For simplicity in this project, drop any remaining rows with missing values
    df.dropna(inplace=True)

    print("Data loading and preparation complete.")
    print(f"Final master dataframe shape: {df.shape}")
    
    return df