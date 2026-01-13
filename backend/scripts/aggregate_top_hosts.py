#!/usr/bin/env python3
"""
Aggregate top 10 hosts by total listings per neighborhood and city
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from config import Config

def aggregate_top_hosts():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]
    
    print("🔄 Aggregating top hosts...")
    
    # Drop existing collection
    db.top_hosts.drop()
    
    cities = ['amsterdam', 'prague', 'rome']
    
    for city in cities:
        print(f"\n📊 Processing {city}...")
        
        # 1. Get top 10 hosts city-wide
        city_pipeline = [
            {'$match': {'city': city, 'host_name': {'$ne': None}}},
            {'$group': {
                '_id': {
                    'host_id': '$host_id',
                    'host_name': '$host_name'
                },
                'total_listings': {'$sum': 1},
                'avg_price': {'$avg': '$price'},
                'avg_rating': {'$avg': '$review_score_rating'}
            }},
            {'$sort': {'total_listings': -1}},
            {'$limit': 10},
            {'$project': {
                'host_id': '$_id.host_id',
                'host_name': '$_id.host_name',
                'total_listings': 1,
                'avg_price': {'$round': ['$avg_price', 2]},
                'avg_rating': {'$round': ['$avg_rating', 2]},
                '_id': 0
            }}
        ]
        
        city_hosts = list(db.listings_clean.aggregate(city_pipeline))
        
        if city_hosts:
            city_doc = {
                'city': city,
                'neighbourhood': None,
                'level': 'city',
                'top_hosts': city_hosts
            }
            db.top_hosts.insert_one(city_doc)
            print(f"  ✅ City-level: {len(city_hosts)} hosts")
        
        # 2. Get top 10 hosts per neighborhood
        neighborhoods = db.listings_clean.distinct('neighbourhood', {'city': city, 'neighbourhood': {'$ne': None}})
        
        for neigh in neighborhoods:
            neigh_pipeline = [
                {'$match': {'city': city, 'neighbourhood': neigh, 'host_name': {'$ne': None}}},
                {'$group': {
                    '_id': {
                        'host_id': '$host_id',
                        'host_name': '$host_name'
                    },
                    'total_listings': {'$sum': 1},
                    'avg_price': {'$avg': '$price'},
                    'avg_rating': {'$avg': '$review_score_rating'}
                }},
                {'$sort': {'total_listings': -1}},
                {'$limit': 10},
                {'$project': {
                    'host_id': '$_id.host_id',
                    'host_name': '$_id.host_name',
                    'total_listings': 1,
                    'avg_price': {'$round': ['$avg_price', 2]},
                    'avg_rating': {'$round': ['$avg_rating', 2]},
                    '_id': 0
                }}
            ]
            
            neigh_hosts = list(db.listings_clean.aggregate(neigh_pipeline))
            
            if neigh_hosts:
                neigh_doc = {
                    'city': city,
                    'neighbourhood': neigh,
                    'level': 'neighbourhood',
                    'top_hosts': neigh_hosts
                }
                db.top_hosts.insert_one(neigh_doc)
        
        print(f"  ✅ Neighborhoods: {len(neighborhoods)}")
    
    # Create indexes
    db.top_hosts.create_index([('city', 1), ('level', 1)])
    db.top_hosts.create_index([('city', 1), ('neighbourhood', 1)])
    
    total = db.top_hosts.count_documents({})
    print(f"\n✅ Top hosts aggregation complete: {total} documents")

if __name__ == '__main__':
    aggregate_top_hosts()
