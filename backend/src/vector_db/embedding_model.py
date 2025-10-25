"""
embedding_model.py
-----------------
Wrapper for SentenceTransformer embeddings.
"""

from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# --------------------------- Logging Configuration --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper class for SentenceTransformer embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedding model.

        Args:
            model_name (str): Pretrained SentenceTransformer model name.
        """
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Initialized SentenceTransformer model: %s", model_name)
        except SentenceTransformerException as e:
            logger.error("Failed to load SentenceTransformer model '%s': %s", model_name, e, exc_info=True)
            raise

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Convert a list of texts into embeddings.

        Args:
            texts (List[str]): List of input sentences.

        Returns:
            np.ndarray: Embeddings array.
        """
        try:
            embeddings = self.model.encode(texts)
            logger.info("Encoded %d texts into embeddings.", len(texts))
            return embeddings
        except Exception as e:
            logger.error("Error encoding texts: %s", e, exc_info=True)
            raise
