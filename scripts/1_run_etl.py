# scripts/1_run_etl.py

import sys
import os
import configparser
from sqlalchemy import types, text

# Adjust the path to import from the src directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_processing.loader import load_and_prepare_data
from src.database.utils import get_db_engine

def main():
    """Main ETL script to load, transform, and save data to MySQL."""
    print("Starting ETL process...")

    config = configparser.ConfigParser()
    config.read('config/config.ini')
    raw_data_path = config['data_paths']['raw_data_dir']
    
    master_df = load_and_prepare_data(raw_data_path)
    if master_df.empty:
        print("Data loading failed. Exiting.")
        return

    master_df['customer_segment'] = None 

    dtype_mapping = {
        'order_id': types.VARCHAR(length=255),
        'order_item_id': types.INTEGER,
        'product_id': types.VARCHAR(length=255),
        'price': types.DECIMAL(10, 2),
        'freight_value': types.DECIMAL(10, 2),
        'customer_id': types.VARCHAR(length=255),
        'order_purchase_timestamp': types.DATETIME,
        'customer_unique_id': types.VARCHAR(length=255),
        'customer_zip_code_prefix': types.INTEGER,
        'customer_city': types.VARCHAR(length=255),
        'customer_state': types.VARCHAR(length=50),
        'product_category_name_english': types.VARCHAR(length=255),
        'customer_segment': types.INTEGER
    }

    engine = get_db_engine()
    if not engine:
        return
        
    try:
        print("Loading data into master_table with explicit dtypes...")
        master_df.to_sql(
            name='master_table', 
            con=engine, 
            if_exists='replace', 
            index=False,
            dtype=dtype_mapping,
            chunksize=1000  
        )
        print("Data successfully loaded into 'master_table'.")

        # --- THE CLEANED UP AND CORRECTED BLOCK ---
        print("Setting primary key...")
        with engine.connect() as conn:
            # Execute the statement within the auto-begun transaction
            conn.execute(text('ALTER TABLE master_table ADD PRIMARY KEY (order_id, order_item_id);'))
            # Explicitly commit the transaction
            conn.commit()
        print("Primary key set successfully.")
        
        print("ETL process completed successfully!")
    
    except Exception as e:
        print(f"An error occurred during the ETL process: {e}")
    
    finally:
        if engine:
            engine.dispose()
            print("Database connection closed.")


if __name__ == "__main__":
    main()