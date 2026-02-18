"""
Sentence-transformer embedding model wrapper.

Uses all-MiniLM-L6-v2 — a lightweight, fast model (~80 MB) that produces
384-dimensional embeddings well-suited for semantic search.
Runs entirely locally; no API key needed.
"""

import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

_model = None


def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (cached after first call)."""
    global _model
    if _model is None:
        print(f"📦 Loading embedding model '{MODEL_NAME}'...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str], batch_size: int = 64) -> np.ndarray:
    """Embed a list of text strings into normalized float32 vectors.

    Returns:
        np.ndarray of shape (len(texts), EMBEDDING_DIM)
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    return np.array(embeddings, dtype="float32")


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string.

    Returns:
        np.ndarray of shape (1, EMBEDDING_DIM)
    """
    model = get_model()
    embedding = model.encode([query], normalize_embeddings=True)
    return np.array(embedding, dtype="float32")
