# backend/data/data_cleaner.py

import pandas as pd
import logging
from typing import List
from .config import LISTINGS_COLUMNS, REVIEWS_COLUMNS, CALENDAR_COLUMNS
from .utils import (
    clean_price, 
    parse_date, 
    clean_percentage, 
    parse_boolean,
    clean_text,
    parse_amenities,
    remove_duplicates,
    log_data_summary
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and transforms raw data from CSV files."""
    
    def clean_listings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean listings data.
        
        Args:
            df: Raw listings DataFrame
            
        Returns:
            Cleaned listings DataFrame
        """
        logger.info("Cleaning listings data...")
        
        # Select only required columns (if they exist)
        available_cols = [col for col in LISTINGS_COLUMNS if col in df.columns]
        df = df[available_cols].copy()
        
        # Clean price
        if 'price' in df.columns:
            df['price'] = df['price'].apply(clean_price)
        
        # Clean host response rate
        if 'host_response_rate' in df.columns:
            df['host_response_rate'] = df['host_response_rate'].apply(clean_percentage)
        
        # Parse boolean fields
        boolean_fields = ['host_is_superhost', 'instant_bookable']
        for field in boolean_fields:
            if field in df.columns:
                df[field] = df[field].apply(parse_boolean)
        
        # Clean text fields
        text_fields = ['name', 'description', 'neighborhood_overview']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].apply(clean_text)
        
        # Parse amenities
        if 'amenities' in df.columns:
            df['amenities'] = df['amenities'].apply(parse_amenities)
        
        # Convert numeric fields
        numeric_fields = [
            'latitude', 'longitude', 'accommodates', 
            'bathrooms', 'bedrooms', 'beds',
            'minimum_nights', 'maximum_nights',
            'number_of_reviews', 'review_scores_rating',
            'review_scores_cleanliness', 'review_scores_location',
            'host_listings_count'
        ]
        
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Parse dates
        if 'host_since' in df.columns:
            df['host_since'] = pd.to_datetime(df['host_since'], errors='coerce')
        
        # Remove duplicates
        df = remove_duplicates(df, subset=['id'])
        
        # Convert id to string for consistency
        df['id'] = df['id'].astype(str)
        if 'host_id' in df.columns:
            df['host_id'] = df['host_id'].astype(str)
        
        log_data_summary(df, "Cleaned Listings")
        logger.info("Listings cleaning complete")
        
        return df
    
    def clean_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean reviews data.
        
        Args:
            df: Raw reviews DataFrame
            
        Returns:
            Cleaned reviews DataFrame
        """
        logger.info("Cleaning reviews data...")
        
        # Select only required columns
        available_cols = [col for col in REVIEWS_COLUMNS if col in df.columns]
        df = df[available_cols].copy()
        
        # Convert IDs to string
        df['listing_id'] = df['listing_id'].astype(str)
        df['id'] = df['id'].astype(str)
        if 'reviewer_id' in df.columns:
            df['reviewer_id'] = df['reviewer_id'].astype(str)
        
        # Parse date
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Clean comments text
        if 'comments' in df.columns:
            df['comments'] = df['comments'].apply(lambda x: clean_text(x, remove_html=True))
            
            # Remove rows with empty comments after cleaning
            df = df[df['comments'].notna()]
            df = df[df['comments'].str.len() >= 10]  # Minimum 10 characters
        
        # Clean reviewer name
        if 'reviewer_name' in df.columns:
            df['reviewer_name'] = df['reviewer_name'].apply(lambda x: clean_text(x, remove_html=False))
        
        # Remove duplicates
        df = remove_duplicates(df, subset=['id'])
        
        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date')
        
        log_data_summary(df, "Cleaned Reviews")
        logger.info("Reviews cleaning complete")
        
        return df
    
    def clean_calendar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean calendar data.
        
        Args:
            df: Raw calendar DataFrame
            
        Returns:
            Cleaned calendar DataFrame
        """
        logger.info("Cleaning calendar data...")
        
        # Select only required columns
        available_cols = [col for col in CALENDAR_COLUMNS if col in df.columns]
        df = df[available_cols].copy()
        
        # Convert listing_id to string
        df['listing_id'] = df['listing_id'].astype(str)
        
        # Parse date
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
        
        # Parse available field
        if 'available' in df.columns:
            df['available'] = df['available'].apply(parse_boolean)
        
        # Clean price
        if 'price' in df.columns:
            df['price'] = df['price'].apply(clean_price)
        
        # Convert numeric fields
        numeric_fields = ['minimum_nights', 'maximum_nights']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Remove duplicates (listing_id + date should be unique)
        df = remove_duplicates(df, subset=['listing_id', 'date'])
        
        # Sort by listing_id and date
        df = df.sort_values(['listing_id', 'date'])
        
        log_data_summary(df, "Cleaned Calendar")
        logger.info("Calendar cleaning complete")
        
        return df
    
    def clean_neighbourhoods(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean neighbourhoods data.
        
        Args:
            df: Raw neighbourhoods DataFrame
            
        Returns:
            Cleaned neighbourhoods DataFrame
        """
        logger.info("Cleaning neighbourhoods data...")
        
        # Clean text fields
        if 'neighbourhood' in df.columns:
            df['neighbourhood'] = df['neighbourhood'].apply(lambda x: clean_text(x, remove_html=False))
        
        if 'neighbourhood_group' in df.columns:
            df['neighbourhood_group'] = df['neighbourhood_group'].apply(lambda x: clean_text(x, remove_html=False))
        
        # Remove duplicates
        if 'neighbourhood' in df.columns:
            df = remove_duplicates(df, subset=['neighbourhood'])
        
        log_data_summary(df, "Cleaned Neighbourhoods")
        logger.info("Neighbourhoods cleaning complete")
        
        return df
