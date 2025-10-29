"""Qdrant connector for managing collections and points."""

import logging
from typing import List, Dict, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class QdrantConnector:
    """Manages Qdrant vector database operations."""

    def __init__(self, url: str = "http://localhost:6333", collection_name: str = "cost_data") -> None:
        try:
            self.client = QdrantClient(url=url)
            self.collection_name = collection_name
            logger.info("Connected to Qdrant at %s, collection: %s", url, collection_name)
        except Exception as e:
            logger.error("Failed to connect: %s", e)
            raise

    def recreate_collection(self, vector_size: int) -> None:
        """Recreate collection with specified vector size."""
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance="Cosine")
            )
            logger.info("Collection recreated with vector size %d", vector_size)
        except Exception as e:
            logger.error("Failed to recreate collection: %s", e)

    def upsert_points(self, embeddings: np.ndarray, payloads: List[Dict[str, Any]]) -> None:
        """Upsert embeddings and payloads into collection."""
        try:
            if len(embeddings) != len(payloads):
                raise ValueError("Embeddings and payloads must have same length")

            points = [
                PointStruct(id=i, vector=embeddings[i].tolist(), payload=payloads[i])
                for i in range(len(payloads))
            ]
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info("Upserted %d points", len(points))
        except Exception as e:
            logger.error("Failed to upsert points: %s", e)
