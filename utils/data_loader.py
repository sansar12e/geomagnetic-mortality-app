"""Data loading functions with caching."""
import streamlit as st
import pandas as pd
import json
from pathlib import Path


@st.cache_data(ttl=3600)
def load_preprocessed_data():
    """Load pre-aggregated data for fast initial render."""
    data_dir = Path(__file__).parent.parent / 'data' / 'preprocessed'
    
    return {
        'weekly': pd.read_parquet(data_dir / 'weekly_merged.parquet'),
        'monthly': pd.read_parquet(data_dir / 'monthly_summary.parquet'),
        'correlations': pd.read_parquet(data_dir / 'correlation_matrix.parquet'),
        'summary_stats': json.load(open(data_dir / 'summary_stats.json'))
    }


@st.cache_data
def load_weekly_data():
    """Load full weekly data (called on demand)."""
    data_dir = Path(__file__).parent.parent / 'data' / 'preprocessed'
    df = pd.read_parquet(data_dir / 'weekly_merged.parquet')
    df['week_end'] = pd.to_datetime(df['week_end'])
    return df


@st.cache_data
def compute_correlation(df, x_col, y_col):
    """Compute Pearson correlation between two variables."""
    from scipy import stats
    r, p = stats.pearsonr(df[x_col].dropna(), df[y_col].dropna())
    return {'r': r, 'p': p, 'r_squared': r**2}

