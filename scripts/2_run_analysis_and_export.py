# scripts/2_run_analysis_and_export.py

import sys, os, pandas as pd, configparser
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database.utils import get_db_engine
from src.analysis.segmentation import perform_rfm_segmentation
from src.analysis.elasticity import calculate_elasticity_and_model
from numpy import mean # Import mean for aggregation

def main():
    """Main script to run analysis, update the database, and create exports for Tableau."""
    print("Starting analysis & export process...")
    engine = get_db_engine()
    if not engine: return
    
    # Load configuration to get the export path
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    export_path = config['data_paths']['tableau_exports_dir']
    
    # Ensure the export directory exists
    os.makedirs(export_path, exist_ok=True)
        
    try:
        print("Reading data from 'master_table'...")
        df = pd.read_sql('SELECT * FROM master_table', engine)
        if df.empty:
            print("Master table is empty. Run ETL first."); return

        # --- 1. Customer Segmentation Analysis ---
        print("\nPerforming RFM customer segmentation...")
        segments_df = perform_rfm_segmentation(df, num_clusters=4)
        
        # Merge segment labels back into the main dataframe
        if 'customer_segment' in df.columns: df.drop(columns=['customer_segment'], inplace=True)
        df = pd.merge(df, segments_df, on='customer_unique_id', how='left')

        # --- 2. Create and Export `segment_summary.csv` for Tableau ---
        print("Creating and exporting segment summary for Tableau...")
        snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
        rfm_raw = df.groupby('customer_unique_id').agg({
            'order_purchase_timestamp': lambda date: (snapshot_date - date.max()).days,
            'order_id': 'nunique',
            'price': 'sum',
            'customer_segment': 'first' # Get the assigned segment
        }).rename(columns={'order_purchase_timestamp': 'Recency', 'order_id': 'Frequency', 'price': 'Monetary'})
        
        # Aggregate by segment
        segment_summary = rfm_raw.groupby('customer_segment').agg(
            number_of_customers=('Monetary', 'count'),
            total_revenue=('Monetary', 'sum'),
            avg_recency=('Recency', 'mean'),
            avg_frequency=('Frequency', 'mean'),
            avg_monetary=('Monetary', 'mean')
        ).round(2).reset_index()

        # Map segment IDs to names for readability in Tableau
        segment_names = {0: 'Best Customers', 1: 'Loyal Customers', 2: 'At-Risk Customers', 3: 'New/Infrequent'}
        segment_summary['customer_segment'] = segment_summary['customer_segment'].map(segment_names)
        
        segment_summary.to_csv(os.path.join(export_path, 'segment_summary.csv'), index=False)
        print(f"✅ `segment_summary.csv` exported successfully to {export_path}")

        # --- 3. Create and Export `category_summary.csv` for Tableau ---
        print("\nCalculating elasticities and creating category summary for Tableau...")
        categories = df['product_category_name_english'].unique()
        elasticity_results = []

        for cat in categories:
            elasticity, _ = calculate_elasticity_and_model(df, product_category=cat)
            elasticity_results.append({'product_category': cat, 'price_elasticity': elasticity})

        elasticity_df = pd.DataFrame(elasticity_results)
        
        # Aggregate category sales data
        category_revenue = df.groupby('product_category_name_english').agg(
            total_revenue=('price', 'sum'),
            total_orders=('order_id', 'nunique'),
            avg_price=('price', 'mean')
        ).reset_index()
        
        # Merge elasticity scores with category sales data
        category_summary = pd.merge(category_revenue, elasticity_df, left_on='product_category_name_english', right_on='product_category', how='left')
        
        category_summary.to_csv(os.path.join(export_path, 'category_summary.csv'), index=False)
        print(f"✅ `category_summary.csv` exported successfully to {export_path}")

    except Exception as e:
        print(f"An error occurred during the analysis & export process: {e}")
    finally:
        engine.dispose()
        print("\nAnalysis & Export process finished.")

if __name__ == "__main__":
    main()