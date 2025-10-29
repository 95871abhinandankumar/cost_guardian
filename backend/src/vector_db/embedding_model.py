"""SentenceTransformer embeddings for semantic search."""

import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Generates embeddings using SentenceTransformer."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Initialized model: %s", model_name)
        except Exception as e:
            logger.error("Failed to load model: %s", e)
            raise

    def encode(self, texts: List[str]) -> np.ndarray:
        """Convert texts to embeddings."""
        try:
            embeddings = self.model.encode(texts)
            logger.info("Encoded %d texts", len(texts))
            return embeddings
        except Exception as e:
            logger.error("Encoding failed: %s", e)
            raise
