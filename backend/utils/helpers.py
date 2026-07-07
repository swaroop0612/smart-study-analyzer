"""
Helper Functions
Common utilities used across the application.
"""
from datetime import datetime, date


def format_date(value):
    """Convert date/datetime to ISO string."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def format_time(value):
    """Convert time to HH:MM:SS string."""
    if hasattr(value, 'strftime'):
        return value.strftime("%H:%M:%S")
    return value


def safe_round(value, decimals=2):
    """Safely round a value, return 0 if None."""
    if value is None:
        return 0
    try:
        return round(float(value), decimals)
    except (ValueError, TypeError):
        return 0


def get_weekday_name(date_value):
    """Get weekday name from date."""
    if isinstance(date_value, str):
        try:
            date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return "Unknown"
    if isinstance(date_value, date):
        return date_value.strftime("%A")
    return "Unknown"


def get_time_of_day(time_value):
    """Categorize time into morning/afternoon/evening/night."""
    if not time_value:
        return "Unknown"
    
    if isinstance(time_value, str):
        try:
            time_value = datetime.strptime(time_value, "%H:%M:%S").time()
        except ValueError:
            return "Unknown"
    
    hour = time_value.hour
    
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"
