#!/usr/bin/env python3

import sys
from pathlib import Path
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

try:
    from utils.db import get_db
    db = get_db()
except:
    from pymongo import MongoClient
    client = MongoClient()
    db = client.innsight_db

CHUNK_SIZE = 10000

def upload_file(city_name, csv_path):
    collection_name = csv_path.stem
    coll = db[collection_name]
    
    print(f"{city_name}/{csv_path.name}")
    
    total = 0
    chunk_limit = 10 if csv_path.name == 'reviews_sentiment.csv' else None  # 100k max
    
    for chunk_num, df_chunk in enumerate(pd.read_csv(csv_path, chunksize=CHUNK_SIZE), 1):
        if chunk_limit and chunk_num > chunk_limit:
            print(f"  ⏹️  STOPPED reviews_sentiment at {chunk_limit*CHUNK_SIZE:,}")
            break
        
        df_chunk = df_chunk.where(pd.notnull(df_chunk), None)
        df_chunk["city"] = city_name
        
        docs = df_chunk.to_dict('records')
        result = coll.insert_many(docs, ordered=False)
        total += len(result.inserted_ids)
        print(f"  Chunk {chunk_num}: {len(docs):,} rows")
    
    return total

def process_city(city_dir):
    city_name = city_dir.name
    print(f"\n🏙️  {city_name}")
    
    expected = [
        'listings_clean.csv', 
        'neighborhood_stats.csv', 
        'occupancy_monthly.csv', 
        'top_hosts.csv', 
        'review_words.csv', 
        'reviews_sentiment.csv',
        'listing_sentiment.csv', 
        'neighborhood_sentiment.csv', 
        'listings_map.csv'
    ]
    
    total = 0
    for f in expected:
        csv_path = city_dir / f
        if csv_path.exists():
            total += upload_file(city_name, csv_path)
    
    print(f"✅ {city_name}: {total:,}")
    return total

def main():
    base_path = BACKEND_DIR / "data" / "processed"
    city_folders = [p for p in base_path.iterdir() if p.is_dir()]
    print(f"Found cities: {[p.name for p in city_folders]}")
    
    grand_total = 0
    for city_dir in sorted(city_folders):
        grand_total += process_city(city_dir)
    
    print(f"\n🎉 COMPLETE: {grand_total:,} TOTAL ROWS")
    print("✅ Dashboard ready! curl http://localhost:5000/api/listings?city=amsterdam")

if __name__ == "__main__":
    main()
