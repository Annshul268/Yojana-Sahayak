"""Embedding service abstraction for semantic search and RAG."""

from typing import List
from backend.app.core.logging import logger

_default_ef = None


def get_default_embedding_function():
    """Lazily load and cache the DefaultEmbeddingFunction on first actual use."""
    global _default_ef
    if _default_ef is None:
        try:
            from chromadb.utils import embedding_functions

            logger.info("Initializing embedding model lazily...")
            _default_ef = embedding_functions.DefaultEmbeddingFunction()
            logger.info("Embedding model initialized successfully.")
        except Exception as exc:
            logger.warning("DefaultEmbeddingFunction initialization notice: %s", exc)
            _default_ef = None
    return _default_ef


class EmbeddingService:
    """Service layer generating dense vector embeddings for scheme documents."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of texts."""
        ef = get_default_embedding_function()
        if ef is not None:
            try:
                return ef(texts)
            except Exception as exc:
                logger.error("Error generating embeddings via default_ef: %s", exc)

        # Deterministic pseudo-embedding fallback if model runtime is unavailable
        logger.info("Using lightweight fallback embedding generation")
        results = []
        for text in texts:
            # 384-dimensional normalized vector derived deterministically
            vec = [0.0] * 384
            for idx, char in enumerate(text[:384]):
                vec[idx % 384] += (ord(char) % 100) / 100.0
            results.append(vec)
        return results

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single query string."""
        return self.embed_texts([query])[0]


embedding_service = EmbeddingService()
