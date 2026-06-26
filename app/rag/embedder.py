"""Local text embedding via sentence-transformers."""

from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer

_MODEL_NAME = "all-MiniLM-L6-v2"
_MODEL: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(_MODEL_NAME)
    return _MODEL


def embed_text(text: str) -> List[float]:
    """Embed a single text string into a 384-dimension vector."""
    vector = _get_model().encode(text, normalize_embeddings=True)
    return vector.tolist()


def embed_documents(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add an embedding field to each document dict."""
    texts = [doc["content"] for doc in docs]
    vectors = _get_model().encode(texts, normalize_embeddings=True)
    enriched: List[Dict[str, Any]] = []
    for doc, vector in zip(docs, vectors):
        enriched.append({**doc, "embedding": vector.tolist()})
    return enriched
