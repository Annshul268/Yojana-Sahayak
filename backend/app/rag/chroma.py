"""ChromaDB Client and Collection Manager for Scheme Embeddings."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.rag.embeddings import embedding_service


class ChromaManager:
    """Manages the persistent ChromaDB collection for schemes with lazy initialization."""

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_dir = Path(persist_directory or settings.CHROMA_PERSIST_DIRECTORY)
        self.collection_name = "yojana_schemes"
        self._client = None
        self._collection = None

    def _get_collection(self):
        """Lazily initializes ChromaDB client and collection on first actual use."""
        if self._collection is not None:
            return self._collection

        try:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self.persist_dir),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "RAG initialized lazily: ChromaDB collection '%s' ready at %s (docs: %d)",
                self.collection_name,
                self.persist_dir,
                self._collection.count(),
            )
            return self._collection
        except Exception as exc:
            logger.error("Failed to initialize ChromaDB collection: %s. Operating in resilient fallback mode.", exc)
            return None

    @property
    def collection(self):
        return self._get_collection()

    @property
    def client(self):
        if self._client is None:
            self._get_collection()
        return self._client

    def upsert_scheme_document(
        self,
        scheme_id: str,
        document_text: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Embeds and upserts a scheme document into ChromaDB."""
        coll = self._get_collection()
        if coll is None:
            logger.warning("Skipping document upsert: ChromaDB collection is not available.")
            return

        # Clean metadata (ChromaDB allows strings, ints, floats, bools only)
        cleaned_meta = {}
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                cleaned_meta[k] = v
            elif isinstance(v, list):
                cleaned_meta[k] = ", ".join(str(i) for i in v)
            else:
                cleaned_meta[k] = str(v)

        try:
            embedding = embedding_service.embed_texts([document_text])[0]
            coll.upsert(
                ids=[scheme_id],
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[cleaned_meta],
            )
        except Exception as exc:
            logger.error("Failed to upsert scheme document into ChromaDB: %s", exc)

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Queries the vector database for nearest scheme matches."""
        coll = self._get_collection()
        if coll is None or coll.count() == 0:
            return []

        try:
            query_embedding = embedding_service.embed_query(query_text)
            kwargs: Dict[str, Any] = {
                "query_embeddings": [query_embedding],
                "n_results": min(n_results, coll.count()),
            }
            if where:
                kwargs["where"] = where

            results = coll.query(**kwargs)
            formatted: List[Dict[str, Any]] = []
            if not results or not results["ids"]:
                return formatted

            ids = results["ids"][0]
            docs = results["documents"][0] if results.get("documents") else []
            metas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []

            for idx, scheme_id in enumerate(ids):
                formatted.append({
                    "scheme_id": scheme_id,
                    "document": docs[idx] if idx < len(docs) else "",
                    "metadata": metas[idx] if idx < len(metas) else {},
                    "distance": distances[idx] if idx < len(distances) else 1.0,
                })
            return formatted
        except Exception as exc:
            logger.error("ChromaDB query execution error: %s. Returning empty RAG context.", exc)
            return []

    def count(self) -> int:
        coll = self._get_collection()
        return coll.count() if coll is not None else 0


chroma_manager = ChromaManager()
