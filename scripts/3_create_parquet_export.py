# scripts/3_create_parquet_export.py

import sys, os, pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database.utils import get_db_engine

def main():
    """
    Reads the fully processed master_table from the local database
    and saves it to a single, efficient Parquet file for the Streamlit app.
    """
    print("--- Starting export to Parquet process ---")

    # Connect to your LOCAL MySQL database
    engine = get_db_engine()
    if not engine:
        print("❌ Could not connect to the local database. Ensure your config.ini is pointing to localhost.")
        return

    # Read the entire table, which should already be segmented.
    print("Reading data from 'master_table'...")
    try:
        df = pd.read_sql('SELECT * FROM master_table', engine)
    except Exception as e:
        print(f"❌ Failed to read from master_table: {e}")
        return
    finally:
        engine.dispose()
    
    if df.empty or 'customer_segment' not in df.columns or df['customer_segment'].isnull().all():
        print("❌ Data is incomplete. Please run scripts 1 and 2 pointed at your LOCAL database first.")
        return
        
    # Define the output path
    output_dir = "streamlit_app/data" # We'll create a new data folder inside the app
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "master_data.parquet")
    
    # Save to Parquet
    df.to_parquet(output_path, index=False)
    
    print(f"\n✅ Successfully exported {len(df)} rows to {output_path}")
    print("--- The app is now ready to run in self-contained mode. ---")


if __name__ == "__main__":
    main()