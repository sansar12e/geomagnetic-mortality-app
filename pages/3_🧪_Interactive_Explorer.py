"""Interactive Explorer - User-customizable analysis."""
import streamlit as st
import pandas as pd
from utils.data_loader import load_weekly_data
from components.charts import create_scatter_plot, create_distribution_comparison
from components.statistics import compute_correlation, compare_groups, format_p_value


st.set_page_config(page_title="Interactive Explorer", page_icon="🧪", layout="wide")

st.title("Interactive Explorer")
st.markdown("### Customize analysis parameters")

# Load data
weekly_df = load_weekly_data()

st.divider()

# Section 1: Filter Data
st.markdown("## Customize Analysis")

# Outcome selector (first control)
outcome_map = {
    'Suicide': 'suicide',
    'Violence/Assault': 'violence',
    'Overdose': 'overdose',
    'Cardiovascular': 'cardiovascular'
}

selected_outcome_label = st.selectbox(
    "Select outcome:",
    options=list(outcome_map.keys()),
    index=0,
    help="Choose which health outcome to analyze"
)

selected_outcome = outcome_map[selected_outcome_label]
y_col_base = f'deaths_{selected_outcome}'

col1, col2 = st.columns(2)

with col1:
    # Year range filter
    min_year = int(weekly_df['year'].min())
    max_year = int(weekly_df['year'].max())
    
    year_range = st.slider(
        "Select years to analyze:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        help="Narrow down to specific years to see if patterns change over time"
    )
    
    # Metric selection
    storm_metric_map = {
        'Weekly Mean Kp': 'weekly_mean_Kp',
        'Weekly Mean Ap': 'weekly_mean_ap',
        'Weekly Sum Ap': 'weekly_sum_ap',
        'Weekly Max Kp': 'weekly_max_Kp',
        'Storm Count (Kp≥5)': 'storm_count_Kp5'
    }
    
    storm_metric_display = st.selectbox(
        "Storm metric to use:",
        options=list(storm_metric_map.keys()),
        help="Different ways to measure 'how stormy' a week was"
    )
    
    storm_metric = storm_metric_map[storm_metric_display]

with col2:
    # Seasonal adjustment
    remove_seasonality = st.checkbox(
        "Remove seasonal patterns?",
        value=False,
        help="Subtract monthly averages to focus on week-to-week variation"
    )
    
    # Confidence interval
    show_confidence = st.checkbox(
        "Show additional statistics?",
        value=True,
        help="Display more detailed statistical information"
    )

# Filter data
filtered_df = weekly_df[
    (weekly_df['year'] >= year_range[0]) & 
    (weekly_df['year'] <= year_range[1])
].copy()

# Apply seasonal adjustment if requested
if remove_seasonality:
    from components.statistics import compute_seasonal_adjustment
    filtered_df = compute_seasonal_adjustment(filtered_df, 'week_end', y_col_base)
    filtered_df.rename(columns={'adjusted': f'{y_col_base}_adjusted'}, inplace=True)
    filtered_df = compute_seasonal_adjustment(filtered_df, 'week_end', storm_metric)
    filtered_df.rename(columns={'adjusted': f'{storm_metric}_adjusted'}, inplace=True)
    x_col = f'{storm_metric}_adjusted'
    y_col = f'{y_col_base}_adjusted'
else:
    x_col = storm_metric
    y_col = y_col_base

st.divider()

# Section 2: Results
st.markdown("## Results")

st.info(f"Analyzing **{len(filtered_df)} weeks** from **{year_range[0]} to {year_range[1]}** using **{storm_metric_display}**")

# Compute correlation
corr_results = compute_correlation(filtered_df, x_col, y_col)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Correlation (r)",
        f"{corr_results['pearson_r']:.3f}",
        help="Pearson correlation coefficient"
    )

with col2:
    st.metric(
        "R² (%)",
        f"{corr_results['pearson_r_squared']*100:.1f}%",
        help="Percentage of variation explained"
    )

with col3:
    st.metric(
        "p-value",
        format_p_value(corr_results['pearson_p']),
        help="Statistical significance"
    )

with col4:
    is_sig = "✅ Yes" if corr_results['pearson_p'] < 0.05 else "❌ No"
    st.metric(
        "Significant?",
        is_sig,
        help="Is p < 0.05?"
    )

if show_confidence:
    st.markdown("### Additional Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
**Pearson Correlation:**
- r = {corr_results['pearson_r']:.3f}
- R² = {corr_results['pearson_r_squared']:.3f}
- p = {format_p_value(corr_results['pearson_p'])}
- n = {corr_results['n']} weeks
""")

    with col2:
        st.markdown(f"""
**Spearman Correlation (rank-based):**
- ρ = {corr_results['spearman_r']:.3f}
- p = {format_p_value(corr_results['spearman_p'])}
- More robust to outliers
""")

# Scatter plot
st.markdown("### Scatter Plot")
fig = create_scatter_plot(filtered_df, outcome=selected_outcome, x_col=x_col, y_col=y_col)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Section 3: Compare Groups
st.markdown("## Compare High vs Low Storm Weeks")

# Calculate percentiles for suggested thresholds
p25 = float(filtered_df[storm_metric].quantile(0.25))
p50 = float(filtered_df[storm_metric].quantile(0.50))
p75 = float(filtered_df[storm_metric].quantile(0.75))

st.info(f"""
**💡 Suggested thresholds for {storm_metric_display}:**  
25th percentile: {p25:.2f} | Median: {p50:.2f} | 75th percentile: {p75:.2f}
""")

threshold = st.slider(
    "Define 'high storm' as weeks with storm metric ≥",
    min_value=float(filtered_df[storm_metric].min()),
    max_value=float(filtered_df[storm_metric].max()),
    value=float(filtered_df[storm_metric].median()),
    help="Adjust threshold to compare different groups. Use suggested values for balanced sample sizes."
)

# Show preview of split
preview_low = len(filtered_df[filtered_df[storm_metric] < threshold])
preview_high = len(filtered_df[filtered_df[storm_metric] >= threshold])
st.caption(f"Current split: **{preview_low} low** vs **{preview_high} high** storm weeks")

# Compare groups
group_results = compare_groups(filtered_df, storm_metric, threshold, y_col_base)

# Show sample size preview and warnings
low_n = group_results['low_n']
high_n = group_results['high_n']

# Warning for inadequate sample sizes
if high_n < 10 or low_n < 10:
    st.error(f"""
    ⚠️ **Sample size too small for reliable inference!**  
    Low storm: {low_n} weeks | High storm: {high_n} weeks
    
    **Recommendation:** Use a threshold that gives at least 10 weeks in each group.  
    Try the suggested percentile values above for more balanced groups.
    """)
elif high_n < 30 or low_n < 30:
    st.warning(f"""
    ⚠️ **Small sample size warning:**  
    Low storm: {low_n} weeks | High storm: {high_n} weeks
    
    Statistical tests may be less reliable with fewer than 30 observations per group.
    Consider using a more moderate threshold for more robust results.
    """)
else:
    st.success(f"""
    ✅ **Adequate sample sizes:**  
    Low storm: {low_n} weeks | High storm: {high_n} weeks
    """)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Low Storm Weeks",
        f"{group_results['low_n']}",
        f"Mean: {group_results['low_mean']:.0f}"
    )
    st.caption(f"Std: {group_results['low_std']:.1f}")

with col2:
    st.metric(
        "High Storm Weeks",
        f"{group_results['high_n']}",
        f"Mean: {group_results['high_mean']:.0f}"
    )
    st.caption(f"Std: {group_results['high_std']:.1f}")

with col3:
    st.metric(
        "Difference (deaths/week)",
        f"{group_results['difference']:.1f}",
        delta=f"{(group_results['difference']/group_results['low_mean']*100):.1f}%"
    )
    st.caption(f"p = {format_p_value(group_results['p_value'])}")

if show_confidence:
    st.markdown("""
    ### Statistical Test Results
    """)
    
    reliability_note = ""
    if high_n < 10 or low_n < 10:
        reliability_note = "\n\n⚠️ **Warning:** With fewer than 10 observations in a group, these statistics are highly unreliable and should not be interpreted."
    elif high_n < 30 or low_n < 30:
        reliability_note = "\n\n⚠️ **Note:** With fewer than 30 observations per group, statistical power is limited and results should be interpreted cautiously."
    
    st.markdown(f"""
- **t-statistic:** {group_results['t_statistic']:.2f}
- **p-value:** {format_p_value(group_results['p_value'])}
- **Cohen's d:** {group_results['cohens_d']:.3f} (effect size)

**Interpretation:** Cohen's d values: 0.2 = small, 0.5 = medium, 0.8 = large effect.
Our effect size of {group_results['cohens_d']:.2f} is {'small' if abs(group_results['cohens_d']) < 0.5 else 'medium' if abs(group_results['cohens_d']) < 0.8 else 'large'}.{reliability_note}
""")

# Distribution comparison
fig_dist = create_distribution_comparison(filtered_df, outcome=selected_outcome, threshold=threshold, storm_metric=storm_metric)
st.plotly_chart(fig_dist, use_container_width=True)

st.divider()

# Section 4: Data Table
st.markdown("## Data Table")

if st.checkbox("Show data table"):
    display_cols = ['year', 'week_num', 'week_end', y_col_base, storm_metric]
    st.dataframe(
        filtered_df[display_cols].sort_values('week_end', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df[display_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name=f"geomagnetic_{selected_outcome}_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("Interactive Explorer")

