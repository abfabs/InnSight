# backend/data/config.py

import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
RAW_DATA_DIR = BASE_DIR / 'data' / 'raw' / 'amsterdam'
PROCESSED_DATA_DIR = BASE_DIR / 'data' / 'processed'

# Raw data files
LISTINGS_FILE = RAW_DATA_DIR / 'listings.csv'
REVIEWS_FILE = RAW_DATA_DIR / 'reviews.csv'
CALENDAR_FILE = RAW_DATA_DIR / 'calendar.csv'
NEIGHBOURHOODS_FILE = RAW_DATA_DIR / 'neighbourhoods.csv'
GEOJSON_FILE = RAW_DATA_DIR / 'neighbourhoods.geojson'

# Processed data files
PROCESSED_LISTINGS = PROCESSED_DATA_DIR / 'listings_clean.csv'
PROCESSED_REVIEWS = PROCESSED_DATA_DIR / 'reviews_clean.csv'
PROCESSED_CALENDAR = PROCESSED_DATA_DIR / 'calendar_clean.csv'

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'innsight_db'
COLLECTIONS = {
    'listings': 'listings',
    'reviews': 'reviews',
    'calendar': 'calendar',
    'neighbourhoods': 'neighbourhoods'
}

# Columns to keep from listings.csv
LISTINGS_COLUMNS = [
    'id', 'listing_url', 'name', 'description', 
    'neighborhood_overview', 'picture_url',
    'host_id', 'host_name', 'host_since', 'host_response_rate',
    'host_is_superhost', 'host_listings_count',
    'neighbourhood_cleansed', 'latitude', 'longitude',
    'property_type', 'room_type', 'accommodates',
    'bathrooms', 'bedrooms', 'beds', 'amenities',
    'price', 'minimum_nights', 'maximum_nights',
    'number_of_reviews', 'review_scores_rating',
    'review_scores_cleanliness', 'review_scores_location',
    'instant_bookable'
]

# Columns to keep from reviews.csv
REVIEWS_COLUMNS = [
    'listing_id', 'id', 'date', 'reviewer_id', 
    'reviewer_name', 'comments'
]

# Columns to keep from calendar.csv
CALENDAR_COLUMNS = [
    'listing_id', 'date', 'available', 'price',
    'minimum_nights', 'maximum_nights'
]

# Data validation rules
VALIDATION_RULES = {
    'listings': {
        'required_columns': ['id', 'name', 'latitude', 'longitude', 'price'],
        'numeric_columns': ['latitude', 'longitude', 'accommodates', 'bedrooms', 'beds'],
        'price_range': (0, 10000),  # Min and max reasonable price
        'coordinate_ranges': {
            'latitude': (52.3, 52.45),  # Amsterdam latitude bounds
            'longitude': (4.7, 5.0)      # Amsterdam longitude bounds
        }
    },
    'reviews': {
        'required_columns': ['listing_id', 'date', 'comments'],
        'min_comment_length': 10
    },
    'calendar': {
        'required_columns': ['listing_id', 'date', 'available']
    }
}

# ETL settings
CHUNK_SIZE = 10000  # Process data in chunks for large files
DATE_FORMAT = '%Y-%m-%d'
