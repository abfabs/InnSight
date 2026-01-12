#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
import re

class DataETL:
    """
    Fast data processing: listings, calendar, hosts
    """
    
    def __init__(self, city):
        self.city = city
        self.raw_path = Path(f'../data/raw/{city}')
        self.output_path = Path(f'../data/processed/{city}')
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def clean_price(self, price_str):
        if pd.isna(price_str):
            return np.nan
        if isinstance(price_str, (int, float)):
            return float(price_str)
        cleaned = re.sub(r'[€$,]', '', str(price_str))
        try:
            return float(cleaned)
        except:
            return np.nan
    
    def process_listings(self):
        print(f"Processing {self.city} listings...")
        
        listings = pd.read_csv(self.raw_path / 'listings.csv')
        
        essential_cols = {
            'id': 'listing_id',
            'name': 'listing_name',
            'host_id': 'host_id',
            'host_name': 'host_name',
            'neighbourhood_cleansed': 'neighbourhood',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'property_type': 'property_type',
            'room_type': 'room_type',
            'accommodates': 'accommodates',
            'bedrooms': 'bedrooms',
            'beds': 'beds',
            'price': 'price',
            'minimum_nights': 'minimum_nights',
            'maximum_nights': 'maximum_nights',
            'number_of_reviews': 'number_of_reviews',
            'review_scores_rating': 'review_scores_rating'
        }
        
        available = [col for col in essential_cols.keys() if col in listings.columns]
        listings_clean = listings[available].copy()
        listings_clean.rename(columns=essential_cols, inplace=True)
        
        listings_clean['price'] = listings_clean['price'].apply(self.clean_price)
        
        # Remove outliers
        Q1 = listings_clean['price'].quantile(0.01)
        Q3 = listings_clean['price'].quantile(0.99)
        listings_clean = listings_clean[
            (listings_clean['price'] >= Q1) & 
            (listings_clean['price'] <= Q3)
        ]
        
        listings_clean.dropna(subset=['listing_id', 'latitude', 'longitude', 'price', 'neighbourhood'], inplace=True)
        
        output_file = self.output_path / 'listings_clean.csv'
        listings_clean.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(listings_clean)} listings)")
        
        return listings_clean
    
    def process_calendar(self, listings):
        print(f"Processing {self.city} calendar data...")
        
        calendar = pd.read_csv(self.raw_path / 'calendar.csv')
        calendar = calendar[calendar['listing_id'].isin(listings['listing_id'])]
        
        calendar['date'] = pd.to_datetime(calendar['date'])
        calendar['year_month'] = calendar['date'].dt.to_period('M')
        calendar['is_available'] = calendar['available'].map({'t': 1, 'f': 0})
        
        monthly = calendar.groupby('year_month').agg({
            'is_available': ['sum', 'count']
        }).reset_index()
        
        monthly.columns = ['year_month', 'available_nights', 'total_nights']
        monthly['occupancy_rate'] = (1 - monthly['available_nights'] / monthly['total_nights']) * 100
        monthly['year_month'] = monthly['year_month'].astype(str)
        
        output_file = self.output_path / 'occupancy_monthly.csv'
        monthly.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(monthly)} months)")
        
        return monthly
    
    def create_neighborhood_stats(self, listings):
        print(f"Creating neighborhood statistics...")
        
        neighborhood_stats = listings.groupby('neighbourhood').agg({
            'listing_id': 'count',
            'price': ['mean', 'median', 'min', 'max'],
            'review_scores_rating': 'mean',
            'room_type': lambda x: x.mode()[0] if len(x) > 0 else 'Entire home/apt'
        }).reset_index()
        
        neighborhood_stats.columns = [
            'neighbourhood', 'total_listings', 
            'avg_price', 'median_price', 'min_price', 'max_price',
            'avg_rating', 'most_common_room_type'
        ]
        
        # Room type distribution
        room_type_dist = listings.groupby(['neighbourhood', 'room_type']).size().unstack(fill_value=0)
        room_type_dist = room_type_dist.div(room_type_dist.sum(axis=1), axis=0) * 100
        room_type_dist = room_type_dist.reset_index()
        
        neighborhood_stats = neighborhood_stats.merge(room_type_dist, on='neighbourhood', how='left')
        
        output_file = self.output_path / 'neighborhood_stats.csv'
        neighborhood_stats.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(neighborhood_stats)} neighborhoods)")
        
        return neighborhood_stats
    
    def create_top_hosts(self, listings):
        print(f"Creating top hosts data...")
        
        host_listings = listings.groupby(['host_id', 'host_name']).agg({
            'listing_id': 'count',
            'review_scores_rating': 'mean'
        }).reset_index()
        
        host_listings.columns = ['host_id', 'host_name', 'total_listings', 'avg_rating']
        host_listings = host_listings.sort_values('total_listings', ascending=False).head(20)
        
        output_file = self.output_path / 'top_hosts.csv'
        host_listings.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} (top 20)")
        
        return host_listings
    
    def run(self):
        print("=" * 60)
        print(f"DATA ETL: {self.city.upper()}")
        print("=" * 60)
        
        listings = self.process_listings()
        calendar = self.process_calendar(listings)
        neighborhood_stats = self.create_neighborhood_stats(listings)
        top_hosts = self.create_top_hosts(listings)
        
        print(f"\n✓ {self.city.upper()} DATA ETL COMPLETE!\n")


if __name__ == "__main__":
    cities = ['amsterdam', 'rome', 'prague']
    
    for city in cities:
        etl = DataETL(city)
        etl.run()
        print()
