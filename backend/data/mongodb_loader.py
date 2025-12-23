# backend/data/mongodb_loader.py

import pandas as pd
import json
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, BulkWriteError
from typing import Dict, List
from pathlib import Path
from .config import (
    MONGO_URI, DB_NAME, COLLECTIONS,
    PROCESSED_LISTINGS, PROCESSED_REVIEWS, PROCESSED_CALENDAR,
    PROCESSED_DATA_DIR
)
from .geojson_processor import GeoJSONProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBLoader:
    """Load cleaned data into MongoDB."""
    
    def __init__(self, uri: str = MONGO_URI, db_name: str = DB_NAME):
        """
        Initialize MongoDB connection.
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB."""
        try:
            logger.info(f"Connecting to MongoDB at {self.uri}...")
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.db_name]
            logger.info(f"Connected to database: {self.db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def drop_collections(self):
        """Drop all existing collections (use with caution)."""
        logger.warning("Dropping all existing collections...")
        
        for collection_name in COLLECTIONS.values():
            if collection_name in self.db.list_collection_names():
                self.db[collection_name].drop()
                logger.info(f"Dropped collection: {collection_name}")
    
    def create_indexes(self):
        """Create indexes for better query performance."""
        logger.info("Creating indexes...")
        
        # Listings indexes
        listings = self.db[COLLECTIONS['listings']]
        listings.create_index([('id', ASCENDING)], unique=True)
        listings.create_index([('neighbourhood_cleansed', ASCENDING)])
        listings.create_index([('price', ASCENDING)])
        listings.create_index([('latitude', ASCENDING), ('longitude', ASCENDING)])
        listings.create_index([('room_type', ASCENDING)])
        logger.info("Created indexes for listings")
        
        # Reviews indexes
        reviews = self.db[COLLECTIONS['reviews']]
        reviews.create_index([('id', ASCENDING)], unique=True)
        reviews.create_index([('listing_id', ASCENDING)])
        reviews.create_index([('date', DESCENDING)])
        logger.info("Created indexes for reviews")
        
        # Calendar indexes
        calendar = self.db[COLLECTIONS['calendar']]
        calendar.create_index([('listing_id', ASCENDING), ('date', ASCENDING)], unique=True)
        calendar.create_index([('date', ASCENDING)])
        calendar.create_index([('available', ASCENDING)])
        logger.info("Created indexes for calendar")
        
        # Neighbourhoods indexes
        neighbourhoods = self.db[COLLECTIONS['neighbourhoods']]
        neighbourhoods.create_index([('neighbourhood', ASCENDING)], unique=True)
        logger.info("Created indexes for neighbourhoods")
    
    def load_listings(self, filepath: Path = PROCESSED_LISTINGS) -> int:
        """
        Load listings into MongoDB.
        
        Args:
            filepath: Path to cleaned listings CSV
            
        Returns:
            Number of documents inserted
        """
        logger.info(f"Loading listings from {filepath}...")
        
        df = pd.read_csv(filepath)
        
        # Convert DataFrame to list of dicts
        records = df.to_dict('records')
        
        # Convert NaN to None for MongoDB
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                # Convert numpy types to Python types
                elif hasattr(value, 'item'):
                    record[key] = value.item()
        
        collection = self.db[COLLECTIONS['listings']]
        
        try:
            # Use ordered=False to continue on errors
            result = collection.insert_many(records, ordered=False)
            inserted = len(result.inserted_ids)
            logger.info(f"Inserted {inserted} listings")
            return inserted
            
        except BulkWriteError as e:
            logger.warning(f"Some listings failed to insert: {e.details['nInserted']} succeeded")
            return e.details['nInserted']
    
    def load_reviews(self, filepath: Path = PROCESSED_REVIEWS, 
                     batch_size: int = 10000) -> int:
        """
        Load reviews into MongoDB in batches.
        
        Args:
            filepath: Path to cleaned reviews CSV
            batch_size: Number of records per batch
            
        Returns:
            Number of documents inserted
        """
        logger.info(f"Loading reviews from {filepath}...")
        
        collection = self.db[COLLECTIONS['reviews']]
        total_inserted = 0
        
        # Read in chunks for memory efficiency
        for chunk_num, chunk in enumerate(pd.read_csv(filepath, chunksize=batch_size)):
            logger.info(f"Processing batch {chunk_num + 1}...")
            
            records = chunk.to_dict('records')
            
            # Clean records
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif hasattr(value, 'item'):
                        record[key] = value.item()
            
            try:
                result = collection.insert_many(records, ordered=False)
                total_inserted += len(result.inserted_ids)
                
            except BulkWriteError as e:
                total_inserted += e.details['nInserted']
                logger.warning(f"Some reviews in batch failed to insert")
        
        logger.info(f"Inserted {total_inserted} reviews total")
        return total_inserted
    
    def load_calendar(self, filepath: Path = PROCESSED_CALENDAR,
                     batch_size: int = 10000) -> int:
        """
        Load calendar into MongoDB in batches.
        
        Args:
            filepath: Path to cleaned calendar CSV
            batch_size: Number of records per batch
            
        Returns:
            Number of documents inserted
        """
        logger.info(f"Loading calendar from {filepath}...")
        
        collection = self.db[COLLECTIONS['calendar']]
        total_inserted = 0
        
        # Read in chunks for memory efficiency
        for chunk_num, chunk in enumerate(pd.read_csv(filepath, chunksize=batch_size)):
            logger.info(f"Processing batch {chunk_num + 1}...")
            
            records = chunk.to_dict('records')
            
            # Clean records
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif hasattr(value, 'item'):
                        record[key] = value.item()
            
            try:
                result = collection.insert_many(records, ordered=False)
                total_inserted += len(result.inserted_ids)
                
            except BulkWriteError as e:
                total_inserted += e.details['nInserted']
                logger.warning(f"Some calendar entries in batch failed to insert")
        
        logger.info(f"Inserted {total_inserted} calendar entries total")
        return total_inserted
    
    def load_neighbourhoods(self) -> int:
        """
        Load neighbourhoods with GeoJSON into MongoDB.
        
        Returns:
            Number of documents inserted
        """
        logger.info("Loading neighbourhoods...")
        
        # Load CSV
        csv_path = PROCESSED_DATA_DIR / 'neighbourhoods_clean.csv'
        df = pd.read_csv(csv_path)
        
        # Load GeoJSON
        geojson_path = PROCESSED_DATA_DIR / 'neighbourhoods_simplified.geojson'
        processor = GeoJSONProcessor()
        processor.load_geojson(geojson_path)
        geo_docs = processor.prepare_for_mongodb()
        
        # Merge CSV and GeoJSON data
        records = []
        for _, row in df.iterrows():
            neighbourhood_name = row['neighbourhood']
            
            # Find matching GeoJSON
            geo_data = next(
                (doc for doc in geo_docs if doc['neighbourhood'] == neighbourhood_name),
                None
            )
            
            record = {
                'neighbourhood': neighbourhood_name,
                'neighbourhood_group': row['neighbourhood_group'] if pd.notna(row['neighbourhood_group']) else None
            }
            
            if geo_data:
                record['geometry'] = geo_data['geometry']
                record['bounds'] = geo_data.get('bounds')
            
            records.append(record)
        
        collection = self.db[COLLECTIONS['neighbourhoods']]
        
        try:
            result = collection.insert_many(records, ordered=False)
            inserted = len(result.inserted_ids)
            logger.info(f"Inserted {inserted} neighbourhoods")
            return inserted
            
        except BulkWriteError as e:
            logger.warning(f"Some neighbourhoods failed to insert: {e.details['nInserted']} succeeded")
            return e.details['nInserted']
    
    def load_all(self, drop_existing: bool = False):
        """
        Load all data into MongoDB.
        
        Args:
            drop_existing: Whether to drop existing collections first
        """
        logger.info("\n" + "="*60)
        logger.info("LOADING DATA INTO MONGODB")
        logger.info("="*60)
        
        self.connect()
        
        try:
            if drop_existing:
                self.drop_collections()
            
            # Load all datasets
            listings_count = self.load_listings()
            reviews_count = self.load_reviews()
            calendar_count = self.load_calendar()
            neighbourhoods_count = self.load_neighbourhoods()
            
            # Create indexes
            self.create_indexes()
            
            logger.info("\n" + "="*60)
            logger.info("MONGODB LOADING COMPLETE")
            logger.info("="*60)
            logger.info(f"\nSummary:")
            logger.info(f"  Listings: {listings_count}")
            logger.info(f"  Reviews: {reviews_count}")
            logger.info(f"  Calendar: {calendar_count}")
            logger.info(f"  Neighbourhoods: {neighbourhoods_count}")
            
        finally:
            self.disconnect()


def main():
    """Run MongoDB loader from command line."""
    loader = MongoDBLoader()
    loader.load_all(drop_existing=True)


if __name__ == "__main__":
    main()
