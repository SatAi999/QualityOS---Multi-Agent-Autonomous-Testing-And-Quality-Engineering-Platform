import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.core.config import settings

logger = logging.getLogger(settings.APP_NAME)

class VectorDatabaseManager:
    """
    Qdrant client manager for semantic log querying, requirement similarity analysis,
    and historical bug retrieval.
    """
    def __init__(self):
        self.host = settings.QDRANT_HOST
        self.port = settings.QDRANT_PORT
        self.client: Optional[QdrantClient] = None

    def connect(self):
        if not self.client:
            self.client = QdrantClient(host=self.host, port=self.port)

    def init_collection(self, collection_name: str, vector_size: int = 1536):
        """Ensure collection exists in Qdrant database."""
        self.connect()
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            logger.info(f"Creating vector DB collection: {collection_name} (dimensions: {vector_size})")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE
                )
            )

    def upsert_vectors(self, collection_name: str, ids: List[Any], vectors: List[List[float]], payloads: List[Dict[str, Any]]):
        """Insert or update vectors into a collection."""
        self.connect()
        points = [
            qmodels.PointStruct(
                id=ids[i],
                vector=vectors[i],
                payload=payloads[i]
            ) for i in range(len(ids))
        ]
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    def search(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Perform cosine similarity search on the vector database."""
        self.connect()
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            } for hit in results
        ]

vector_db = VectorDatabaseManager()
