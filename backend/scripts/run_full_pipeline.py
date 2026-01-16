#!/usr/bin/env python3
"""
RUN FULL PIPELINE (import-call style)

Order:
1) Drop DB
2) data_etl -> creates processed CSVs
3) sentiment_etl -> english-filtered sentiment + listing_sentiment + listings_map
4) wordcloud_etl -> review_words + images (optional)
5) upload_all_data -> uploads processed CSVs to Mongo (NO aggregations here)
6) aggregation scripts -> build dashboard collections
"""

import sys
from pathlib import Path
from datetime import datetime

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def must(ok: bool, step: str):
    """Stop pipeline immediately if a required step fails."""
    if not ok:
        raise RuntimeError(f"CRITICAL: {step} failed. Pipeline stopped.")


def main():
    start = datetime.now()

    print("=" * 80)
    print("  🚀 INNSIGHT FULL PIPELINE")
    print("  Drop DB → ETL → Upload → Aggregations")
    print("=" * 80)
    print(f"\n⏰ Started at: {start.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Import after sys.path is set
    from scripts import drop_innsight_db
    from scripts import data_etl
    from scripts import sentiment_etl
    from scripts import wordcloud_etl
    from scripts import upload_all_data

    from scripts import aggregate_sentiment_summary
    from scripts import aggregate_room_types
    from scripts import aggregate_occupancy
    from scripts import aggregate_top_hosts

    cities = ["amsterdam", "rome", "prague"]

    # 0) Drop DB
    print_header("STEP 0: DROP DATABASE")
    must(drop_innsight_db.main() is not False, "Drop database")

    # 1) Data ETL
    print_header("STEP 1: DATA ETL")
    must(data_etl.main(cities=cities) is not False, "Data ETL")

    # 2) Sentiment ETL
    print_header("STEP 2: SENTIMENT ETL")
    must(sentiment_etl.main(cities=cities) is not False, "Sentiment ETL")

    # 3) Wordcloud ETL (optional)
    print_header("STEP 3: WORDCLOUD ETL (OPTIONAL)")
    try:
        wordcloud_etl.main(cities=cities)
    except Exception as e:
        print(f"⚠️ Wordcloud ETL failed, continuing... ({e})")

    # 4) Upload ONLY
    print_header("STEP 4: UPLOAD PROCESSED CSVs (NO AGGREGATIONS)")
    must(upload_all_data.main(upload_raw=True, run_aggs=False, show_summary=True) is not False, "Upload processed CSVs")

    # 5) Run aggregations explicitly
    print_header("STEP 5: AGGREGATIONS (DASHBOARD COLLECTIONS)")
    must(aggregate_sentiment_summary.main() is not False, "Aggregate sentiment summary")
    must(aggregate_room_types.main() is not False, "Aggregate room types")
    must(aggregate_occupancy.main() is not False, "Aggregate occupancy")
    must(aggregate_top_hosts.main() is not False, "Aggregate top hosts")

    end = datetime.now()
    print_header("DONE")
    print(f"⏱️ Duration: {end - start}")
    print("✅ Pipeline finished successfully.")


if __name__ == "__main__":
    main()
