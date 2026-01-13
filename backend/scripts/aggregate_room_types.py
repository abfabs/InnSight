#!/usr/bin/env python3
"""
Aggregate room type distribution by neighborhood and city
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from config import Config

def aggregate_room_types():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]
    
    print("🔄 Aggregating room type distribution...")
    
    # Drop existing collection
    db.room_type_distribution.drop()
    
    cities = ['amsterdam', 'prague', 'rome']
    
    for city in cities:
        print(f"\n📊 Processing {city}...")
        
        # 1. Get overall city room type distribution
        city_pipeline = [
            {'$match': {'city': city, 'room_type': {'$ne': None}}},
            {'$group': {
                '_id': '$room_type',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        city_results = list(db.listings_clean.aggregate(city_pipeline))
        
        if city_results:
            # Calculate total for percentages
            total_city = sum(r['count'] for r in city_results)
            
            room_types = {}
            for r in city_results:
                room_types[r['_id']] = {
                    'count': r['count'],
                    'percentage': round((r['count'] / total_city) * 100, 2)
                }
            
            city_doc = {
                'city': city,
                'neighbourhood': None,
                'level': 'city',
                'total_listings': total_city,
                'room_types': room_types
            }
            db.room_type_distribution.insert_one(city_doc)
            print(f"  ✅ City-level: {total_city} listings")
        
        # 2. Get neighborhood-level room type distribution
        neighborhoods = db.listings_clean.distinct('neighbourhood', {'city': city, 'neighbourhood': {'$ne': None}})
        
        for neigh in neighborhoods:
            neigh_pipeline = [
                {'$match': {'city': city, 'neighbourhood': neigh, 'room_type': {'$ne': None}}},
                {'$group': {
                    '_id': '$room_type',
                    'count': {'$sum': 1}
                }},
                {'$sort': {'count': -1}}
            ]
            
            neigh_results = list(db.listings_clean.aggregate(neigh_pipeline))
            
            if neigh_results:
                total_neigh = sum(r['count'] for r in neigh_results)
                
                room_types = {}
                for r in neigh_results:
                    room_types[r['_id']] = {
                        'count': r['count'],
                        'percentage': round((r['count'] / total_neigh) * 100, 2)
                    }
                
                neigh_doc = {
                    'city': city,
                    'neighbourhood': neigh,
                    'level': 'neighbourhood',
                    'total_listings': total_neigh,
                    'room_types': room_types
                }
                db.room_type_distribution.insert_one(neigh_doc)
        
        print(f"  ✅ Neighborhoods: {len(neighborhoods)}")
    
    # Create indexes
    db.room_type_distribution.create_index([('city', 1), ('level', 1)])
    db.room_type_distribution.create_index([('city', 1), ('neighbourhood', 1)])
    
    total = db.room_type_distribution.count_documents({})
    print(f"\n✅ Room type distribution complete: {total} documents")

if __name__ == '__main__':
    aggregate_room_types()
