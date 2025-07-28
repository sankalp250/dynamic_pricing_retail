import streamlit as st

def create_kpi_card(title, value, delta=None):
    """
    Creates a styled KPI card using HTML and CSS.
    """
    delta_html = ""
    if delta:
        delta_html = f'<p class="metric-delta">{delta}</p>'

    # The stray ``` at the end of the original code has been removed.
    st.markdown(f'''
    <div class="metric-card">
        <h3 class="metric-title">{title}</h3>
        <p class="metric-value">{value}</p>
        {delta_html}
    </div>
    ''', unsafe_allow_html=True)