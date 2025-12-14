"""Statistical computation functions."""
import pandas as pd
from scipy import stats


def compute_correlation(df, x_col, y_col):
    """Compute Pearson and Spearman correlations."""
    # Remove NaN values
    valid_data = df[[x_col, y_col]].dropna()
    
    # Pearson correlation
    r_pearson, p_pearson = stats.pearsonr(valid_data[x_col], valid_data[y_col])
    
    # Spearman correlation
    r_spearman, p_spearman = stats.spearmanr(valid_data[x_col], valid_data[y_col])
    
    return {
        'pearson_r': r_pearson,
        'pearson_p': p_pearson,
        'pearson_r_squared': r_pearson ** 2,
        'spearman_r': r_spearman,
        'spearman_p': p_spearman,
        'n': len(valid_data)
    }


def compare_groups(df, group_col, threshold, value_col):
    """Compare two groups based on a threshold."""
    high_group = df[df[group_col] >= threshold][value_col]
    low_group = df[df[group_col] < threshold][value_col]
    
    # T-test
    t_stat, p_value = stats.ttest_ind(high_group, low_group)
    
    # Effect size (Cohen's d)
    pooled_std = ((len(high_group)-1) * high_group.std()**2 + 
                  (len(low_group)-1) * low_group.std()**2) / (len(high_group) + len(low_group) - 2)
    pooled_std = pooled_std ** 0.5
    cohens_d = (high_group.mean() - low_group.mean()) / pooled_std if pooled_std > 0 else 0
    
    return {
        'high_mean': high_group.mean(),
        'high_std': high_group.std(),
        'high_n': len(high_group),
        'low_mean': low_group.mean(),
        'low_std': low_group.std(),
        'low_n': len(low_group),
        'difference': high_group.mean() - low_group.mean(),
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d
    }


def compute_seasonal_adjustment(df, date_col, value_col):
    """Remove seasonal patterns from data."""
    df = df.copy()
    df['month'] = pd.to_datetime(df[date_col]).dt.month
    
    # Calculate monthly means
    monthly_means = df.groupby('month')[value_col].mean()
    
    # Subtract monthly mean from each observation
    df['adjusted'] = df.apply(
        lambda row: row[value_col] - monthly_means[row['month']] + df[value_col].mean(),
        axis=1
    )
    
    return df


def format_p_value(p):
    """Format p-value for display."""
    if p < 0.001:
        return "< 0.001"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.2f}"


def is_significant(p, alpha=0.05):
    """Check if p-value is significant."""
    return p < alpha

