"""Reusable chart functions for the Streamlit app."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st


# Color palette
COLORS = {
    'deaths': '#2E86AB',      # Steel blue (legacy, for backward compatibility)
    'storms': '#E94F37',      # Coral red
    'significant': '#28A745', # Green
    'not_significant': '#6C757D',  # Gray
    'warning': '#FFC107',     # Amber
}

# Outcome-specific colors
OUTCOME_COLORS = {
    'suicide': '#2E86AB',           # Steel blue (primary outcome)
    'violence': '#E94F37',          # Coral red
    'overdose': '#8E44AD',          # Purple
    'cardiovascular': '#27AE60',    # Green
}


def create_comparison_bar_chart(storm_mean, no_storm_mean, outcome='suicide'):
    """Create simple bar chart comparing storm vs non-storm weeks.
    
    Args:
        storm_mean: Mean deaths during storm weeks
        no_storm_mean: Mean deaths during non-storm weeks
        outcome: One of 'suicide', 'violence', 'overdose', 'cardiovascular'
    """
    # Outcome labels for display
    outcome_labels = {
        'suicide': 'Suicide Deaths',
        'violence': 'Violence/Assault Deaths',
        'overdose': 'Overdose Deaths',
        'cardiovascular': 'Cardiovascular Deaths'
    }
    
    fig = go.Figure()
    
    categories = ['Quiet Weeks<br>(no storms)', 'Storm Weeks<br>(Kp ≥ 5)']
    values = [no_storm_mean, storm_mean]
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=[OUTCOME_COLORS.get(outcome, COLORS['deaths']), COLORS['storms']],
        text=[f"{v:.0f}" for v in values],
        textposition='outside',
    ))
    
    fig.update_layout(
        title=f"Average Weekly {outcome_labels.get(outcome, 'Deaths')}: Storm vs Quiet Weeks",
        yaxis_title="Deaths per Week",
        height=400,
        showlegend=False,
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#000000')
    )
    
    return fig


def create_scatter_plot(df, outcome='suicide', x_col='weekly_mean_Kp', y_col=None, use_lag=False):
    """Create scatter plot with trendline for a specific outcome.
    
    Args:
        df: Dataframe with weekly data
        outcome: One of 'suicide', 'violence', 'overdose', 'cardiovascular'
        x_col: Column name for x-axis (geomagnetic metric)
        y_col: Column name for y-axis (if None, uses deaths_{outcome})
        use_lag: If True, use lagged version of x_col (storms from previous week)
    """
    if y_col is None:
        y_col = f'deaths_{outcome}'
    
    # If using lag, modify x_col to use lagged version
    if use_lag and not x_col.endswith('_lag1'):
        x_col_display = x_col
        x_col = f'{x_col}_lag1'
        lag_text = " (1 week prior)"
    else:
        x_col_display = x_col.replace('_lag1', '')
        lag_text = " (1 week prior)" if x_col.endswith('_lag1') else ""
    
    # Outcome labels for display
    outcome_labels = {
        'suicide': 'Suicide Deaths',
        'violence': 'Violence/Assault Deaths',
        'overdose': 'Overdose Deaths',
        'cardiovascular': 'Cardiovascular Deaths'
    }
    
    # Check if column exists
    if x_col not in df.columns:
        # Fall back to non-lagged version
        x_col = x_col.replace('_lag1', '')
        lag_text = ""
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        trendline='ols',
        opacity=0.6,
        labels={
            x_col: f'Storm Index (Kp){lag_text}',
            y_col: f'Weekly {outcome_labels.get(outcome, "Deaths")}'
        },
        title=f'Storm Activity{lag_text} vs {outcome_labels.get(outcome, "Deaths")} (n={len(df)} weeks)'
    )

    fig.update_layout(
        template='plotly_white',
        height=500
    )
    
    # Get R² from trendline
    results = px.get_trendline_results(fig)
    if len(results) > 0:
        r_squared = results.iloc[0]['px_fit_results'].rsquared
        
        annotation_text = f"R² = {r_squared:.3f}"
        if lag_text:
            annotation_text += "\n(Storms from previous week)"
        
        fig.add_annotation(
            text=annotation_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(size=11, color='black'),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
            borderpad=4
        )
    
    fig.update_traces(marker=dict(color=OUTCOME_COLORS.get(outcome, COLORS['deaths'])))
    
    return fig


def create_time_series_chart(df, outcome='suicide', show_weekly=False):
    """Create time series chart showing deaths and storm activity over time.
    
    Args:
        df: Dataframe with weekly or monthly data
        outcome: One of 'suicide', 'violence', 'overdose', 'cardiovascular'
        show_weekly: Whether showing weekly (True) or monthly (False) data
    """
    outcome_col = f'deaths_{outcome}'
    
    # Outcome labels for display
    outcome_labels = {
        'suicide': 'Suicide Deaths',
        'violence': 'Violence/Assault Deaths',
        'overdose': 'Overdose Deaths',
        'cardiovascular': 'Cardiovascular Deaths'
    }
    
    fig = go.Figure()
    
    # Deaths line
    fig.add_trace(go.Scatter(
        x=df['week_end'] if 'week_end' in df.columns else df['year_month'],
        y=df[outcome_col],
        name=outcome_labels.get(outcome, 'Deaths'),
        line=dict(color=OUTCOME_COLORS.get(outcome, COLORS['deaths']), width=2),
        yaxis='y1'
    ))
    
    # Storm activity line
    storm_col = 'weekly_mean_Kp' if 'weekly_mean_Kp' in df.columns else 'weekly_mean_Kp'
    fig.add_trace(go.Scatter(
        x=df['week_end'] if 'week_end' in df.columns else df['year_month'],
        y=df[storm_col],
        name='Storm Index (Kp)',
        line=dict(color=COLORS['storms'], width=2, dash='dash'),
        yaxis='y2'
    ))
    
    # Layout with dual y-axes
    fig.update_layout(
        title=f"{outcome_labels.get(outcome, 'Deaths')} and Storm Activity Over Time",
        xaxis=dict(title="Date"),
        yaxis=dict(
            title=f"Weekly {outcome_labels.get(outcome, 'Deaths')}",
            title_font=dict(color=OUTCOME_COLORS.get(outcome, COLORS['deaths'])),
            tickfont=dict(color=OUTCOME_COLORS.get(outcome, COLORS['deaths']))
        ),
        yaxis2=dict(
            title="Storm Index (Kp)",
            title_font=dict(color=COLORS['storms']),
            tickfont=dict(color=COLORS['storms']),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99),
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def create_seasonal_chart(df, outcome='suicide'):
    """Create side-by-side bar charts showing seasonal patterns.
    
    Args:
        df: Dataframe with weekly data
        outcome: One of 'suicide', 'violence', 'overdose', 'cardiovascular'
    """
    outcome_col = f'deaths_{outcome}'
    
    # Outcome labels for display
    outcome_labels = {
        'suicide': 'Suicide Deaths',
        'violence': 'Violence/Assault Deaths',
        'overdose': 'Overdose Deaths',
        'cardiovascular': 'Cardiovascular Deaths'
    }
    
    # Extract month from week_end
    df = df.copy()
    df['month'] = pd.to_datetime(df['week_end']).dt.month
    
    # Calculate monthly averages
    monthly_deaths = df.groupby('month')[outcome_col].mean()
    monthly_kp = df.groupby('month')['weekly_mean_Kp'].mean()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create figure with subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'{outcome_labels.get(outcome, "Deaths")} by Month', 'Storm Activity by Month')
    )
    
    fig.add_trace(
        go.Bar(x=month_names, y=monthly_deaths.values, 
               marker_color=OUTCOME_COLORS.get(outcome, COLORS['deaths']), 
               name=outcome_labels.get(outcome, 'Deaths')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=month_names, y=monthly_kp.values, marker_color=COLORS['storms'], name='Storm Index'),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Month", row=1, col=1)
    fig.update_xaxes(title_text="Month", row=1, col=2)
    fig.update_yaxes(title_text="Average Deaths", row=1, col=1)
    fig.update_yaxes(title_text="Average Kp", row=1, col=2)
    
    fig.update_layout(
        height=400,
        showlegend=False,
        template='plotly_white'
    )
    
    return fig


def create_distribution_comparison(df, outcome='suicide', threshold=5.0, storm_metric='weekly_max_Kp'):
    """Create overlapping histograms comparing storm vs non-storm weeks.

    Args:
        df: Dataframe with weekly data
        outcome: One of 'suicide', 'violence', 'overdose', 'cardiovascular'
        threshold: Kp threshold for defining "storm week"
        storm_metric: Column name for storm metric to use for comparison
    """
    outcome_col = f'deaths_{outcome}'

    # Outcome labels for display
    outcome_labels = {
        'suicide': 'Suicide Deaths',
        'violence': 'Violence/Assault Deaths',
        'overdose': 'Overdose Deaths',
        'cardiovascular': 'Cardiovascular Deaths'
    }

    high_storm = df[df[storm_metric] >= threshold][outcome_col]
    low_storm = df[df[storm_metric] < threshold][outcome_col]
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=low_storm,
        name=f'Low Storm ({storm_metric} < {threshold:.2f})',
        opacity=0.6,
        marker_color=OUTCOME_COLORS.get(outcome, COLORS['deaths']),
        nbinsx=20
    ))

    fig.add_trace(go.Histogram(
        x=high_storm,
        name=f'High Storm ({storm_metric} ≥ {threshold:.2f})',
        opacity=0.6,
        marker_color=COLORS['storms'],
        nbinsx=20
    ))
    
    fig.update_layout(
        title=f"Distribution of Weekly {outcome_labels.get(outcome, 'Deaths')} by Storm Activity",
        xaxis_title=f"Weekly {outcome_labels.get(outcome, 'Deaths')}",
        yaxis_title="Number of Weeks",
        barmode='overlay',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_correlation_heatmap(corr_df, outcome=None):
    """Create heatmap showing correlation results.
    
    Args:
        corr_df: Correlation dataframe with all outcomes
        outcome: If specified, only show correlations for this outcome. 
                 If None, show all outcomes.
    """
    if outcome is not None:
        # Filter for specific outcome
        corr_df = corr_df[corr_df['outcome'] == outcome].copy()
        title = f"Correlation Between Geomagnetic Metrics and {corr_df.iloc[0]['outcome_label']}"
    else:
        # Show all outcomes
        title = "Correlations: All Outcomes vs Geomagnetic Metrics"
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=corr_df['pearson_r'],
        y=corr_df['metric'] if outcome else corr_df['outcome_label'] + ' - ' + corr_df['metric'],
        orientation='h',
        marker=dict(
            color=corr_df['pearson_r'],
            colorscale='RdBu',
            cmin=-0.5,
            cmax=0.5,
            showscale=True
        ),
        text=[f"r={r:.3f}" for r in corr_df['pearson_r']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Pearson Correlation (r)",
        yaxis_title="",
        height=400 if outcome else 800,  # Taller for all outcomes
        template='plotly_white'
    )
    
    return fig


def create_multi_outcome_comparison(summary_stats):
    """Create bar chart comparing correlations across all 4 outcomes.
    
    Args:
        summary_stats: Summary statistics dictionary from preprocessing
    
    Returns:
        Plotly figure showing strongest correlation for each outcome
    """
    outcomes = ['suicide', 'violence', 'overdose', 'cardiovascular']
    outcome_labels_map = {
        'suicide': 'Suicide',
        'violence': 'Violence/Assault',
        'overdose': 'Overdose',
        'cardiovascular': 'Cardiovascular'
    }
    
    correlations = []
    labels = []
    colors_list = []
    
    for outcome in outcomes:
        if outcome in summary_stats['strongest_correlations']:
            corr_data = summary_stats['strongest_correlations'][outcome]['overall']
            correlations.append(corr_data['pearson_r'])
            labels.append(outcome_labels_map[outcome])
            colors_list.append(OUTCOME_COLORS[outcome])
        else:
            correlations.append(0)
            labels.append(outcome_labels_map[outcome])
            colors_list.append(OUTCOME_COLORS[outcome])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=correlations,
        marker_color=colors_list,
        text=[f"r={r:.3f}" for r in correlations],
        textposition='outside',
    ))
    
    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="Strongest Correlation with Magnetic Activity (by Outcome)",
        xaxis_title="Outcome Type",
        yaxis_title="Pearson Correlation (r)",
        height=450,
        showlegend=False,
        template='plotly_white'
    )
    
    return fig

