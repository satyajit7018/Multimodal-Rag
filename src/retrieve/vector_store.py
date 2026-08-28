from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


class VectorStore:
    """Thin wrapper around a single Qdrant collection. Create one instance
    per content type (text / tables / images) for the multimodal pipeline,
    or a single instance for the Week 1 baseline.
    """

    def __init__(
        self,
        collection: str = "baseline_text",
        dim: int = 384,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection = collection
        if not self.client.collection_exists(collection):
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids: list[int], vectors: list[list[float]], payloads: list[dict]):
        points = [
            PointStruct(id=i, vector=v, payload=p)
            for i, v, p in zip(ids, vectors, payloads)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: list[float], top_k: int = 5):
        return self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
        )
