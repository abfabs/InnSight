# backend/data/utils.py

import re
import pandas as pd
from datetime import datetime
from typing import Optional, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_price(price_str: Union[str, float, None]) -> Optional[float]:
    """
    Clean price string and convert to float.
    
    Args:
        price_str: Price as string (e.g., "$123.45") or float
        
    Returns:
        Float price or None if invalid
    """
    if pd.isna(price_str) or price_str == '':
        return None
    
    if isinstance(price_str, (int, float)):
        return float(price_str)
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[$,€£]', '', str(price_str))
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def parse_date(date_str: Union[str, datetime, None], date_format: str = '%Y-%m-%d') -> Optional[datetime]:
    """
    Parse date string to datetime object.
    
    Args:
        date_str: Date as string or datetime
        date_format: Expected date format
        
    Returns:
        Datetime object or None if invalid
    """
    if pd.isna(date_str) or date_str == '':
        return None
    
    if isinstance(date_str, datetime):
        return date_str
    
    try:
        return datetime.strptime(str(date_str), date_format)
    except (ValueError, TypeError):
        return None


def clean_percentage(percent_str: Union[str, float, None]) -> Optional[float]:
    """
    Clean percentage string and convert to float (0-100 scale).
    
    Args:
        percent_str: Percentage as string (e.g., "95%") or float
        
    Returns:
        Float percentage or None if invalid
    """
    if pd.isna(percent_str) or percent_str == '':
        return None
    
    if isinstance(percent_str, (int, float)):
        return float(percent_str)
    
    # Remove percentage symbol
    cleaned = str(percent_str).replace('%', '').strip()
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def parse_boolean(value: Union[str, bool, None]) -> Optional[bool]:
    """
    Parse various boolean representations to bool.
    
    Args:
        value: Boolean as string ('t', 'f', 'true', 'false') or bool
        
    Returns:
        Boolean or None if invalid
    """
    if pd.isna(value) or value == '':
        return None
    
    if isinstance(value, bool):
        return value
    
    value_lower = str(value).lower().strip()
    
    if value_lower in ['t', 'true', '1', 'yes']:
        return True
    elif value_lower in ['f', 'false', '0', 'no']:
        return False
    else:
        return None


def clean_text(text: Union[str, None], remove_html: bool = True) -> Optional[str]:
    """
    Clean text by removing extra whitespace and optionally HTML tags.
    
    Args:
        text: Text to clean
        remove_html: Whether to remove HTML tags
        
    Returns:
        Cleaned text or None if empty
    """
    if pd.isna(text) or text == '':
        return None
    
    text = str(text)
    
    # Remove HTML tags if requested
    if remove_html:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'<br\s*/?\s*>', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip() if text else None


def parse_amenities(amenities_str: Union[str, list, None]) -> list:
    """
    Parse amenities string/list into a clean list.
    
    Args:
        amenities_str: Amenities as string or list
        
    Returns:
        List of amenities
    """
    if pd.isna(amenities_str) or amenities_str == '':
        return []
    
    if isinstance(amenities_str, list):
        return amenities_str
    
    # Remove brackets and quotes, split by comma
    amenities_str = str(amenities_str).strip('[]')
    amenities = [a.strip(' "\'') for a in amenities_str.split(',')]
    
    return [a for a in amenities if a]


def validate_coordinates(lat: float, lon: float, 
                        lat_range: tuple = (52.3, 52.45), 
                        lon_range: tuple = (4.7, 5.0)) -> bool:
    """
    Validate if coordinates are within Amsterdam bounds.
    
    Args:
        lat: Latitude
        lon: Longitude
        lat_range: Valid latitude range (min, max)
        lon_range: Valid longitude range (min, max)
        
    Returns:
        True if valid, False otherwise
    """
    try:
        lat = float(lat)
        lon = float(lon)
        
        return (lat_range[0] <= lat <= lat_range[1] and 
                lon_range[0] <= lon <= lon_range[1])
    except (ValueError, TypeError):
        return False


def remove_duplicates(df: pd.DataFrame, subset: list, keep: str = 'first') -> pd.DataFrame:
    """
    Remove duplicate rows from DataFrame.
    
    Args:
        df: DataFrame to deduplicate
        subset: Columns to check for duplicates
        keep: Which duplicate to keep ('first', 'last', False)
        
    Returns:
        DataFrame without duplicates
    """
    initial_count = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    removed = initial_count - len(df_clean)
    
    if removed > 0:
        logger.info(f"Removed {removed} duplicate rows")
    
    return df_clean


def log_data_summary(df: pd.DataFrame, name: str):
    """
    Log summary statistics for a DataFrame.
    
    Args:
        df: DataFrame to summarize
        name: Name of the dataset
    """
    logger.info(f"\n{name} Summary:")
    logger.info(f"  Total rows: {len(df)}")
    logger.info(f"  Total columns: {len(df.columns)}")
    logger.info(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        logger.info(f"  Columns with missing values:")
        for col, count in missing[missing > 0].items():
            logger.info(f"    {col}: {count} ({count/len(df)*100:.1f}%)")
