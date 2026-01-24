#!/usr/bin/env python3
"""
Aggregate monthly occupancy from calendar CSV by neighborhood and city.

Outputs to Mongo: occupancy_by_month
Schema:
  { city, neighborhood, level: 'city'|'neighborhood', monthly_occupancy: [...] }
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from pymongo import MongoClient
from config import Config


def _pick_neighborhood_field(sample_doc: dict) -> str:
    # prefer canonical
    if "neighborhood" in sample_doc:
        return "neighborhood"
    if "neighbourhood" in sample_doc:
        return "neighbourhood"
    return "neighborhood"


def aggregate_occupancy():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]

    print("🔄 Aggregating occupancy by month...")
    db.occupancy_by_month.drop()

    cities = ["amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"]
    base_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

    # indexes that make API queries fast
    db.occupancy_by_month.create_index([("city", 1), ("level", 1)])
    db.occupancy_by_month.create_index([("city", 1), ("neighborhood", 1)])

    for city in cities:
        print(f"\n📊 Processing {city}...")

        calendar_path = os.path.join(base_path, city, "calendar.csv")
        if not os.path.exists(calendar_path):
            print(f"  ⚠️  Calendar file not found: {calendar_path}")
            continue

        calendar_df = pd.read_csv(calendar_path)

        if calendar_df.empty:
            print("  ⚠️  calendar.csv is empty")
            continue

        calendar_df["date"] = pd.to_datetime(calendar_df["date"], errors="coerce")
        calendar_df = calendar_df.dropna(subset=["date"])
        calendar_df["month"] = calendar_df["date"].dt.to_period("M").astype(str)

        # Airbnb calendar: available == 't' means NOT occupied
        calendar_df["occupied"] = calendar_df["available"].apply(lambda x: 0 if x == "t" else 1)

        # Pull one doc to detect the correct field name
        sample = db.listings_clean.find_one({"city": city})
        if not sample:
            print("  ⚠️  No listings_clean docs found for this city")
            continue

        neigh_field = _pick_neighborhood_field(sample)

        # Build listing_id -> neighborhood map from Mongo
        listings = db.listings_clean.find(
            {"city": city},
            {"listing_id": 1, neigh_field: 1}
        )

        listing_to_neigh = {}
        for l in listings:
            lid = l.get("listing_id")
            neigh = l.get(neigh_field)
            if lid is None or neigh is None:
                continue
            listing_to_neigh[str(lid)] = neigh

        # Map neighborhoods into calendar
        calendar_df["neighborhood"] = calendar_df["listing_id"].astype(str).map(listing_to_neigh)
        before = len(calendar_df)
        calendar_df = calendar_df.dropna(subset=["neighborhood"])
        after = len(calendar_df)

        print(f"  🔎 Calendar rows: {before:,} → {after:,} after neighborhood mapping")

        if calendar_df.empty:
            db.occupancy_by_month.insert_one({
                "city": city,
                "neighborhood": None,
                "level": "city",
                "monthly_occupancy": []
            })
            print("  ⚠️  No mapped calendar rows; inserted empty city doc")
            continue

        # ---------------- CITY LEVEL ----------------
        city_monthly = (
            calendar_df.groupby("month", as_index=False)
            .agg(occupied=("occupied", "sum"), total_nights=("listing_id", "count"))
        )
        city_monthly["occupancy_rate"] = (city_monthly["occupied"] / city_monthly["total_nights"] * 100).round(2)

        monthly_data = [
            {
                "month": row["month"],
                "occupied_nights": int(row["occupied"]),
                "total_nights": int(row["total_nights"]),
                "occupancy_rate": float(row["occupancy_rate"]),
            }
            for _, row in city_monthly.iterrows()
        ]

        db.occupancy_by_month.insert_one({
            "city": city,
            "neighborhood": None,
            "level": "city",
            "monthly_occupancy": monthly_data,
        })
        print(f"  ✅ City-level: {len(monthly_data)} months")

        # ---------------- NEIGHBORHOOD LEVEL ----------------
        inserted = 0
        for neigh, neigh_df in calendar_df.groupby("neighborhood"):
            neigh_monthly = (
                neigh_df.groupby("month", as_index=False)
                .agg(occupied=("occupied", "sum"), total_nights=("listing_id", "count"))
            )
            neigh_monthly["occupancy_rate"] = (neigh_monthly["occupied"] / neigh_monthly["total_nights"] * 100).round(2)

            monthly_data = [
                {
                    "month": row["month"],
                    "occupied_nights": int(row["occupied"]),
                    "total_nights": int(row["total_nights"]),
                    "occupancy_rate": float(row["occupancy_rate"]),
                }
                for _, row in neigh_monthly.iterrows()
            ]

            db.occupancy_by_month.insert_one({
                "city": city,
                "neighborhood": neigh,
                "level": "neighborhood",
                "monthly_occupancy": monthly_data,
            })
            inserted += 1

        print(f"  ✅ Neighborhoods inserted: {inserted}")

    total = db.occupancy_by_month.count_documents({})
    print(f"\n✅ Occupancy aggregation complete: {total} documents")


def main():
    """Callable entrypoint for pipeline imports."""
    aggregate_occupancy()
    return True


if __name__ == "__main__":
    main()
