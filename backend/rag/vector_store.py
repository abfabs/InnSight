"""
FAISS vector store for InnSight RAG.

Stores a flat inner-product index (cosine similarity on normalized vectors)
alongside a JSON metadata file that maps each vector position to its
original text and metadata (city, source type, neighborhood, etc.).
"""

import json
from pathlib import Path

import faiss
import numpy as np

from rag.embeddings import embed_texts, embed_query, EMBEDDING_DIM


DEFAULT_INDEX_DIR = Path(__file__).resolve().parent.parent / "faiss_index"


class FAISSStore:
    """Manages a FAISS index with parallel document metadata."""

    def __init__(self, index_dir: str | Path | None = None):
        self.index_dir = Path(index_dir or DEFAULT_INDEX_DIR)
        self.index: faiss.IndexFlatIP | None = None
        self.documents: list[dict] = []  # [{text, metadata}, ...]

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, documents: list[dict], batch_size: int = 256):
        """Build the FAISS index from a list of documents.

        Args:
            documents: list of ``{"text": str, "metadata": dict}``
            batch_size: encoding batch size passed to the embedding model
        """
        self.documents = documents
        texts = [d["text"] for d in documents]

        print(f"🔢 Embedding {len(texts):,} documents …")
        embeddings = embed_texts(texts, batch_size=batch_size)

        # Inner-product on L2-normalized vectors == cosine similarity
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self.index.add(embeddings)

        print(f"✅ FAISS index built — {self.index.ntotal:,} vectors")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self):
        """Write index + metadata to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(self.index_dir / "index.faiss"))

        with open(self.index_dir / "documents.json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False)

        print(f"💾 Index saved to {self.index_dir}")

    def load(self):
        """Load a previously saved index from disk."""
        index_path = self.index_dir / "index.faiss"
        docs_path = self.index_dir / "documents.json"

        if not index_path.exists() or not docs_path.exists():
            raise FileNotFoundError(
                f"No FAISS index at {self.index_dir}. Run  python -m rag.ingest  first."
            )

        self.index = faiss.read_index(str(index_path))

        with open(docs_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        print(f"📂 Loaded FAISS index — {self.index.ntotal:,} vectors")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_city: str | None = None,
        min_score: float = 0.25,
    ) -> list[dict]:
        """Semantic search with optional city filtering.

        Args:
            query:       natural-language query
            top_k:       maximum results to return
            filter_city: if set, only return docs whose metadata ``city`` matches
            min_score:   discard results below this cosine-similarity threshold

        Returns:
            List of ``{"text": str, "metadata": dict, "score": float}``
        """
        if self.index is None:
            self.load()

        q_vec = embed_query(query)

        # Over-fetch when filtering so we still get enough after pruning
        fetch_k = top_k * 6 if filter_city else top_k
        fetch_k = min(fetch_k, self.index.ntotal)

        scores, indices = self.index.search(q_vec, fetch_k)

        results: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            if score < min_score:
                continue

            doc = self.documents[idx]
            doc_city = doc.get("metadata", {}).get("city") or ""

            if filter_city and doc_city.lower() != filter_city.lower():
                continue

            results.append(
                {
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": float(score),
                }
            )

            if len(results) >= top_k:
                break

        return results
