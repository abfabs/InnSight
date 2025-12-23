# backend/data/etl_pipeline.py

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional
from .config import (
    LISTINGS_FILE, REVIEWS_FILE, CALENDAR_FILE,
    NEIGHBOURHOODS_FILE, GEOJSON_FILE,
    PROCESSED_LISTINGS, PROCESSED_REVIEWS, PROCESSED_CALENDAR,
    PROCESSED_DATA_DIR, CHUNK_SIZE
)
from .data_cleaner import DataCleaner
from .data_validator import DataValidator
from .geojson_processor import GeoJSONProcessor
from .utils import log_data_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """Main ETL pipeline orchestrator."""
    
    def __init__(self):
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.geojson_processor = GeoJSONProcessor()
        
        # Ensure processed directory exists
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def extract_listings(self, filepath: Path = LISTINGS_FILE) -> pd.DataFrame:
        """
        Extract listings data from CSV.
        
        Args:
            filepath: Path to listings CSV file
            
        Returns:
            Raw listings DataFrame
        """
        logger.info(f"Extracting listings from {filepath}...")
        
        try:
            df = pd.read_csv(filepath, low_memory=False)
            logger.info(f"Extracted {len(df)} listings")
            return df
        except FileNotFoundError:
            logger.error(f"Listings file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading listings file: {e}")
            raise
    
    def extract_reviews(self, filepath: Path = REVIEWS_FILE, 
                       use_chunks: bool = True) -> pd.DataFrame:
        """
        Extract reviews data from CSV (may be large file).
        
        Args:
            filepath: Path to reviews CSV file
            use_chunks: Whether to read in chunks
            
        Returns:
            Raw reviews DataFrame
        """
        logger.info(f"Extracting reviews from {filepath}...")
        
        try:
            if use_chunks and filepath.stat().st_size > 50 * 1024 * 1024:  # > 50MB
                logger.info("Large file detected, reading in chunks...")
                chunks = []
                
                for chunk in pd.read_csv(filepath, chunksize=CHUNK_SIZE):
                    chunks.append(chunk)
                
                df = pd.concat(chunks, ignore_index=True)
            else:
                df = pd.read_csv(filepath)
            
            logger.info(f"Extracted {len(df)} reviews")
            return df
        
        except FileNotFoundError:
            logger.error(f"Reviews file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading reviews file: {e}")
            raise
    
    def extract_calendar(self, filepath: Path = CALENDAR_FILE,
                        use_chunks: bool = True) -> pd.DataFrame:
        """
        Extract calendar data from CSV (may be large file).
        
        Args:
            filepath: Path to calendar CSV file
            use_chunks: Whether to read in chunks
            
        Returns:
            Raw calendar DataFrame
        """
        logger.info(f"Extracting calendar from {filepath}...")
        
        try:
            if use_chunks and filepath.stat().st_size > 50 * 1024 * 1024:  # > 50MB
                logger.info("Large file detected, reading in chunks...")
                chunks = []
                
                for chunk in pd.read_csv(filepath, chunksize=CHUNK_SIZE):
                    chunks.append(chunk)
                
                df = pd.concat(chunks, ignore_index=True)
            else:
                df = pd.read_csv(filepath)
            
            logger.info(f"Extracted {len(df)} calendar entries")
            return df
        
        except FileNotFoundError:
            logger.error(f"Calendar file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading calendar file: {e}")
            raise
    
    def extract_neighbourhoods(self, filepath: Path = NEIGHBOURHOODS_FILE) -> pd.DataFrame:
        """
        Extract neighbourhoods data from CSV.
        
        Args:
            filepath: Path to neighbourhoods CSV file
            
        Returns:
            Raw neighbourhoods DataFrame
        """
        logger.info(f"Extracting neighbourhoods from {filepath}...")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Extracted {len(df)} neighbourhoods")
            return df
        
        except FileNotFoundError:
            logger.error(f"Neighbourhoods file not found: {filepath}")
            raise
        except Exception as e:
            logger.error(f"Error reading neighbourhoods file: {e}")
            raise
    
    def process_listings(self) -> pd.DataFrame:
        """
        Full ETL process for listings.
        
        Returns:
            Clean and validated listings DataFrame
        """
        logger.info("\n" + "="*60)
        logger.info("PROCESSING LISTINGS")
        logger.info("="*60)
        
        # Extract
        df = self.extract_listings()
        
        # Transform (Clean)
        df = self.cleaner.clean_listings(df)
        
        # Validate
        df, report = self.validator.validate_listings(df)
        self.validator.print_report(report, "Listings")
        
        # Load (Save to processed)
        df.to_csv(PROCESSED_LISTINGS, index=False)
        logger.info(f"Saved cleaned listings to {PROCESSED_LISTINGS}")
        
        return df
    
    def process_reviews(self) -> pd.DataFrame:
        """
        Full ETL process for reviews.
        
        Returns:
            Clean and validated reviews DataFrame
        """
        logger.info("\n" + "="*60)
        logger.info("PROCESSING REVIEWS")
        logger.info("="*60)
        
        # Extract
        df = self.extract_reviews()
        
        # Transform (Clean)
        df = self.cleaner.clean_reviews(df)
        
        # Validate
        df, report = self.validator.validate_reviews(df)
        self.validator.print_report(report, "Reviews")
        
        # Load (Save to processed)
        df.to_csv(PROCESSED_REVIEWS, index=False)
        logger.info(f"Saved cleaned reviews to {PROCESSED_REVIEWS}")
        
        return df
    
    def process_calendar(self) -> pd.DataFrame:
        """
        Full ETL process for calendar.
        
        Returns:
            Clean and validated calendar DataFrame
        """
        logger.info("\n" + "="*60)
        logger.info("PROCESSING CALENDAR")
        logger.info("="*60)
        
        # Extract
        df = self.extract_calendar()
        
        # Transform (Clean)
        df = self.cleaner.clean_calendar(df)
        
        # Validate
        df, report = self.validator.validate_calendar(df)
        self.validator.print_report(report, "Calendar")
        
        # Load (Save to processed)
        df.to_csv(PROCESSED_CALENDAR, index=False)
        logger.info(f"Saved cleaned calendar to {PROCESSED_CALENDAR}")
        
        return df
    
    def process_neighbourhoods(self) -> pd.DataFrame:
        """
        Full ETL process for neighbourhoods.
        
        Returns:
            Clean neighbourhoods DataFrame
        """
        logger.info("\n" + "="*60)
        logger.info("PROCESSING NEIGHBOURHOODS")
        logger.info("="*60)
        
        # Extract
        df = self.extract_neighbourhoods()
        
        # Transform (Clean)
        df = self.cleaner.clean_neighbourhoods(df)
        
        # Load (Save to processed)
        processed_path = PROCESSED_DATA_DIR / 'neighbourhoods_clean.csv'
        df.to_csv(processed_path, index=False)
        logger.info(f"Saved cleaned neighbourhoods to {processed_path}")
        
        return df
    
    def process_geojson(self) -> Dict:
        """
        Process GeoJSON file.
        
        Returns:
            Processed GeoJSON data
        """
        logger.info("\n" + "="*60)
        logger.info("PROCESSING GEOJSON")
        logger.info("="*60)
        
        # Load and validate
        self.geojson_processor.load_geojson(GEOJSON_FILE)
        self.geojson_processor.validate_geojson()
        
        # Extract neighbourhood list
        neighbourhoods = self.geojson_processor.extract_neighbourhoods()
        logger.info(f"Found neighbourhoods: {neighbourhoods}")
        
        # Simplify for better performance
        simplified = self.geojson_processor.simplify_geojson(precision=5)
        
        # Save simplified version
        simplified_path = PROCESSED_DATA_DIR / 'neighbourhoods_simplified.geojson'
        self.geojson_processor.save_geojson(simplified_path, simplified)
        
        return simplified
    
    def run_full_pipeline(self) -> Dict[str, pd.DataFrame]:
        """
        Run the complete ETL pipeline for all datasets.
        
        Returns:
            Dictionary with all processed DataFrames
        """
        logger.info("\n" + "#"*60)
        logger.info("# STARTING FULL ETL PIPELINE")
        logger.info("#"*60 + "\n")
        
        results = {}
        
        try:
            # Process all datasets
            results['listings'] = self.process_listings()
            results['reviews'] = self.process_reviews()
            results['calendar'] = self.process_calendar()
            results['neighbourhoods'] = self.process_neighbourhoods()
            results['geojson'] = self.process_geojson()
            
            logger.info("\n" + "#"*60)
            logger.info("# ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("#"*60)
            
            # Print summary
            logger.info("\nFinal Summary:")
            logger.info(f"  Listings: {len(results['listings'])} rows")
            logger.info(f"  Reviews: {len(results['reviews'])} rows")
            logger.info(f"  Calendar: {len(results['calendar'])} rows")
            logger.info(f"  Neighbourhoods: {len(results['neighbourhoods'])} rows")
            logger.info(f"  GeoJSON features: {len(results['geojson'].get('features', []))}")
            
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            raise
        
        return results


def main():
    """Run ETL pipeline from command line."""
    pipeline = ETLPipeline()
    pipeline.run_full_pipeline()


if __name__ == "__main__":
    main()
