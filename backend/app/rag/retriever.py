"""RAG Retriever module for finding grounded context from ChromaDB."""

from typing import Any, Dict, List, Optional
from backend.app.rag.chroma import chroma_manager


class SchemeRetriever:
    """Retrieves grounded scheme context for questions and recommendations."""

    def __init__(self):
        self.chroma = chroma_manager

    def retrieve_relevant_schemes(
        self,
        query: str,
        top_k: int = 4,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Finds top-K matching schemes using semantic vector distance."""
        where_filter = {"category": category} if category else None
        return self.chroma.query(query_text=query, n_results=top_k, where=where_filter)


scheme_retriever = SchemeRetriever()
