#!/usr/bin/env python3

import sys
from pathlib import Path
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BACKEND_DIR / "scripts"
sys.path.insert(0, str(BACKEND_DIR))

from pymongo import MongoClient
from config import Config


CHUNK_SIZE = 10000

# Columns we want to normalize across the whole project
RENAME_MAP = {
    "neighbourhood": "neighborhood",
    "review_score_rating": "review_scores_rating",
}


def get_db():
    client = MongoClient(Config.MONGO_URI)
    return client[Config.MONGO_DB]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c: RENAME_MAP[c] for c in df.columns if c in RENAME_MAP}
    if cols:
        df = df.rename(columns=cols)
    return df


def upload_file(db, city_name: str, csv_path: Path) -> int:
    collection_name = csv_path.stem
    coll = db[collection_name]

    print(f"  📄 {csv_path.name}")

    # Overwrite city slice for clean re-runs
    coll.delete_many({"city": city_name})

    total = 0

    for chunk_num, df_chunk in enumerate(pd.read_csv(csv_path, chunksize=CHUNK_SIZE), 1):
        df_chunk = normalize_columns(df_chunk)
        df_chunk = df_chunk.where(pd.notnull(df_chunk), None)
        df_chunk["city"] = city_name

        docs = df_chunk.to_dict("records")
        if docs:
            result = coll.insert_many(docs, ordered=False)
            total += len(result.inserted_ids)

        print(f"     Chunk {chunk_num}: {len(docs):,} rows")

    return total


def process_city(db, city_dir: Path, expected_files: list[str]) -> int:
    city_name = city_dir.name
    print(f"\n🏙️  {city_name.upper()}")

    total = 0
    for f in expected_files:
        csv_path = city_dir / f
        if csv_path.exists():
            total += upload_file(db, city_name, csv_path)
        else:
            print(f"  ⚠️  Missing: {f}")

    print(f"  ✅ Total: {total:,} rows")
    return total


def run_aggregations():
    print("\n" + "=" * 70)
    print("🔄 RUNNING AGGREGATIONS FOR DASHBOARD")
    print("=" * 70)

    aggregation_scripts = [
        ("aggregate_sentiment_summary.py", "Sentiment Summary", "aggregate_sentiment"),
        ("aggregate_room_types.py", "Room Type Distribution", "aggregate_room_types"),
        ("aggregate_occupancy.py", "Occupancy by Month", "aggregate_occupancy"),
        ("aggregate_top_hosts.py", "Top Hosts", "aggregate_top_hosts"),
    ]

    import importlib.util

    for script_name, description, fn in aggregation_scripts:
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            print(f"⚠️  {script_name} not found at {script_path}")
            continue

        print(f"\n▶️  Running: {description} ({script_name})")
        print("-" * 70)

        spec = importlib.util.spec_from_file_location(script_name.replace(".py", ""), script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, fn):
            getattr(module, fn)()
            print(f"✅ {description} complete")
        else:
            print(f"❌ {script_name} has no function {fn}()")


def print_database_summary(db):
    print("\n" + "=" * 70)
    print("📊 DATABASE SUMMARY")
    print("=" * 70)

    collections = {
        "Raw Data Collections": [
            "listings_clean",
            "reviews_sentiment",
            "listing_sentiment",
            "neighborhood_sentiment",
            "listings_map",
            "neighborhood_stats",
            "occupancy_monthly",
            "top_hosts",
            "review_words",
        ],
        "Dashboard Collections (Aggregated)": [
            "sentiment_summary",
            "room_type_distribution",
            "occupancy_by_month",
            "top_hosts_agg",
        ],
    }

    for category, coll_names in collections.items():
        print(f"\n{category}:")
        for coll_name in coll_names:
            try:
                count = db[coll_name].count_documents({})
                print(f"  ✓ {coll_name}: {count:,} documents")
            except Exception:
                print(f"  ✗ {coll_name}: Not found")


def main(
    upload_raw: bool = True,
    run_aggs: bool = True,
    show_summary: bool = True,
):
    """
    Upload processed CSVs to MongoDB + (optionally) run aggregations.

    Parameters:
      upload_raw: upload all processed CSV collections (listings_clean, listing_sentiment, etc.)
      run_aggs: run aggregation scripts to build dashboard collections
      show_summary: print DB doc counts at end
    """
    db = get_db()

    print("=" * 70)
    print("🚀 INNSIGHT DATABASE UPLOAD")
    print("=" * 70)

    base_path = BACKEND_DIR / "data" / "processed"
    if not base_path.exists():
        print(f"❌ Processed data directory not found: {base_path}")
        return False

    city_folders = [p for p in base_path.iterdir() if p.is_dir()]
    print(f"\n📍 Found cities: {[p.name for p in city_folders]}")

    expected_files = [
        "listings_clean.csv",
        "neighborhood_stats.csv",
        "occupancy_monthly.csv",
        "top_hosts.csv",
        "review_words.csv",
        "reviews_sentiment.csv",
        "listing_sentiment.csv",
        "neighborhood_sentiment.csv",
        "listings_map.csv",
    ]

    if upload_raw:
        print("\n" + "=" * 70)
        print("📤 STEP 1: UPLOADING CSV FILES")
        print("=" * 70)

        grand_total = 0
        for city_dir in sorted(city_folders):
            grand_total += process_city(db, city_dir, expected_files)

        print(f"\n✅ CSV UPLOAD COMPLETE: {grand_total:,} TOTAL ROWS")
    else:
        print("\nℹ️ upload_raw=False → skipping CSV upload")

    if run_aggs:
        run_aggregations()
    else:
        print("\nℹ️ run_aggs=False → skipping aggregations")

    if show_summary:
        print_database_summary(db)

    print("\n" + "=" * 70)
    print("✅ FULL DATABASE READY!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    main()
