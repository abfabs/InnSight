# backend/data/data_validator.py

import pandas as pd
import logging
from typing import Dict, List, Tuple
from .config import VALIDATION_RULES
from .utils import validate_coordinates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validates data quality for listings, reviews, and calendar data."""
    
    def __init__(self, rules: Dict = None):
        """
        Initialize validator with validation rules.
        
        Args:
            rules: Dictionary of validation rules (uses config default if None)
        """
        self.rules = rules or VALIDATION_RULES
    
    def validate_listings(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Validate listings data.
        
        Args:
            df: Listings DataFrame
            
        Returns:
            Tuple of (validated_df, validation_report)
        """
        logger.info("Validating listings data...")
        report = {
            'total_rows': len(df),
            'errors': [],
            'warnings': [],
            'removed_rows': 0
        }
        
        rules = self.rules['listings']
        initial_count = len(df)
        
        # Check required columns
        missing_cols = set(rules['required_columns']) - set(df.columns)
        if missing_cols:
            report['errors'].append(f"Missing required columns: {missing_cols}")
            return df, report
        
        # Remove rows with missing critical fields
        df = df.dropna(subset=['id', 'latitude', 'longitude'])
        
        # Validate coordinates
        valid_coords = df.apply(
            lambda row: validate_coordinates(
                row['latitude'], 
                row['longitude'],
                rules['coordinate_ranges']['latitude'],
                rules['coordinate_ranges']['longitude']
            ), axis=1
        )
        
        invalid_coords = (~valid_coords).sum()
        if invalid_coords > 0:
            report['warnings'].append(f"Removed {invalid_coords} rows with invalid coordinates")
            df = df[valid_coords]
        
        # Validate price range
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            min_price, max_price = rules['price_range']
            
            invalid_prices = (df['price'] < min_price) | (df['price'] > max_price)
            invalid_price_count = invalid_prices.sum()
            
            if invalid_price_count > 0:
                report['warnings'].append(
                    f"Found {invalid_price_count} listings with invalid prices (outside {min_price}-{max_price} range)"
                )
                # Set invalid prices to None rather than removing rows
                df.loc[invalid_prices, 'price'] = None
        
        # Validate numeric columns
        for col in rules['numeric_columns']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['id'], keep='first').sum()
        if duplicates > 0:
            report['warnings'].append(f"Removed {duplicates} duplicate listing IDs")
            df = df.drop_duplicates(subset=['id'], keep='first')
        
        report['removed_rows'] = initial_count - len(df)
        report['final_rows'] = len(df)
        
        logger.info(f"Listings validation complete: {len(df)}/{initial_count} rows retained")
        
        return df, report
    
    def validate_reviews(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Validate reviews data.
        
        Args:
            df: Reviews DataFrame
            
        Returns:
            Tuple of (validated_df, validation_report)
        """
        logger.info("Validating reviews data...")
        report = {
            'total_rows': len(df),
            'errors': [],
            'warnings': [],
            'removed_rows': 0
        }
        
        rules = self.rules['reviews']
        initial_count = len(df)
        
        # Check required columns
        missing_cols = set(rules['required_columns']) - set(df.columns)
        if missing_cols:
            report['errors'].append(f"Missing required columns: {missing_cols}")
            return df, report
        
        # Remove rows with missing critical fields
        df = df.dropna(subset=['listing_id', 'comments'])
        
        # Validate comment length
        if 'min_comment_length' in rules:
            min_length = rules['min_comment_length']
            short_comments = df['comments'].str.len() < min_length
            short_count = short_comments.sum()
            
            if short_count > 0:
                report['warnings'].append(
                    f"Removed {short_count} reviews with comments shorter than {min_length} characters"
                )
                df = df[~short_comments]
        
        # Validate date format
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            invalid_dates = df['date'].isna().sum()
            
            if invalid_dates > 0:
                report['warnings'].append(f"Found {invalid_dates} reviews with invalid dates")
                df = df.dropna(subset=['date'])
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['id'], keep='first').sum()
        if duplicates > 0:
            report['warnings'].append(f"Removed {duplicates} duplicate review IDs")
            df = df.drop_duplicates(subset=['id'], keep='first')
        
        report['removed_rows'] = initial_count - len(df)
        report['final_rows'] = len(df)
        
        logger.info(f"Reviews validation complete: {len(df)}/{initial_count} rows retained")
        
        return df, report
    
    def validate_calendar(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Validate calendar data.
        
        Args:
            df: Calendar DataFrame
            
        Returns:
            Tuple of (validated_df, validation_report)
        """
        logger.info("Validating calendar data...")
        report = {
            'total_rows': len(df),
            'errors': [],
            'warnings': [],
            'removed_rows': 0
        }
        
        rules = self.rules['calendar']
        initial_count = len(df)
        
        # Check required columns
        missing_cols = set(rules['required_columns']) - set(df.columns)
        if missing_cols:
            report['errors'].append(f"Missing required columns: {missing_cols}")
            return df, report
        
        # Remove rows with missing critical fields
        before_drop = len(df)
        df = df.dropna(subset=['listing_id', 'date'])
        dropped_missing = before_drop - len(df)
        
        if dropped_missing > 0:
            report['warnings'].append(f"Removed {dropped_missing} rows with missing listing_id or date")
        
        # Validate date format
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        invalid_dates = df['date'].isna().sum()
        
        if invalid_dates > 0:
            report['warnings'].append(f"Removed {invalid_dates} rows with invalid dates")
            df = df.dropna(subset=['date'])
        
        # Validate available field
        if 'available' in df.columns:
            # Check if there are any non-boolean values
            invalid_available = df['available'].isna().sum()
            
            if invalid_available > 0:
                report['warnings'].append(
                    f"Removed {invalid_available} rows with missing availability values"
                )
                df = df.dropna(subset=['available'])
        
        # Validate price if present
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Check for duplicates (listing_id + date should be unique)
        duplicates = df.duplicated(subset=['listing_id', 'date'], keep='first').sum()
        if duplicates > 0:
            report['warnings'].append(f"Removed {duplicates} duplicate calendar entries")
            df = df.drop_duplicates(subset=['listing_id', 'date'], keep='first')
        
        report['removed_rows'] = initial_count - len(df)
        report['final_rows'] = len(df)
        
        logger.info(f"Calendar validation complete: {len(df)}/{initial_count} rows retained")
        
        return df, report
    
    def print_report(self, report: Dict, dataset_name: str):
        """
        Print validation report.
        
        Args:
            report: Validation report dictionary
            dataset_name: Name of the dataset
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"Validation Report: {dataset_name}")
        logger.info(f"{'='*50}")
        logger.info(f"Total rows: {report['total_rows']}")
        logger.info(f"Final rows: {report.get('final_rows', 'N/A')}")
        logger.info(f"Removed rows: {report['removed_rows']}")
        
        if report['errors']:
            logger.error("ERRORS:")
            for error in report['errors']:
                logger.error(f"  - {error}")
        
        if report['warnings']:
            logger.warning("WARNINGS:")
            for warning in report['warnings']:
                logger.warning(f"  - {warning}")
        
        logger.info(f"{'='*50}\n")
