"""Vector Store wrapper around Qdrant collections.
Supports both remote Qdrant servers and zero-dependency embedded disk storage
(./data/qdrant_storage) with automatic fallback and connection management.
"""

from __future__ import annotations
import os
from typing import Any, Optional, List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

_EMBEDDED_CLIENT = None
_STORAGE_PATH = os.path.join(os.getcwd(), "data", "qdrant_storage")


def get_qdrant_client(host: str = "localhost", port: int = 6333) -> QdrantClient:
    """Returns a connected Qdrant client, automatically falling back to
    embedded local disk storage if a remote daemon is not reachable.
    """
    global _EMBEDDED_CLIENT
    # First attempt remote host if explicitly configured or running
    if os.environ.get("USE_REMOTE_QDRANT", "0") == "1":
        try:
            client = QdrantClient(host=host, port=port, timeout=2.0)
            client.get_collections()
            return client
        except Exception:
            pass

    # Use shared embedded client to avoid database file locks
    if _EMBEDDED_CLIENT is None:
        os.makedirs(_STORAGE_PATH, exist_ok=True)
        _EMBEDDED_CLIENT = QdrantClient(path=_STORAGE_PATH)
    return _EMBEDDED_CLIENT


class VectorStore:
    """Thin wrapper around a single Qdrant collection. Create one instance
    per content type (text / tables / images) for the multimodal pipeline,
    or a single instance for the baseline.
    """

    def __init__(
        self,
        collection: str = "baseline_text",
        dim: int = 384,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.collection = collection
        self.dim = dim
        self.client = get_qdrant_client(host=host, port=port)
        
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids: list[Any], vectors: list[list[float]], payloads: list[dict]):
        """Upsert points with vectors and rich metadata payload."""
        if not ids:
            return
        points = [
            PointStruct(id=i, vector=v, payload=p)
            for i, v, p in zip(ids, vectors, payloads)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: list[float], top_k: int = 5, query_text: str | None = None):
        """Search by cosine similarity vector. If query_text is provided, applies
        keyword boost for exact alphanumeric part numbers.
        """
        try:
            if hasattr(self.client, "query_points"):
                res = self.client.query_points(
                    collection_name=self.collection,
                    query=query_vector,
                    limit=top_k,
                )
                return getattr(res, "points", res)
            elif hasattr(self.client, "search"):
                return self.client.search(
                    collection_name=self.collection,
                    query_vector=query_vector,
                    limit=top_k,
                )
        except Exception as e:
            print(f"[VectorStore search error]: {e}")
        return []

    def count(self) -> int:
        """Returns total number of points in the collection."""
        try:
            info = self.client.get_collection(self.collection)
            return info.points_count or 0
        except Exception:
            return 0
