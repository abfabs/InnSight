#!/usr/bin/env python3
"""
Aggregate room type distribution by neighborhood and city

Input: listings_clean
Output: room_type_distribution
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import MongoClient
from config import Config


def _detect_neighborhood_field(db, city: str) -> str:
    """
    Some collections historically had 'neighbourhood' (UK spelling).
    Prefer canonical 'neighborhood'. Fall back if needed.
    """
    sample = db.listings_clean.find_one({'city': city})
    if not sample:
        return 'neighborhood'
    if 'neighborhood' in sample:
        return 'neighborhood'
    if 'neighbourhood' in sample:
        return 'neighbourhood'
    return 'neighborhood'


def aggregate_room_types():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]

    print("🔄 Aggregating room type distribution...")

    # Drop existing collection
    db.room_type_distribution.drop()

    cities = ['amsterdam', 'rome', 'prague', 'sicily', 'bordeaux', 'crete']

    for city in cities:
        print(f"\n📊 Processing {city}...")

        neigh_field = _detect_neighborhood_field(db, city)

        # ----------------------------
        # 1) CITY LEVEL
        # ----------------------------
        city_pipeline = [
            {'$match': {'city': city, 'room_type': {'$ne': None}}},
            {'$group': {'_id': '$room_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
        ]

        city_results = list(db.listings_clean.aggregate(city_pipeline))

        if city_results:
            total_city = sum(r['count'] for r in city_results)

            room_types = {
                r['_id']: {
                    'count': int(r['count']),
                    'percentage': round((r['count'] / total_city) * 100, 2) if total_city else 0.0
                }
                for r in city_results
            }

            city_doc = {
                'city': city,
                'neighborhood': None,
                'level': 'city',
                'total_listings': int(total_city),
                'room_types': room_types
            }
            db.room_type_distribution.insert_one(city_doc)
            print(f"  ✅ City-level: {total_city:,} listings")
        else:
            print("  ⚠️  No city room_type data found")

        # ----------------------------
        # 2) NEIGHBORHOOD LEVEL
        # ----------------------------
        neighborhoods = db.listings_clean.distinct(
            neigh_field,
            {'city': city, neigh_field: {'$ne': None}}
        )

        inserted = 0
        for neigh in neighborhoods:
            neigh_pipeline = [
                {'$match': {'city': city, neigh_field: neigh, 'room_type': {'$ne': None}}},
                {'$group': {'_id': '$room_type', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
            ]

            neigh_results = list(db.listings_clean.aggregate(neigh_pipeline))
            if not neigh_results:
                continue

            total_neigh = sum(r['count'] for r in neigh_results)
            room_types = {
                r['_id']: {
                    'count': int(r['count']),
                    'percentage': round((r['count'] / total_neigh) * 100, 2) if total_neigh else 0.0
                }
                for r in neigh_results
            }

            neigh_doc = {
                'city': city,
                'neighborhood': neigh,       # canonical output field
                'level': 'neighborhood',
                'total_listings': int(total_neigh),
                'room_types': room_types
            }
            db.room_type_distribution.insert_one(neigh_doc)
            inserted += 1

        print(f"  ✅ Neighborhoods: {inserted}")

    # Indexes
    db.room_type_distribution.create_index([('city', 1), ('level', 1)])
    db.room_type_distribution.create_index([('city', 1), ('neighborhood', 1)])

    total = db.room_type_distribution.count_documents({})
    print(f"\n✅ Room type distribution complete: {total} documents")


def main():
    """Callable entrypoint for pipeline imports."""
    aggregate_room_types()
    return True


if __name__ == '__main__':
    main()
