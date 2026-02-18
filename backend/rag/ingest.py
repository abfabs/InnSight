#!/usr/bin/env python3
"""
Ingest reviews + text files into the FAISS vector store.

Usage (from the backend/ directory):
    python -m rag.ingest               # ingest everything
    python -m rag.ingest --reviews-only # skip text files
    python -m rag.ingest --text-only    # skip reviews
    python -m rag.ingest --max-reviews 500  # limit per city
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from rag.vector_store import FAISSStore  # noqa: E402

RAW_DATA_DIR = BACKEND_DIR / "data" / "raw"
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
RAG_DATA_DIR = BACKEND_DIR / "rag_data"

CITIES = ["amsterdam", "rome", "lisbon", "sicily", "bordeaux", "crete"]

# Defaults
DEFAULT_MAX_REVIEWS = 2000
MIN_REVIEW_LENGTH = 30


# ===================================================================
# Helpers
# ===================================================================

def is_likely_english(text) -> bool:
    """Quick heuristic English detection (matches sentiment_etl logic)."""
    if pd.isna(text) or len(str(text)) < 10:
        return False

    text_lower = str(text).lower()

    non_english_markers = [
        "het", "een", "van", "voor", "zeer", "erg", "mooie", "zijn",
        "sehr", "gut", "und", "ist", "wir", "schön",
        "molto", "bella", "ottimo", "bellissimo", "siamo", "della",
        "très", "bien", "nous", "était", "avec", "merci",
        "muy", "estaba", "todo", "excelente",
    ]
    first_words = text_lower.split()[:5]
    for word in first_words:
        if word in non_english_markers:
            return False

    english_markers = [
        "the", "was", "very", "great", "nice", "good", "we", "our",
        "had", "place", "location", "stay", "apartment", "host",
        "clean", "would", "recommend", "is", "it", "and", "but",
    ]
    english_count = sum(1 for w in text_lower.split() if w in english_markers)
    return english_count >= 2


# ===================================================================
# Review loading
# ===================================================================

def load_reviews(city: str, max_reviews: int) -> list[dict]:
    """Read raw reviews CSV, filter English, map to neighborhoods."""
    reviews_path = RAW_DATA_DIR / city / "reviews.csv"
    listings_path = PROCESSED_DIR / city / "listings_clean.csv"

    if not reviews_path.exists():
        print(f"  ⚠️  No reviews.csv for {city}")
        return []

    reviews = pd.read_csv(reviews_path, usecols=["listing_id", "comments"])

    # Neighbourhood lookup from cleaned listings
    neighborhood_map: dict = {}
    if listings_path.exists():
        listings = pd.read_csv(listings_path, usecols=["listing_id", "neighborhood"])
        neighborhood_map = dict(zip(listings["listing_id"], listings["neighborhood"]))

    # Filter: English + minimum length
    mask = reviews["comments"].apply(
        lambda x: isinstance(x, str) and len(x) >= MIN_REVIEW_LENGTH and is_likely_english(x)
    )
    reviews = reviews[mask]

    # Sample down if needed
    if len(reviews) > max_reviews:
        reviews = reviews.sample(n=max_reviews, random_state=42)

    documents: list[dict] = []
    for _, row in reviews.iterrows():
        text = str(row["comments"]).strip()
        listing_id = row.get("listing_id")
        neighborhood = neighborhood_map.get(listing_id, "Unknown")

        documents.append(
            {
                "text": text,
                "metadata": {
                    "source": "review",
                    "city": city,
                    "neighborhood": str(neighborhood),
                    "listing_id": int(listing_id) if pd.notna(listing_id) else None,
                },
            }
        )

    print(f"  ✅ {city}: {len(documents):,} reviews")
    return documents


# ===================================================================
# Text-file loading
# ===================================================================

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks at paragraph boundaries."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > chunk_size and current:
            chunks.append(current.strip())
            # overlap: keep the tail of the previous chunk
            words = current.split()
            tail = " ".join(words[-(overlap // 5) :]) if len(words) > overlap // 5 else ""
            current = (tail + "\n\n" + para) if tail else para
        else:
            current = (current + "\n\n" + para) if current else para

    if current.strip():
        chunks.append(current.strip())

    return chunks


def load_text_files() -> list[dict]:
    """Load and chunk all .md / .txt files in rag_data/."""
    if not RAG_DATA_DIR.exists():
        print(f"  ⚠️  No {RAG_DATA_DIR} directory")
        return []

    documents: list[dict] = []
    patterns = list(RAG_DATA_DIR.glob("*.md")) + list(RAG_DATA_DIR.glob("*.txt"))

    for filepath in sorted(patterns):
        text = filepath.read_text(encoding="utf-8")
        if not text.strip():
            continue

        # Detect city from filename
        stem = filepath.stem.lower()
        city = stem if stem in CITIES else None

        chunks = chunk_text(text)
        for chunk in chunks:
            documents.append(
                {
                    "text": chunk,
                    "metadata": {
                        "source": "text_file",
                        "file": filepath.name,
                        "city": city,
                    },
                }
            )

        print(f"  ✅ {filepath.name}: {len(chunks)} chunks")

    return documents


# ===================================================================
# Main
# ===================================================================

def main():
    parser = argparse.ArgumentParser(description="Ingest data into FAISS vector store")
    parser.add_argument("--reviews-only", action="store_true", help="Skip text files")
    parser.add_argument("--text-only", action="store_true", help="Skip reviews")
    parser.add_argument(
        "--max-reviews",
        type=int,
        default=DEFAULT_MAX_REVIEWS,
        help=f"Max reviews per city (default {DEFAULT_MAX_REVIEWS})",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🔄 INNSIGHT RAG INGESTION")
    print("=" * 60)

    all_documents: list[dict] = []

    # 1 — Reviews
    if not args.text_only:
        print("\n📝 Loading reviews from raw CSV files …")
        for city in CITIES:
            all_documents.extend(load_reviews(city, args.max_reviews))

    # 2 — Text files
    if not args.reviews_only:
        print(f"\n📄 Loading text files from {RAG_DATA_DIR} …")
        all_documents.extend(load_text_files())

    if not all_documents:
        print("\n❌ No documents to ingest!")
        sys.exit(1)

    print(f"\n📊 Total documents: {len(all_documents):,}")

    # 3 — Build FAISS index
    print("\n🔨 Building FAISS index …")
    store = FAISSStore()
    store.build(all_documents)
    store.save()

    print("\n" + "=" * 60)
    print("✅ RAG INGESTION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
