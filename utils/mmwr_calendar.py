"""MMWR (Morbidity and Mortality Weekly Report) calendar utilities."""
import pandas as pd
from datetime import datetime, timedelta


def parse_mmwr_week(mmwr_string):
    """Parse MMWR week string to extract year, week number, and end date.
    
    Example: "2018 Week 01 ending January 06, 2018" -> (2018, 1, datetime(2018, 1, 6))
    """
    parts = mmwr_string.split()
    year = int(parts[0])
    week = int(parts[2])
    
    # Parse the ending date
    month_str = parts[4]
    day_str = parts[5].rstrip(',')
    year_str = parts[6]
    
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    end_date = datetime(int(year_str), month_map[month_str], int(day_str))
    
    return year, week, end_date


def get_week_start_date(end_date):
    """Get the start date of a week given its end date (Saturday end)."""
    return end_date - timedelta(days=6)

