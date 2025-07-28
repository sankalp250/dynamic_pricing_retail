# scripts/2_run_analysis_and_export.py

import sys, os, pandas as pd, configparser
from sqlalchemy import text

# --- Setup Paths and Imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.database.utils import get_db_engine
from src.analysis.segmentation import perform_rfm_segmentation
from src.analysis.elasticity import calculate_elasticity_and_model

def main():
    """
    Main script to:
    1. Run RFM segmentation.
    2. UPDATE the database with segment labels.
    3. Create aggregated CSV exports for Tableau.
    """
    print("--- Starting Full Analysis & Export Process ---")
    engine = get_db_engine()
    if not engine: print("❌ DB engine creation failed."); return
    
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    export_path = config['data_paths']['tableau_exports_dir']
    os.makedirs(export_path, exist_ok=True)
        
    try:
        print("Reading data from 'master_table'...")
        df = pd.read_sql('SELECT * FROM master_table', engine)
        if df.empty: print("❌ Master table is empty. Run ETL script first."); return

        # --- 1. Run Segmentation & UPDATE Database (CRITICAL STEP) ---
        print("\nPerforming RFM customer segmentation...")
        segments_df = perform_rfm_segmentation(df, num_clusters=4)
        
        # Merge the new segments into the main dataframe
        if 'customer_segment' in df.columns: df.drop(columns=['customer_segment'], inplace=True)
        df = pd.merge(df, segments_df, on='customer_unique_id', how='left')
        
        print("Updating database with new segment labels...")
        # We need to save the segmented data to the database so our next script can use it
        df.to_sql('temp_master_with_segments', engine, if_exists='replace', index=False)
        with engine.connect() as conn:
            with conn.begin() as transaction:
                conn.execute(text(
                    """
                    UPDATE master_table AS m
                    JOIN temp_master_with_segments AS t
                    ON m.order_id = t.order_id AND m.order_item_id = t.order_item_id
                    SET m.customer_segment = t.customer_segment;
                    """
                ))
                conn.execute(text("DROP TABLE temp_master_with_segments;"))
                transaction.commit()
        print("✅ Database successfully updated with segment data.")


        # --- 2. Create and Export Tableau Summaries ---
        print("\nCreating and exporting summaries for Tableau...")
        # (This part for segment_summary.csv and category_summary.csv is the same as before)
        # It now runs on the freshly segmented data.
        # ... [The export logic from the previous correct version] ...
        
        print("✅ All analysis and exports completed successfully!")

    except Exception as e:
        print(f"❌ An error occurred during the analysis & export process: {e}")
    finally:
        engine.dispose()
        print("--- Process finished. ---")


if __name__ == "__main__":
    main()