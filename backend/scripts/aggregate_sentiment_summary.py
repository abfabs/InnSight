#!/usr/bin/env python3
"""
Aggregate sentiment summary from MongoDB using REVIEW-LEVEL truth.

Source:
  reviews_sentiment: {city, listing_id, sentiment_category, ...}  (English-filtered in ETL)
  listings_clean: {listing_id, neighborhood (or neighbourhood), city, ...}

Output:
  sentiment_summary:
    {
      city,
      neighborhood: null | "<name>",
      level: "city" | "neighborhood",
      total_reviews,
      positive_count, neutral_count, negative_count,
      positive, neutral, negative   # percentages (0-100)
    }
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymongo import MongoClient
from config import Config


def aggregate_sentiment():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]

    print("🔄 Aggregating sentiment summary (from reviews_sentiment)...")
    db.sentiment_summary.drop()

    cities = ["amsterdam", "rome", "lisbon", "sicily", "bordeaux", "crete"]

    # Speed indexes
    db.reviews_sentiment.create_index([("city", 1)])
    db.reviews_sentiment.create_index([("listing_id", 1)])
    db.listings_clean.create_index([("city", 1)])
    db.listings_clean.create_index([("listing_id", 1)])

    # Helpful for API
    db.sentiment_summary.create_index([("city", 1), ("level", 1)])
    db.sentiment_summary.create_index([("city", 1), ("neighborhood", 1)])

    for city in cities:
        print(f"\n📊 {city}")

        # ----------------------------
        # CITY LEVEL (direct from reviews_sentiment)
        # ----------------------------
        city_pipeline = [
            {"$match": {"city": city, "sentiment_category": {"$in": ["positive", "neutral", "negative"]}}},
            {"$group": {"_id": "$sentiment_category", "count": {"$sum": 1}}},
        ]

        city_counts = {r["_id"]: r["count"] for r in db.reviews_sentiment.aggregate(city_pipeline)}
        pos = int(city_counts.get("positive", 0))
        neu = int(city_counts.get("neutral", 0))
        neg = int(city_counts.get("negative", 0))
        total = pos + neu + neg

        if total > 0:
            db.sentiment_summary.insert_one({
                "city": city,
                "neighborhood": None,
                "level": "city",
                "total_reviews": total,
                "positive_count": pos,
                "neutral_count": neu,
                "negative_count": neg,
                "positive": round(pos / total * 100, 1),
                "neutral": round(neu / total * 100, 1),
                "negative": round(neg / total * 100, 1),
            })
            print(f"  ✅ City reviews: {total:,}")
        else:
            print("  ⚠️ No reviews found for city (reviews_sentiment empty?)")

        # ----------------------------
        # NEIGHBORHOOD LEVEL
        # Join reviews_sentiment -> listings_clean to get neighborhood
        # ----------------------------
        neigh_pipeline = [
            {"$match": {"city": city, "sentiment_category": {"$in": ["positive", "neutral", "negative"]}}},
            {"$lookup": {
                "from": "listings_clean",
                "localField": "listing_id",
                "foreignField": "listing_id",
                "as": "listing"
            }},
            {"$unwind": "$listing"},
            {"$addFields": {
                "neighborhood_norm": {"$ifNull": ["$listing.neighborhood", "$listing.neighbourhood"]}
            }},
            {"$match": {"neighborhood_norm": {"$ne": None}}},
            {"$group": {
                "_id": {"neighborhood": "$neighborhood_norm", "category": "$sentiment_category"},
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.neighborhood",
                "counts": {"$push": {"k": "$_id.category", "v": "$count"}},
                "total_reviews": {"$sum": "$count"}
            }},
            {"$addFields": {"countsObj": {"$arrayToObject": "$counts"}}},
            {"$project": {
                "_id": 0,
                "neighborhood": "$_id",
                "total_reviews": 1,
                "positive_count": {"$ifNull": ["$countsObj.positive", 0]},
                "neutral_count": {"$ifNull": ["$countsObj.neutral", 0]},
                "negative_count": {"$ifNull": ["$countsObj.negative", 0]},
            }},
        ]

        neigh_docs = list(db.reviews_sentiment.aggregate(neigh_pipeline))

        inserted = 0
        for n in neigh_docs:
            total_n = int(n.get("total_reviews", 0) or 0)
            if total_n <= 0:
                continue

            pos_n = int(n.get("positive_count", 0) or 0)
            neu_n = int(n.get("neutral_count", 0) or 0)
            neg_n = int(n.get("negative_count", 0) or 0)

            db.sentiment_summary.insert_one({
                "city": city,
                "neighborhood": n["neighborhood"],
                "level": "neighborhood",
                "total_reviews": total_n,
                "positive_count": pos_n,
                "neutral_count": neu_n,
                "negative_count": neg_n,
                "positive": round(pos_n / total_n * 100, 1),
                "neutral": round(neu_n / total_n * 100, 1),
                "negative": round(neg_n / total_n * 100, 1),
            })
            inserted += 1

        print(f"  ✅ Neighborhoods: {inserted}")

    total_docs = db.sentiment_summary.count_documents({})
    print(f"\n✅ DONE: {total_docs} sentiment summary docs")


def main():
    aggregate_sentiment()
    return True


if __name__ == "__main__":
    main()
