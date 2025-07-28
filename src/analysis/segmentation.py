# src/analysis/segmentation.py

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

def perform_rfm_segmentation(df: pd.DataFrame, num_clusters: int = 4):
    """
    Performs customer segmentation using RFM analysis and K-Means clustering.

    Args:
        df (pd.DataFrame): The master dataframe.
        num_clusters (int): The number of customer segments to create.

    Returns:
        pd.DataFrame: A dataframe with customer_unique_id and their assigned segment.
    """
    # 1. Calculate RFM Features
    # Convert timestamp to datetime if not already
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    # Set the 'snapshot date' for recency calculation (one day after the last order)
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    # Aggregate data at the customer level
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda date: (snapshot_date - date.max()).days, # Recency
        'order_id': 'nunique', # Frequency
        'price': 'sum' # Monetary Value
    })

    # Rename the columns
    rfm_df.rename(columns={
        'order_purchase_timestamp': 'recency',
        'order_id': 'frequency',
        'price': 'monetary'
    }, inplace=True)

    # 2. Handle potential skew in the data (log transform) and scale features
    # Log transform helps normalize data with a wide range of values
    rfm_log = np.log1p(rfm_df) # log1p is log(1+x) to handle zero values
    
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)

    # 3. Apply K-Means Clustering
    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(rfm_scaled)
    
    # Assign the cluster label back to the original RFM dataframe
    rfm_df['customer_segment'] = kmeans.labels_
    
    # Return only the customer ID and their segment
    return rfm_df[['customer_segment']].reset_index()