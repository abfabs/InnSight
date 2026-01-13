#!/usr/bin/env python3
"""
Aggregate sentiment data by neighborhood and city for dashboard filtering
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from config import Config

def aggregate_sentiment():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]
    
    print("🔄 Aggregating sentiment summary...")
    
    # Drop existing collection
    db.sentiment_summary.drop()
    
    cities = ['amsterdam', 'prague', 'rome']
    
    for city in cities:
        print(f"\n📊 Processing {city}...")
        
        # 1. Get overall city sentiment (FIXED: snake_case field names)
        city_pipeline = [
            {'$match': {'city': city}},
            {'$group': {
                '_id': None,
                'sentiment_mean': {'$avg': '$sentiment_mean'},
                'sentiment_median': {'$avg': '$sentiment_median'},
                'total_reviews': {'$sum': '$total_reviews'},
                'positive': {'$avg': '$positive'},
                'neutral': {'$avg': '$neutral'},
                'negative': {'$avg': '$negative'}
            }}
        ]
        
        city_result = list(db.neighborhood_sentiment.aggregate(city_pipeline))
        
        if city_result and city_result[0]['sentiment_mean'] is not None:
            city_doc = {
                'city': city,
                'neighbourhood': None,  # City-level aggregate
                'level': 'city',
                'sentiment_mean': round(city_result[0]['sentiment_mean'], 4),
                'sentiment_median': round(city_result[0]['sentiment_median'], 4),
                'total_reviews': city_result[0]['total_reviews'],
                'positive': round(city_result[0]['positive'], 4),
                'neutral': round(city_result[0]['neutral'], 4),
                'negative': round(city_result[0]['negative'], 4)
            }
            db.sentiment_summary.insert_one(city_doc)
            print(f"  ✅ City-level: {city_result[0]['total_reviews']} reviews")
        else:
            print(f"  ⚠️  No sentiment data found for {city}")
            continue
        
        # 2. Get neighborhood-level sentiment (FIXED: no need to rename fields)
        neigh_pipeline = [
            {'$match': {'city': city}},
            {'$project': {
                'neighbourhood': 1,
                'sentiment_mean': 1,
                'sentiment_median': 1,
                'total_reviews': 1,
                'positive': 1,
                'neutral': 1,
                'negative': 1
            }}
        ]
        
        neigh_results = list(db.neighborhood_sentiment.aggregate(neigh_pipeline))
        
        for neigh in neigh_results:
            if neigh.get('sentiment_mean') is not None:
                neigh_doc = {
                    'city': city,
                    'neighbourhood': neigh['neighbourhood'],
                    'level': 'neighbourhood',
                    'sentiment_mean': round(neigh['sentiment_mean'], 4),
                    'sentiment_median': round(neigh['sentiment_median'], 4),
                    'total_reviews': neigh['total_reviews'],
                    'positive': round(neigh['positive'], 4),
                    'neutral': round(neigh['neutral'], 4),
                    'negative': round(neigh['negative'], 4)
                }
                db.sentiment_summary.insert_one(neigh_doc)
        
        print(f"  ✅ Neighborhoods: {len(neigh_results)}")
    
    # Create indexes
    db.sentiment_summary.create_index([('city', 1), ('level', 1)])
    db.sentiment_summary.create_index([('city', 1), ('neighbourhood', 1)])
    
    total = db.sentiment_summary.count_documents({})
    print(f"\n✅ Sentiment summary complete: {total} documents")

if __name__ == '__main__':
    aggregate_sentiment()
