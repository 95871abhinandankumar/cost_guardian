"""
qdrant_client_connector.py
--------------------------
Connector class for managing Qdrant collections and points.
"""

import logging
from typing import List, Dict, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse

# --------------------------- Logging Configuration --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class QdrantConnector:
    """
    Connector for Qdrant vector database.

    Provides functionality to create/recreate collections and upsert points.
    """

    def __init__(self, url: str = "http://localhost:6333", collection_name: str = "cost_data") -> None:
        """
        Initialize Qdrant client.

        Args:
            url (str): URL to the Qdrant instance.
            collection_name (str): Default collection name.
        """
        try:
            self.client = QdrantClient(url=url)
            self.collection_name = collection_name
            logger.info("Connected to Qdrant at %s, collection: %s", url, collection_name)
        except Exception as e:
            logger.error("Failed to connect to Qdrant: %s", e, exc_info=True)
            raise

    def recreate_collection(self, vector_size: int) -> None:
        """
        Recreate the collection with specified vector size.

        Args:
            vector_size (int): Dimensionality of vectors.
        """
        try:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance="Cosine")
            )
            logger.info("Collection '%s' recreated with vector size %d.", self.collection_name, vector_size)
        except UnexpectedResponse as e:
            logger.error("Error recreating collection '%s': %s", self.collection_name, e, exc_info=True)
        except Exception as e:
            logger.error("Unexpected error recreating collection '%s': %s", self.collection_name, e, exc_info=True)

    def upsert_points(self, embeddings: np.ndarray, payloads: List[Dict[str, Any]]) -> None:
        """
        Upsert embeddings and their payloads into the collection.

        Args:
            embeddings (np.ndarray): 2D array of embeddings.
            payloads (List[Dict[str, Any]]): List of payload dictionaries.
        """
        try:
            if len(embeddings) != len(payloads):
                raise ValueError("Embeddings and payloads must have the same length.")

            points = [
                PointStruct(id=i, vector=embeddings[i].tolist(), payload=payloads[i])
                for i in range(len(payloads))
            ]
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info("Upserted %d points into collection '%s'.", len(points), self.collection_name)
        except Exception as e:
            logger.error("Failed to upsert points into '%s': %s", self.collection_name, e, exc_info=True)
