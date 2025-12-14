"""Overview Dashboard - Main findings and data summary."""
import streamlit as st
import pandas as pd
from utils.data_loader import load_preprocessed_data
from components.explanations import explain_kp_index, explain_p_value, show_methodology_summary
from components.statistics import format_p_value
from components.charts import create_comparison_bar_chart, create_multi_outcome_comparison


st.set_page_config(page_title="Overview Dashboard", page_icon="📊", layout="wide")

# Load data
data = load_preprocessed_data()
summary_stats = data['summary_stats']
correlation_df = data['correlations']

st.title("📊 Overview Dashboard")
st.markdown("### Detailed look at the data and statistical findings")

# Outcome selector
outcome_map = {
    'Suicide': 'suicide',
    'Violence/Assault': 'violence',
    'Overdose': 'overdose',
    'Cardiovascular': 'cardiovascular'
}

selected_outcome_label = st.selectbox(
    "Select outcome to view:",
    options=list(outcome_map.keys()),
    index=0,
    help="Suicide is the primary behavioral outcome"
)

selected_outcome = outcome_map[selected_outcome_label]

st.divider()

# Section 1: Data at a Glance
st.markdown("## Data at a Glance")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Mortality Data: {selected_outcome_label}")
    st.metric("📅 Weeks analyzed", summary_stats['n_weeks'])
    st.metric("📍 Geographic scope", "United States (national)")
    st.metric("📈 Mean deaths/week", f"{summary_stats['outcomes'][selected_outcome]['mean']:.0f}")
    st.metric("📊 Range", f"{summary_stats['outcomes'][selected_outcome]['min']} - {summary_stats['outcomes'][selected_outcome]['max']}")
    st.metric("📏 Std deviation", f"{summary_stats['outcomes'][selected_outcome]['std']:.1f}")

with col2:
    st.markdown("### Geomagnetic Storm Data")
    st.metric("🌐 Measurements", f"{summary_stats['n_measurements']:,}")
    st.metric("📡 Source", "GFZ Potsdam")
    st.metric("⚡ Mean Kp", f"{summary_stats['geomagnetic']['mean_Kp']:.2f}")
    st.metric("🔴 Max Kp observed", f"{summary_stats['geomagnetic']['max_Kp_overall']:.1f}")
    st.metric("📅 Date range", f"{summary_stats['date_range']['start']} to {summary_stats['date_range']['end']}")

st.divider()

# Section 2: What is a Geomagnetic Storm?
st.markdown("## Understanding Geomagnetic Storms")
explain_kp_index()

# Visual representation of Kp scale
st.markdown("""
```
Kp Index Scale:
0-1: Quiet      ██                    (Most common)
2-3: Unsettled  ████                  (Elevated activity)
4:   Active     ██████                (Minor disturbances)
5+:  STORM      ████████              ← We count these as "storm weeks"
7+:  Strong     ██████████            (Can affect power grids)
9:   Extreme    ████████████          (Rare, severe impacts)
```
""")

st.info(f"""
During our study period (2018-2025), there were about **{summary_stats['storm_comparison']['storm_weeks_count']} weeks 
with at least one storm interval** (Kp ≥ 5), compared to **{summary_stats['storm_comparison']['no_storm_weeks_count']} 
quiet weeks**.
""")

st.divider()

# Section 3: Correlation Results
st.markdown("## Correlation Results")

st.markdown(f"### {selected_outcome_label}")

# Filter correlations for selected outcome
outcome_corrs = [c for c in summary_stats['all_correlations'] if c['outcome'] == selected_outcome]

# Separate same-week and lagged
same_week_corrs = [c for c in outcome_corrs if c.get('lag') == 'same-week']
lag1_corrs = [c for c in outcome_corrs if c.get('lag') == 'lag-1']

# Display option
display_mode = st.radio(
    "Show:",
    options=["Same-week effects", "Lagged effects (1 week prior)", "Both"],
    index=2,
    horizontal=True,
    help="Lagged effects measure storms from the previous week"
)

if display_mode == "Same-week effects":
    corrs_to_show = same_week_corrs
elif display_mode == "Lagged effects (1 week prior)":
    corrs_to_show = lag1_corrs
else:
    corrs_to_show = outcome_corrs

corr_display = pd.DataFrame({
    'Metric': [c['metric'] for c in corrs_to_show],
    'Timing': [c.get('lag', 'same-week') for c in corrs_to_show],
    'Correlation (r)': [f"{c['pearson_r']:.3f}" for c in corrs_to_show],
    'R² (%)': [f"{c['r_squared']*100:.1f}%" for c in corrs_to_show],
    'p-value': [format_p_value(c['pearson_p']) for c in corrs_to_show],
    'Significant?': ['✅ Yes' if c['significant'] else '❌ No' for c in corrs_to_show]
})

st.dataframe(corr_display, use_container_width=True, hide_index=True)

st.info("""
**About lagged effects:** Lagged correlations test whether storm activity from the previous 
week correlates with deaths this week. This tests for potential delayed effects.
""")

# Add comparison table for all outcomes
with st.expander("📊 Compare correlations across all outcomes"):
    st.markdown("### All Outcomes: Strongest Correlations")
    
    comparison_data = []
    for outcome_key in ['suicide', 'violence', 'overdose', 'cardiovascular']:
        if outcome_key in summary_stats['strongest_correlations']:
            corr_overall = summary_stats['strongest_correlations'][outcome_key]['overall']
            comparison_data.append({
                'Outcome': outcome_key.capitalize(),
                'Strongest Metric': corr_overall['metric'],
                'Timing': corr_overall['lag'],
                'Correlation (r)': f"{corr_overall['pearson_r']:.3f}",
                'R² (%)': f"{corr_overall['r_squared']*100:.1f}%",
                'p-value': format_p_value(corr_overall['pearson_p'])
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Add visual comparison chart
    fig_multi = create_multi_outcome_comparison(summary_stats)
    st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown("""
    **Summary:**
    - Suicide shows strongest positive correlation
    - Violence and Cardiovascular show negative (inverse) correlations
    - Overdose shows no significant correlation

    Mixed patterns suggest outcome-specific mechanisms. See landing page for detailed interpretation.
    """)

# Explanation box
st.markdown("### How to Read This Table")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Correlation (r)**
    
    How strongly two things move together. 
    - Ranges from -1 to +1
    - Our values (~0.1-0.2) are "weak positive"
    - Means slight tendency to move together
    """)

with col2:
    st.markdown("""
    **R² (%)**
    
    Percentage of variation explained.
    - Shows how much of the variation in deaths can be explained by storms
    - Our values (~2-5%) are quite small
    - Means most variation comes from other factors
    """)

with col3:
    st.markdown("""
    **p-value**
    
    Probability this is random chance.
    - Below 0.05 = statistically significant
    - Our p-values are mostly < 0.001
    - Unlikely to be random, but doesn't mean large effect
    """)

explain_p_value()

st.success("""
**Key insight:** The correlations are *statistically significant* (unlikely to be 
random) but *small in magnitude* (storms explain only ~2-5% of variation in deaths).
""")

st.divider()

# Section 4: Group Comparison
st.markdown(f"## Storm vs Quiet Weeks: {selected_outcome_label}")

comp_data = summary_stats['outcome_comparisons'][selected_outcome]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Quiet Weeks",
        f"{summary_stats['storm_comparison']['no_storm_weeks_count']}",
        help="Weeks with no Kp ≥ 5 intervals"
    )
    st.metric(
        "Mean Deaths",
        f"{comp_data['no_storm_weeks_mean']:.0f}"
    )

with col2:
    st.metric(
        "Storm Weeks",
        f"{summary_stats['storm_comparison']['storm_weeks_count']}",
        help="Weeks with at least one Kp ≥ 5 interval"
    )
    st.metric(
        "Mean Deaths",
        f"{comp_data['storm_weeks_mean']:.0f}"
    )

with col3:
    diff = comp_data['difference']
    pct_diff = (abs(diff) / comp_data['no_storm_weeks_mean']) * 100 if comp_data['no_storm_weeks_mean'] > 0 else 0
    st.metric(
        "Difference",
        f"{abs(diff):.1f} deaths",
        delta=f"{pct_diff:.1f}% {'increase' if diff > 0 else 'decrease'}"
    )

# Add bar chart visualization
fig_comparison = create_comparison_bar_chart(
    storm_mean=comp_data['storm_weeks_mean'],
    no_storm_mean=comp_data['no_storm_weeks_mean'],
    outcome=selected_outcome
)
st.plotly_chart(fig_comparison, use_container_width=True)

st.divider()

# Methodology
st.markdown("## 📚 Methodology")
show_methodology_summary()

# Footer
st.markdown("---")
st.caption("Overview Dashboard")

