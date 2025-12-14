"""Data preprocessing script for geomagnetic and mortality data."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
from scipy import stats


def load_geomagnetic_data(filepath):
    """Load Kp and ap geomagnetic data."""
    print("Loading geomagnetic data...")
    
    # Read the data file, skipping header lines
    df = pd.read_csv(
        filepath,
        sep=r'\s+',
        skiprows=30,
        names=['year', 'month', 'day', 'hour', 'hour_mid', 'days', 'days_mid', 'Kp', 'ap', 'D']
    )
    
    # Create datetime column
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']]) + pd.to_timedelta(df['hour'], unit='h')
    
    # Filter data from 2018 onwards
    df = df[df['year'] >= 2018].copy()
    
    print(f"Loaded {len(df)} geomagnetic measurements from {df['datetime'].min()} to {df['datetime'].max()}")
    
    return df


def load_mortality_data(filepath, outcome_label):
    """Load mortality data from Excel file.
    
    Args:
        filepath: Path to mortality data file
        outcome_label: Label for the outcome (e.g., 'suicide', 'violence', 'overdose', 'cardiovascular')
    
    Returns:
        DataFrame with columns: year, week_num, week_start, week_end, deaths_{outcome_label}
    """
    print(f"Loading {outcome_label} mortality data...")
    
    # The file has .xls extension but is actually a tab-separated text file
    df = pd.read_csv(filepath, sep='\t')
    
    # Extract relevant columns
    df = df[['MMWR Year', 'MMWR Week', 'Deaths']].copy()
    df.columns = ['year', 'mmwr_week_string', f'deaths_{outcome_label}']
    
    # Remove any rows with missing data
    df = df.dropna(subset=['mmwr_week_string'])
    
    # Filter out rows where MMWR Week doesn't contain "Week"
    df = df[df['mmwr_week_string'].str.contains('Week', na=False)]
    
    # Convert year to numeric, handling cases like "2025 (provisional and partial)"
    # Extract just the year number, ignoring any text after it
    df['year'] = df['year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    
    # Parse MMWR week string to extract end date
    def parse_week_string(s):
        # Example: "2018 Week 01 ending January 06, 2018"
        try:
            parts = s.split()
            month_map = {
                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                'September': 9, 'October': 10, 'November': 11, 'December': 12
            }
            week_num = int(parts[2])
            month = month_map[parts[4]]
            day = int(parts[5].rstrip(','))
            year = int(parts[6])
            return week_num, datetime(year, month, day)
        except (IndexError, ValueError, KeyError) as e:
            print(f"Warning: Could not parse week string: '{s}' - {e}")
            return None, None
    
    df[['week_num', 'week_end']] = df['mmwr_week_string'].apply(
        lambda x: pd.Series(parse_week_string(x))
    )
    
    # Drop rows where parsing failed
    df = df.dropna(subset=['week_end'])
    
    # Calculate week start (6 days before end, since weeks end on Saturday)
    df['week_start'] = df['week_end'] - timedelta(days=6)
    
    # Drop rows with missing deaths
    df = df.dropna(subset=[f'deaths_{outcome_label}'])
    
    print(f"  Loaded {len(df)} weekly records from {df['week_end'].min()} to {df['week_end'].max()}")
    
    return df[['year', 'week_num', 'week_start', 'week_end', f'deaths_{outcome_label}']]


def load_all_mortality_datasets(raw_dir):
    """Load all 4 mortality datasets and merge them.
    
    Returns:
        DataFrame with columns: year, week_num, week_start, week_end, 
                                deaths_suicide, deaths_violence, deaths_overdose, deaths_cardiovascular
    """
    print("\n" + "="*60)
    print("LOADING ALL MORTALITY DATASETS")
    print("="*60)
    
    # Define datasets to load
    datasets = [
        ('Provisional Mortality Statistics, 2018 through Last Week_X60-X84.xls', 'suicide'),
        ('Provisional Mortality Statistics, 2018 through Last Week_X85-Y09.xls', 'violence'),
        ('Provisional Mortality Statistics, 2018 through Last Week_X40-X49&Y10-Y19.xls', 'overdose'),
        ('Provisional Mortality Statistics, 2018 through Last Week_I20-I25& I60-I69.xls', 'cardiovascular'),
    ]
    
    # Load first dataset to establish baseline
    first_file, first_label = datasets[0]
    merged_df = load_mortality_data(raw_dir / first_file, first_label)
    
    # Merge remaining datasets
    for filename, label in datasets[1:]:
        df = load_mortality_data(raw_dir / filename, label)
        merged_df = pd.merge(
            merged_df, 
            df,
            on=['year', 'week_num', 'week_start', 'week_end'],
            how='inner'  # Use inner join to only keep weeks present in all datasets
        )
    
    # Sort by week_end
    merged_df = merged_df.sort_values('week_end').reset_index(drop=True)
    
    print("\n" + "-"*60)
    print(f"✓ Merged all datasets: {len(merged_df)} weeks total")
    print(f"  Date range: {merged_df['week_end'].min()} to {merged_df['week_end'].max()}")
    print(f"  Outcomes included: suicide, violence, overdose, cardiovascular")
    print("-"*60)
    
    return merged_df


def aggregate_geomagnetic_weekly(geo_df, mort_df):
    """Aggregate geomagnetic data to match weekly mortality data.
    
    Args:
        geo_df: Geomagnetic dataframe with Kp, ap measurements
        mort_df: Mortality dataframe with all 4 outcomes
    
    Returns:
        Merged weekly dataframe with geomagnetic metrics and all 4 mortality outcomes
    """
    print("\nAggregating geomagnetic data by week...")
    
    weekly_data = []
    
    for _, mort_row in mort_df.iterrows():
        week_start = mort_row['week_start']
        week_end = mort_row['week_end']
        
        # Get all geomagnetic measurements for this week
        week_mask = (geo_df['datetime'] >= week_start) & (geo_df['datetime'] <= week_end + timedelta(days=1))
        week_geo = geo_df[week_mask]
        
        if len(week_geo) == 0:
            continue
        
        # Calculate weekly aggregates - include all mortality outcomes
        weekly_stats = {
            'year': mort_row['year'],
            'week_num': mort_row['week_num'],
            'week_start': week_start,
            'week_end': week_end,
            'deaths_suicide': mort_row['deaths_suicide'],
            'deaths_violence': mort_row['deaths_violence'],
            'deaths_overdose': mort_row['deaths_overdose'],
            'deaths_cardiovascular': mort_row['deaths_cardiovascular'],
            'weekly_mean_Kp': week_geo['Kp'].mean(),
            'weekly_mean_ap': week_geo['ap'].mean(),
            'weekly_sum_ap': week_geo['ap'].sum(),
            'weekly_max_Kp': week_geo['Kp'].max(),
            'weekly_max_ap': week_geo['ap'].max(),
            'storm_count_Kp5': (week_geo['Kp'] >= 5).sum(),
            'storm_count_Kp6': (week_geo['Kp'] >= 6).sum(),
            'storm_count_Kp7': (week_geo['Kp'] >= 7).sum(),
        }
        
        weekly_data.append(weekly_stats)
    
    weekly_df = pd.DataFrame(weekly_data)
    
    # CRITICAL: Add lagged geomagnetic variables (storms from previous weeks)
    print("\n  Adding lagged geomagnetic variables...")
    
    # Sort by date to ensure correct lagging
    weekly_df = weekly_df.sort_values('week_end').reset_index(drop=True)
    
    # Create lag-1 (previous week) and lag-2 (2 weeks prior) variables
    lag_vars = ['weekly_mean_Kp', 'weekly_mean_ap', 'weekly_sum_ap', 'weekly_max_Kp', 'storm_count_Kp5']
    
    for var in lag_vars:
        weekly_df[f'{var}_lag1'] = weekly_df[var].shift(1)
        weekly_df[f'{var}_lag2'] = weekly_df[var].shift(2)
    
    # Drop first 2 rows where lags are NaN
    weekly_df = weekly_df.dropna(subset=[f'{lag_vars[0]}_lag1', f'{lag_vars[0]}_lag2']).reset_index(drop=True)
    
    print(f"✓ Created {len(weekly_df)} weekly records with 4 outcomes + lagged variables")
    print(f"  (Lost 2 rows due to lagging)")
    
    return weekly_df


def compute_correlations(weekly_df):
    """Compute correlations between geomagnetic metrics and all 4 outcomes.
    
    Tests both SAME-WEEK and LAGGED (1 week prior) effects.
    
    Returns:
        DataFrame with columns: outcome, metric, metric_col, lag, pearson_r, pearson_p, 
                                spearman_r, spearman_p, r_squared, significant
    """
    print("\nComputing correlations for all outcomes (same-week + lagged)...")
    
    # Define metrics with both same-week and lag-1 versions
    metrics = [
        # Same week (baseline)
        ('weekly_mean_Kp', 'Weekly Mean Kp', 'same-week'),
        ('weekly_mean_ap', 'Weekly Mean Ap', 'same-week'),
        ('weekly_sum_ap', 'Weekly Sum Ap', 'same-week'),
        ('weekly_max_Kp', 'Weekly Max Kp', 'same-week'),
        ('storm_count_Kp5', 'Storm Count (Kp≥5)', 'same-week'),
        # Lag-1 (previous week) - CRITICAL: These are often stronger!
        ('weekly_mean_Kp_lag1', 'Weekly Mean Kp (lag-1)', 'lag-1'),
        ('weekly_mean_ap_lag1', 'Weekly Mean Ap (lag-1)', 'lag-1'),
        ('weekly_sum_ap_lag1', 'Weekly Sum Ap (lag-1)', 'lag-1'),
        ('weekly_max_Kp_lag1', 'Weekly Max Kp (lag-1)', 'lag-1'),
        ('storm_count_Kp5_lag1', 'Storm Count Kp≥5 (lag-1)', 'lag-1'),
    ]
    
    outcomes = [
        ('deaths_suicide', 'Suicide', 'suicide'),
        ('deaths_violence', 'Violence/Assault', 'violence'),
        ('deaths_overdose', 'Overdose', 'overdose'),
        ('deaths_cardiovascular', 'Cardiovascular', 'cardiovascular'),
    ]
    
    results = []
    
    for outcome_col, outcome_name, outcome_key in outcomes:
        print(f"\n  {outcome_name}:")
        print(f"    Same-week effects:")
        
        for metric_col, metric_name, lag in metrics:
            if lag == 'same-week':
                r, p = stats.pearsonr(weekly_df[metric_col], weekly_df[outcome_col])
                r_spearman, p_spearman = stats.spearmanr(weekly_df[metric_col], weekly_df[outcome_col])
                
                results.append({
                    'outcome': outcome_key,
                    'outcome_label': outcome_name,
                    'metric': metric_name,
                    'metric_col': metric_col,
                    'lag': lag,
                    'pearson_r': r,
                    'pearson_p': p,
                    'spearman_r': r_spearman,
                    'spearman_p': p_spearman,
                    'r_squared': r**2,
                    'significant': p < 0.05
                })
                
                sig_marker = "✓" if p < 0.05 else "✗"
                print(f"      {metric_name}: r={r:.3f}, p={p:.4f} {sig_marker}")
        
        print(f"    Lagged effects (1 week prior):")
        for metric_col, metric_name, lag in metrics:
            if lag == 'lag-1':
                r, p = stats.pearsonr(weekly_df[metric_col], weekly_df[outcome_col])
                r_spearman, p_spearman = stats.spearmanr(weekly_df[metric_col], weekly_df[outcome_col])
                
                results.append({
                    'outcome': outcome_key,
                    'outcome_label': outcome_name,
                    'metric': metric_name,
                    'metric_col': metric_col,
                    'lag': lag,
                    'pearson_r': r,
                    'pearson_p': p,
                    'spearman_r': r_spearman,
                    'spearman_p': p_spearman,
                    'r_squared': r**2,
                    'significant': p < 0.05
                })
                
                sig_marker = "✓✓" if p < 0.01 else "✓" if p < 0.05 else "✗"
                print(f"      {metric_name}: r={r:.3f}, p={p:.4f} {sig_marker}")
    
    return pd.DataFrame(results)


def create_monthly_summary(weekly_df):
    """Create monthly aggregated summary for all outcomes."""
    print("\nCreating monthly summary...")
    
    weekly_df_copy = weekly_df.copy()
    weekly_df_copy['year_month'] = weekly_df_copy['week_end'].dt.to_period('M')
    
    monthly = weekly_df_copy.groupby('year_month').agg({
        'deaths_suicide': 'mean',
        'deaths_violence': 'mean',
        'deaths_overdose': 'mean',
        'deaths_cardiovascular': 'mean',
        'weekly_mean_Kp': 'mean',
        'weekly_mean_ap': 'mean',
        'weekly_mean_Kp_lag1': 'mean',
        'storm_count_Kp5': 'sum'
    }).reset_index()
    
    monthly['year_month'] = monthly['year_month'].dt.to_timestamp()
    
    print(f"✓ Created {len(monthly)} monthly summary records")
    
    return monthly


def compute_summary_stats(weekly_df, correlation_df):
    """Compute summary statistics for the app - now for all 4 outcomes."""
    print("\nComputing summary statistics...")
    
    # Get storm vs non-storm weeks comparison
    storm_weeks = weekly_df[weekly_df['storm_count_Kp5'] > 0]
    no_storm_weeks = weekly_df[weekly_df['storm_count_Kp5'] == 0]
    
    # Compute stats for each outcome
    outcomes = {
        'suicide': 'deaths_suicide',
        'violence': 'deaths_violence',
        'overdose': 'deaths_overdose',
        'cardiovascular': 'deaths_cardiovascular'
    }
    
    outcome_stats = {}
    outcome_comparisons = {}
    
    for outcome_name, outcome_col in outcomes.items():
        outcome_stats[outcome_name] = {
            'mean': float(weekly_df[outcome_col].mean()),
            'std': float(weekly_df[outcome_col].std()),
            'min': int(weekly_df[outcome_col].min()),
            'max': int(weekly_df[outcome_col].max())
        }
        
        outcome_comparisons[outcome_name] = {
            'storm_weeks_mean': float(storm_weeks[outcome_col].mean()) if len(storm_weeks) > 0 else None,
            'no_storm_weeks_mean': float(no_storm_weeks[outcome_col].mean()) if len(no_storm_weeks) > 0 else None,
            'difference': float(storm_weeks[outcome_col].mean() - no_storm_weeks[outcome_col].mean()) if len(storm_weeks) > 0 and len(no_storm_weeks) > 0 else None
        }
    
    # Get strongest correlation for each outcome, plus separate same-week and lag-1 best
    correlations_by_outcome = {}
    for outcome_name in outcomes.keys():
        outcome_corrs = correlation_df[correlation_df['outcome'] == outcome_name]
        if len(outcome_corrs) > 0:
            valid_corrs = outcome_corrs.dropna(subset=['pearson_r'])
            if len(valid_corrs) > 0:
                # Overall strongest
                strongest_idx = valid_corrs['pearson_r'].abs().idxmax()
                strongest = valid_corrs.loc[strongest_idx]
                
                # Strongest same-week
                same_week_corrs = valid_corrs[valid_corrs['lag'] == 'same-week']
                strongest_same_week = None
                if len(same_week_corrs) > 0:
                    strongest_same_week_idx = same_week_corrs['pearson_r'].abs().idxmax()
                    strongest_same_week = same_week_corrs.loc[strongest_same_week_idx]
                
                # Strongest lag-1
                lag1_corrs = valid_corrs[valid_corrs['lag'] == 'lag-1']
                strongest_lag1 = None
                if len(lag1_corrs) > 0:
                    strongest_lag1_idx = lag1_corrs['pearson_r'].abs().idxmax()
                    strongest_lag1 = lag1_corrs.loc[strongest_lag1_idx]
                
                correlations_by_outcome[outcome_name] = {
                    'overall': {
                        'metric': strongest['metric'],
                        'metric_col': strongest['metric_col'],
                        'lag': strongest['lag'],
                        'pearson_r': float(strongest['pearson_r']),
                        'pearson_p': float(strongest['pearson_p']),
                        'r_squared': float(strongest['r_squared'])
                    },
                    'same_week': {
                        'metric': strongest_same_week['metric'] if strongest_same_week is not None else None,
                        'metric_col': strongest_same_week['metric_col'] if strongest_same_week is not None else None,
                        'pearson_r': float(strongest_same_week['pearson_r']) if strongest_same_week is not None else None,
                        'pearson_p': float(strongest_same_week['pearson_p']) if strongest_same_week is not None else None,
                    } if strongest_same_week is not None else None,
                    'lag1': {
                        'metric': strongest_lag1['metric'] if strongest_lag1 is not None else None,
                        'metric_col': strongest_lag1['metric_col'] if strongest_lag1 is not None else None,
                        'pearson_r': float(strongest_lag1['pearson_r']) if strongest_lag1 is not None else None,
                        'pearson_p': float(strongest_lag1['pearson_p']) if strongest_lag1 is not None else None,
                    } if strongest_lag1 is not None else None
                }
    
    summary = {
        'n_weeks': len(weekly_df),
        'n_measurements': len(weekly_df) * 56,  # 8 per day * 7 days
        'date_range': {
            'start': weekly_df['week_start'].min().strftime('%Y-%m-%d'),
            'end': weekly_df['week_end'].max().strftime('%Y-%m-%d')
        },
        'outcomes': outcome_stats,
        'geomagnetic': {
            'mean_Kp': float(weekly_df['weekly_mean_Kp'].mean()),
            'max_Kp_overall': float(weekly_df['weekly_max_Kp'].max()),
            'mean_ap': float(weekly_df['weekly_mean_ap'].mean()),
        },
        'storm_comparison': {
            'storm_weeks_count': len(storm_weeks),
            'no_storm_weeks_count': len(no_storm_weeks),
        },
        'outcome_comparisons': outcome_comparisons,
        'strongest_correlations': correlations_by_outcome,
        'all_correlations': correlation_df.to_dict('records')
    }
    
    return summary


def main():
    """Main preprocessing pipeline."""
    print("="*60)
    print("GEOMAGNETIC-MORTALITY DATA PREPROCESSING")
    print("Multi-Outcome Analysis (4 Outcomes)")
    print("="*60)
    
    # Set up paths
    base_dir = Path(__file__).parent
    data_dir = base_dir / 'data'
    raw_dir = data_dir / 'raw'
    preprocessed_dir = data_dir / 'preprocessed'
    
    # Load raw data
    geo_df = load_geomagnetic_data(raw_dir / 'Kp_ap_since_1932.txt')
    mort_df = load_all_mortality_datasets(raw_dir)
    
    # Aggregate and merge
    weekly_df = aggregate_geomagnetic_weekly(geo_df, mort_df)
    
    # Compute correlations (now for all 4 outcomes)
    correlation_df = compute_correlations(weekly_df)
    
    # Create monthly summary
    monthly_df = create_monthly_summary(weekly_df)
    
    # Compute summary statistics
    summary_stats = compute_summary_stats(weekly_df, correlation_df)
    
    # Save preprocessed data
    print("\n" + "="*60)
    print("SAVING PREPROCESSED DATA")
    print("="*60)
    preprocessed_dir.mkdir(parents=True, exist_ok=True)
    
    weekly_df.to_parquet(preprocessed_dir / 'weekly_merged.parquet', index=False)
    print(f"✓ Saved weekly_merged.parquet ({len(weekly_df)} weeks, 4 outcomes)")
    
    monthly_df.to_parquet(preprocessed_dir / 'monthly_summary.parquet', index=False)
    print(f"✓ Saved monthly_summary.parquet")
    
    correlation_df.to_parquet(preprocessed_dir / 'correlation_matrix.parquet', index=False)
    print(f"✓ Saved correlation_matrix.parquet ({len(correlation_df)} correlations)")
    
    with open(preprocessed_dir / 'summary_stats.json', 'w') as f:
        json.dump(summary_stats, f, indent=2)
    print(f"✓ Saved summary_stats.json")
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE!")
    print("="*60)
    print(f"\nSummary:")
    print(f"  - {summary_stats['n_weeks']} weeks analyzed")
    print(f"  - 4 outcomes: Suicide, Violence, Overdose, Cardiovascular")
    print(f"  - {summary_stats['geomagnetic']['mean_Kp']:.2f} average Kp index")
    print(f"\nStrongest correlations by outcome:")
    for outcome in ['suicide', 'violence', 'overdose', 'cardiovascular']:
        if outcome in summary_stats['strongest_correlations']:
            overall = summary_stats['strongest_correlations'][outcome]['overall']
            same_week = summary_stats['strongest_correlations'][outcome].get('same_week')
            lag1 = summary_stats['strongest_correlations'][outcome].get('lag1')
            
            print(f"\n  {outcome.capitalize()}:")
            print(f"    Overall strongest: r={overall['pearson_r']:.3f} [{overall['lag']}] ({overall['metric']})")
            if same_week:
                print(f"    Same-week best: r={same_week['pearson_r']:.3f} ({same_week['metric']})")
            if lag1:
                print(f"    Lag-1 best: r={lag1['pearson_r']:.3f} ({lag1['metric']})")
    
    print("\n" + "="*60)
    print("NOTE: Both same-week and lag-1 effects analyzed.")
    print("Your data scientist found lag-1 effects often stronger")
    print("when controlling for autocorrelation (lagged deaths).")
    print("="*60)


if __name__ == '__main__':
    main()

