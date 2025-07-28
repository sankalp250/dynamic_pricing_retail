# streamlit_app/components/plots.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

# A decorator to cache the data, so we don't hit the database on every interaction.
# ttl=600 means the cache will expire after 600 seconds (10 minutes).
@st.cache_data(ttl=600)
def fetch_data_from_db(_engine):
    """
    Fetches the entire master_table from the database.
    The _engine parameter is used by st.cache_data to detect changes.
    """
    try:
        df = pd.read_sql('SELECT * FROM master_table', _engine)
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
        df['customer_segment'] = df['customer_segment'].astype('category')
        return df
    except Exception as e:
        st.error(f"Failed to fetch data from database: {e}")
        return pd.DataFrame()

def create_sales_overview_line_chart(df):
    """Creates a line chart of daily total sales."""
    daily_sales = df.set_index('order_purchase_timestamp').groupby(pd.Grouper(freq='D'))['price'].sum().reset_index()
    fig = px.line(daily_sales, x='order_purchase_timestamp', y='price', title='Daily Sales Revenue Over Time',
                  labels={'order_purchase_timestamp': 'Date', 'price': 'Total Revenue (R$)'})
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# (Keep the other functions in plots.py, just replace this one)
def create_segment_distribution_pie_chart(df):
    """Creates a pie chart showing the distribution of customer segments."""
    # Convert segment numbers to string type FIRST to avoid categorical errors
    df_copy = df.copy()
    df_copy['customer_segment'] = df_copy['customer_segment'].astype(str)

    segment_counts = df_copy['customer_segment'].value_counts().reset_index()
    segment_counts.columns = ['customer_segment', 'count']
    
    # Map using string keys, now that the column is string-based
    segment_names = {'0': 'Best Customers', '1': 'Loyal Customers', '2': 'At-Risk Customers', '3': 'New/Infrequent'}
    segment_counts['customer_segment'] = segment_counts['customer_segment'].map(segment_names).fillna('Unknown/NaN')
    
    fig = px.pie(segment_counts, names='customer_segment', values='count', 
                 title='Customer Segment Distribution',
                 hole=0.4,
                 color_discrete_sequence=px.colors.sequential.RdBu)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title_text='Segment'
    )
    return fig

def create_category_sales_bar_chart(df):
    """Creates a bar chart for sales by product category."""
    category_sales = df.groupby('product_category_name_english')['price'].sum().nlargest(15).sort_values(ascending=True).reset_index()
    fig = px.bar(category_sales, y='product_category_name_english', x='price', orientation='h',
                 title='Top 15 Product Categories by Sales Revenue',
                 labels={'product_category_name_english': 'Product Category', 'price': 'Total Revenue (R$)'})
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_price_elasticity_scatter_plot(df, category):
    """
    Creates an interactive scatter plot showing price vs. demand, with a regression line.
    """
    if category != 'All Products':
        df_filtered = df[df['product_category_name_english'] == category]
    else:
        df_filtered = df

    # Aggregate demand at each price point
    agg_df = df_filtered.groupby('price').agg(
        demand=('order_item_id', 'count')
    ).reset_index()

    if len(agg_df) < 5:
        return go.Figure().update_layout(
            title=f"Not enough data for '{category}'",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'
        )

    # Use log-log for regression to find elasticity, but plot the original scale for interpretability
    agg_df['log_price'] = np.log(agg_df['price'])
    agg_df['log_demand'] = np.log(agg_df['demand'])

    # Plot using original price/demand
    fig = px.scatter(agg_df, x='price', y='demand',
                     title=f'Price vs. Demand Curve for: {category}',
                     labels={'price': 'Unit Price (R$)', 'demand': 'Total Quantity Sold (Demand)'},
                     trendline='ols', # Ordinary Least Squares regression line
                     trendline_color_override='red')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_elasticity_comparison_bar_chart(df, elasticity_func):
    """
    Calculates elasticity for top N categories and displays them in a bar chart.
    """
    st.info("Calculating elasticity across all major categories... This may take a moment.")
    
    # Get top 20 categories by number of sales to avoid calculating on tiny categories
    top_categories = df['product_category_name_english'].value_counts().nlargest(20).index.tolist()
    
    elasticities = {}
    for cat in top_categories:
        # Pass the pre-filtered dataframe to the elasticity function
        cat_df = df[df['product_category_name_english'] == cat]
        score = elasticity_func(cat_df, product_category=cat)
        if score is not None:
            elasticities[cat] = score
            
    if not elasticities:
        st.warning("Could not calculate elasticities for enough categories to compare.")
        return go.Figure()

    elasticity_df = pd.DataFrame(list(elasticities.items()), columns=['Category', 'Elasticity']).sort_values('Elasticity')
    
    # Separate into elastic and inelastic
    elastic_df = elasticity_df[elasticity_df['Elasticity'] < -1].tail(10) # Most price sensitive
    inelastic_df = elasticity_df[elasticity_df['Elasticity'] > -1].head(10) # Least price sensitive
    
    comparison_df = pd.concat([elastic_df, inelastic_df])

    fig = px.bar(comparison_df, 
                 x='Elasticity', 
                 y='Category', 
                 orientation='h',
                 title='Price Elasticity Comparison: Most vs. Least Sensitive Categories',
                 color='Elasticity',
                 color_continuous_scale=px.colors.sequential.RdBu_r) # Red for elastic, Blue for inelastic

    fig.add_vline(x=-1, line_dash="dash", line_color="white", annotation_text="Unit Elasticity")

    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    return fig

import plotly.graph_objects as go

def create_rfm_summary_df(df):
    """
    Calculates the average Recency, Frequency, and Monetary value for each customer segment.
    """
    # 1. Calculate RFM values for each customer
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda date: (snapshot_date - date.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        'price': 'Monetary'
    })

    # 2. Merge with segment data
    # Ensure segments are treated as strings for merging and naming
    df_segments = df[['customer_unique_id', 'customer_segment']].drop_duplicates()
    df_segments['customer_segment'] = df_segments['customer_segment'].astype(str)

    rfm_with_segments = pd.merge(rfm_df, df_segments, on='customer_unique_id')

    # 3. Calculate the average for each metric, grouped by segment
    segment_summary = rfm_with_segments.groupby('customer_segment').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean'
    }).round(1).reset_index()

    # 4. Map the segment IDs to their meaningful names
    segment_names = {'0': 'Best Customers', '1': 'Loyal Customers', '2': 'At-Risk Customers', '3': 'New/Infrequent'}
    segment_summary['customer_segment'] = segment_summary['customer_segment'].map(segment_names)

    return segment_summary

def create_forecast_plot(model, forecast):
    """
    Creates a detailed forecast plot from a Prophet model and forecast dataframe.
    """
    fig = model.plot(forecast, xlabel='Date', ylabel='Revenue (R$)')
    
    # Customize with Plotly for a better look and feel
    # Find the lines and points in the figure
    lines = fig.get_lines()
    lines[0].set_color('black')      # Historical data points
    lines[1].set_color('#4F8BF9')    # Forecast line (yhat)
    
    # Fill the uncertainty interval
    ax = fig.gca()
    patches = [p for p in ax.get_children() if isinstance(p, go.Scatter) and p.fill == 'toself']
    if patches:
        fill_color = 'rgba(79, 139, 249, 0.2)'
        patches[0].update(fillcolor=fill_color)

    # Convert Matplotlib fig to Plotly fig for interactivity
    plotly_fig = go.Figure(data=fig.data)
    
    plotly_fig.update_layout(
        title="Sales Revenue Forecast with 95% Confidence Interval",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return plotly_fig