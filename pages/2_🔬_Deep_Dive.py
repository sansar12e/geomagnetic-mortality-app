"""Deep Dive - Detailed analysis and visualizations."""
import streamlit as st
import pandas as pd
from utils.data_loader import load_preprocessed_data
from components.charts import (
    create_time_series_chart, 
    create_scatter_plot, 
    create_seasonal_chart,
    create_correlation_heatmap
)
from components.explanations import show_caveat_banner


st.set_page_config(page_title="Deep Dive Analysis", page_icon="🔬", layout="wide")

# Load data
data = load_preprocessed_data()
weekly_df = data['weekly']
monthly_df = data['monthly']
correlation_df = data['correlations']

st.title("🔬 Deep Dive Analysis")
st.markdown("### Detailed visualizations and temporal patterns")

# Outcome selector
outcome_map = {
    'Suicide': 'suicide',
    'Violence/Assault': 'violence',
    'Overdose': 'overdose',
    'Cardiovascular': 'cardiovascular'
}

selected_outcome_label = st.selectbox(
    "Select outcome to analyze:",
    options=list(outcome_map.keys()),
    index=0,
    help="Explore each outcome separately"
)

selected_outcome = outcome_map[selected_outcome_label]

show_caveat_banner(mode='compact')

# Section 1: Time Series
st.markdown(f"## Time Series: {selected_outcome_label} & Storm Activity")

# Option to show weekly or monthly
show_detail = st.checkbox("Show weekly detail (may be slower)", value=False)

if show_detail:
    st.info("Showing all 388 weekly data points...")
    fig = create_time_series_chart(weekly_df, outcome=selected_outcome, show_weekly=True)
else:
    st.info("Showing monthly aggregates for faster loading. Check box above for weekly detail.")
    fig = create_time_series_chart(monthly_df, outcome=selected_outcome, show_weekly=False)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
The solid line shows deaths; the dashed line shows storm activity (Kp index). 
Both variables exhibit seasonal variation and show weak covariation over time.
""")

st.divider()

# Section 2: Scatter Plot
st.markdown(f"## Scatter Plot: {selected_outcome_label}")

st.markdown("""
Each dot on this chart represents one week. The horizontal position shows how stormy 
that week (or the previous week) was, and the vertical position shows how many deaths occurred.
""")

# Option to show lagged relationship
show_lagged = st.checkbox(
    "Show lagged relationship (storms from 1 week prior)",
    value=False,
    help="This option plots deaths against storm activity from the previous week to test for delayed effects"
)

fig_scatter = create_scatter_plot(weekly_df, outcome=selected_outcome, use_lag=show_lagged)
st.plotly_chart(fig_scatter, use_container_width=True)

if show_lagged:
    st.info("""
    **Lagged relationship:** This chart shows deaths this week vs storm activity from last week.
    Biological effects, if present, may be delayed by several days.
    """)

st.markdown("""
**How to interpret this:**

- The **trendline** shows the overall relationship (upward slope indicates positive correlation)
- The **scatter** around the line shows substantial variability
- Many low-storm weeks had high deaths, and vice versa
- The **R² value** indicates storms explain only a small fraction (~4-5%) of the variation

Storm activity alone is a poor predictor of weekly deaths. Other factors account for 
most of the variation.
""")

st.divider()

# Section 3: Seasonality
st.markdown("## Seasonal Patterns")

fig_seasonal = create_seasonal_chart(weekly_df, outcome=selected_outcome)
st.plotly_chart(fig_seasonal, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Deaths by Month:**
    - Peak: Late spring/summer (May-July)
    - Low: Late fall (November-December)
    """)

with col2:
    st.markdown("""
    **Storm Activity by Month:**
    - Peaks: Equinoxes (March, September)
    - Low: Summer months
    """)

st.info("""
Seasonal patterns do not perfectly align. Deaths peak in summer; storms peak at equinoxes. 
Controlling for month, the correlation persists for suicide (r ≈ 0.22 after seasonal adjustment).
""")

st.divider()

# Section 4: Correlation Matrix
st.markdown("## Correlation Matrix")

st.markdown(f"""
This chart shows how strongly each geomagnetic metric correlates with {selected_outcome_label.lower()}:
""")

fig_corr = create_correlation_heatmap(correlation_df, outcome=selected_outcome)
st.plotly_chart(fig_corr, use_container_width=True)

with st.expander("📊 Compare with other outcomes"):
    st.markdown("### All Outcomes Combined")
    fig_all = create_correlation_heatmap(correlation_df, outcome=None)
    st.plotly_chart(fig_all, use_container_width=True)


st.divider()

# Section 5: Distribution Comparison
st.markdown("## Distribution Comparison")

from components.charts import create_distribution_comparison

threshold = st.slider(
    "Define 'storm week' as weeks with max Kp ≥",
    min_value=3.0,
    max_value=7.0,
    value=5.0,
    step=0.5,
    help="Adjust the threshold to see how it affects the comparison"
)

fig_dist = create_distribution_comparison(weekly_df, outcome=selected_outcome, threshold=threshold)
st.plotly_chart(fig_dist, use_container_width=True)

outcome_col = f'deaths_{selected_outcome}'
high_storm = weekly_df[weekly_df['weekly_max_Kp'] >= threshold][outcome_col]
low_storm = weekly_df[weekly_df['weekly_max_Kp'] < threshold][outcome_col]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Low Storm Weeks", len(low_storm), f"Mean: {low_storm.mean():.0f}")

with col2:
    st.metric("High Storm Weeks", len(high_storm), f"Mean: {high_storm.mean():.0f}")

with col3:
    diff = high_storm.mean() - low_storm.mean()
    st.metric("Difference", f"{diff:.1f} deaths")

st.markdown("""
Distributions overlap considerably. Storm weeks show slightly higher mean deaths, 
but substantial overlap indicates storm activity explains limited variance.
""")

# Footer
st.markdown("---")
st.caption("Deep Dive Analysis")

