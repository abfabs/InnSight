#!/usr/bin/env python3
"""
Aggregate top 10 hosts by total listings per neighborhood and city.

Input: listings_clean
Output: top_hosts_agg
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymongo import MongoClient
from config import Config


def _detect_neighborhood_field(db, city: str) -> str:
    sample = db.listings_clean.find_one({"city": city})
    if not sample:
        return "neighborhood"
    if "neighborhood" in sample:
        return "neighborhood"
    if "neighbourhood" in sample:
        return "neighbourhood"
    return "neighborhood"


def _safe_avg_rating_in_range(field_name: str, lo: float = 0.0, hi: float = 5.0):
    """
    NaN-proof rating average:
    - Keeps only ratings in [lo, hi] (Airbnb rating scale is 0..5 in your DB)
    - Everything else (null, missing, strings, NaN) becomes null and is ignored by $avg
    """
    return {
        "$avg": {
            "$cond": [
                {
                    "$and": [
                        {"$gte": [f"${field_name}", lo]},
                        {"$lte": [f"${field_name}", hi]},
                    ]
                },
                f"${field_name}",
                None,
            ]
        }
    }


def aggregate_top_hosts():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]

    print("🔄 Aggregating top hosts...")
    db.top_hosts_agg.drop()

    cities = ["amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"]

    # speed
    db.listings_clean.create_index([("city", 1)])
    db.listings_clean.create_index([("host_id", 1)])
    db.top_hosts_agg.create_index([("city", 1), ("level", 1)])
    db.top_hosts_agg.create_index([("city", 1), ("neighborhood", 1)])

    rating_field = "review_scores_rating"

    for city in cities:
        print(f"\n📊 Processing {city}...")

        neigh_field = _detect_neighborhood_field(db, city)

        neighborhoods = db.listings_clean.distinct(
            neigh_field,
            {"city": city, neigh_field: {"$ne": None}}
        )

        # ---------- CITY LEVEL ----------
        city_pipeline = [
            {"$match": {"city": city, "host_id": {"$ne": None}, "host_name": {"$ne": None}}},
            {"$group": {
                "_id": {"host_id": "$host_id", "host_name": "$host_name"},
                "total_listings": {"$sum": 1},
                "avg_price": {"$avg": "$price"},
                "avg_rating": _safe_avg_rating_in_range(rating_field),
            }},
            {"$sort": {"total_listings": -1}},
            {"$limit": 10},
            {"$project": {
                "_id": 0,
                "host_id": "$_id.host_id",
                "host_name": "$_id.host_name",
                "total_listings": 1,
                "avg_price": {"$round": ["$avg_price", 2]},
                "avg_rating": {
                    "$cond": [
                        {"$ne": ["$avg_rating", None]},
                        {"$round": ["$avg_rating", 3]},
                        None,
                    ]
                },
            }},
        ]

        city_hosts = list(db.listings_clean.aggregate(city_pipeline, allowDiskUse=True))
        db.top_hosts_agg.insert_one({
            "city": city,
            "neighborhood": None,
            "level": "city",
            "top_hosts": city_hosts,
        })
        print(f"  ✅ City-level: {len(city_hosts)} hosts")

        # ---------- NEIGHBORHOOD LEVEL ----------
        inserted = 0
        for neigh in neighborhoods:
            match = {"city": city, "host_id": {"$ne": None}, "host_name": {"$ne": None}, neigh_field: neigh}

            neigh_pipeline = [
                {"$match": match},
                {"$group": {
                    "_id": {"host_id": "$host_id", "host_name": "$host_name"},
                    "total_listings": {"$sum": 1},
                    "avg_price": {"$avg": "$price"},
                    "avg_rating": _safe_avg_rating_in_range(rating_field),
                }},
                {"$sort": {"total_listings": -1}},
                {"$limit": 10},
                {"$project": {
                    "_id": 0,
                    "host_id": "$_id.host_id",
                    "host_name": "$_id.host_name",
                    "total_listings": 1,
                    "avg_price": {"$round": ["$avg_price", 2]},
                    "avg_rating": {
                        "$cond": [
                            {"$ne": ["$avg_rating", None]},
                            {"$round": ["$avg_rating", 3]},
                            None,
                        ]
                    },
                }},
            ]

            neigh_hosts = list(db.listings_clean.aggregate(neigh_pipeline, allowDiskUse=True))
            db.top_hosts_agg.insert_one({
                "city": city,
                "neighborhood": neigh,  # canonical output field
                "level": "neighborhood",
                "top_hosts": neigh_hosts,
            })
            inserted += 1

        print(f"  ✅ Neighborhoods: {inserted}")

    total = db.top_hosts_agg.count_documents({})
    print(f"\n✅ Top hosts aggregation complete: {total} documents")


def main():
    aggregate_top_hosts()
    return True


if __name__ == "__main__":
    main()
