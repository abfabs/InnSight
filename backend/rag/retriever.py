"""
High-level retriever for the InnSight chatbot.

Wraps the FAISS vector store and provides a simple API to:
  1. Retrieve relevant document chunks for a query
  2. Format them into a context string suitable for LLM prompts
"""

from rag.vector_store import FAISSStore


_store: FAISSStore | None = None
_available: bool | None = None  # None = not checked yet


def _get_store() -> FAISSStore | None:
    """Lazy-load the FAISS store.  Returns None if the index hasn't been
    built yet (so the chatbot still works without RAG)."""
    global _store, _available

    if _available is False:
        return None

    if _store is None:
        try:
            _store = FAISSStore()
            _store.load()
            _available = True
        except FileNotFoundError:
            print("⚠️  FAISS index not found — RAG disabled.  Run: python -m rag.ingest")
            _available = False
            return None

    return _store


def retrieve_context(
    query: str,
    city: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Search the vector store and return the top-k matching chunks.

    Returns an empty list if the FAISS index hasn't been built yet.
    """
    store = _get_store()
    if store is None:
        return []

    return store.search(query, top_k=top_k, filter_city=city)


def format_rag_context(results: list[dict]) -> str:
    """Turn retriever results into a readable context block for the LLM prompt.

    Example output::

        [1] Guest review (Amsterdam, Centrum):
        The apartment was super clean and the host was amazing …

        [2] Guide (amsterdam.md):
        Centrum is the historic heart of Amsterdam …
    """
    if not results:
        return ""

    lines: list[str] = []

    for i, r in enumerate(results, 1):
        meta = r.get("metadata", {})
        source = meta.get("source", "unknown")
        city = (meta.get("city") or "").title()

        if source == "review":
            neighborhood = meta.get("neighborhood", "Unknown")
            label = f"Guest review ({city}, {neighborhood})"
        elif source == "text_file":
            file_name = meta.get("file", "")
            label = f"Travel guide ({file_name})"
        else:
            label = f"Source: {source}"

        text = r["text"].strip()
        # Truncate very long chunks so the LLM prompt stays reasonable
        if len(text) > 600:
            text = text[:597] + "…"

        lines.append(f"[{i}] {label}:\n{text}")

    return "\n\n".join(lines)


def reload_store():
    """Force-reload the FAISS index (e.g. after re-running ingest)."""
    global _store, _available
    _store = None
    _available = None
