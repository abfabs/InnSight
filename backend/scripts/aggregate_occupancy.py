#!/usr/bin/env python3
"""
Aggregate monthly occupancy from calendar data by neighborhood and city
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from pymongo import MongoClient
from config import Config

def aggregate_occupancy():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]
    
    print("🔄 Aggregating occupancy by month...")
    
    # Drop existing collection
    db.occupancy_by_month.drop()
    
    cities = ['amsterdam', 'prague', 'rome']
    base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    
    for city in cities:
        print(f"\n📊 Processing {city}...")
        
        calendar_path = os.path.join(base_path, city, 'calendar.csv')
        
        if not os.path.exists(calendar_path):
            print(f"  ⚠️  Calendar file not found: {calendar_path}")
            continue
        
        # Load calendar data
        calendar_df = pd.read_csv(calendar_path)
        calendar_df['date'] = pd.to_datetime(calendar_df['date'])
        calendar_df['month'] = calendar_df['date'].dt.to_period('M').astype(str)
        calendar_df['occupied'] = calendar_df['available'].apply(lambda x: 0 if x == 't' else 1)
        
        # Get listing to neighborhood mapping
        listings = list(db.listings_clean.find(
            {'city': city},
            {'listing_id': 1, 'neighbourhood': 1}
        ))
        
        listing_to_neigh = {str(l['listing_id']): l.get('neighbourhood') for l in listings}
        
        # Add neighborhood to calendar
        calendar_df['neighbourhood'] = calendar_df['listing_id'].astype(str).map(listing_to_neigh)
        calendar_df = calendar_df.dropna(subset=['neighbourhood'])
        
        # 1. City-level occupancy by month
        city_monthly = calendar_df.groupby('month').agg({
            'occupied': 'sum',
            'listing_id': 'count'
        }).reset_index()
        
        city_monthly['occupancy_rate'] = (city_monthly['occupied'] / city_monthly['listing_id'] * 100).round(2)
        
        monthly_data = []
        for _, row in city_monthly.iterrows():
            monthly_data.append({
                'month': row['month'],
                'occupied_nights': int(row['occupied']),
                'total_nights': int(row['listing_id']),
                'occupancy_rate': float(row['occupancy_rate'])
            })
        
        city_doc = {
            'city': city,
            'neighbourhood': None,
            'level': 'city',
            'monthly_occupancy': monthly_data
        }
        db.occupancy_by_month.insert_one(city_doc)
        print(f"  ✅ City-level: {len(monthly_data)} months")
        
        # 2. Neighborhood-level occupancy
        neighborhoods = calendar_df['neighbourhood'].unique()
        
        for neigh in neighborhoods:
            neigh_df = calendar_df[calendar_df['neighbourhood'] == neigh]
            
            neigh_monthly = neigh_df.groupby('month').agg({
                'occupied': 'sum',
                'listing_id': 'count'
            }).reset_index()
            
            neigh_monthly['occupancy_rate'] = (neigh_monthly['occupied'] / neigh_monthly['listing_id'] * 100).round(2)
            
            monthly_data = []
            for _, row in neigh_monthly.iterrows():
                monthly_data.append({
                    'month': row['month'],
                    'occupied_nights': int(row['occupied']),
                    'total_nights': int(row['listing_id']),
                    'occupancy_rate': float(row['occupancy_rate'])
                })
            
            neigh_doc = {
                'city': city,
                'neighbourhood': neigh,
                'level': 'neighbourhood',
                'monthly_occupancy': monthly_data
            }
            db.occupancy_by_month.insert_one(neigh_doc)
        
        print(f"  ✅ Neighborhoods: {len(neighborhoods)}")
    
    # Create indexes
    db.occupancy_by_month.create_index([('city', 1), ('level', 1)])
    db.occupancy_by_month.create_index([('city', 1), ('neighbourhood', 1)])
    
    total = db.occupancy_by_month.count_documents({})
    print(f"\n✅ Occupancy aggregation complete: {total} documents")

if __name__ == '__main__':
    aggregate_occupancy()
