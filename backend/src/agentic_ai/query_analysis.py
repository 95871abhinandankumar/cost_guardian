"""Query intent detection and semantic search for agentic AI."""

from __future__ import annotations

import logging
import os
from typing import Dict, Any, List, Optional
from qdrant_client import QdrantClient
from vector_db.embedding_model import EmbeddingModel
from .utils import normalize_text

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "cost_data")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)


class QueryAnalyzer:
    """Detects query intent and retrieves relevant context."""

    def __init__(self, qdrant_url: str = QDRANT_URL, collection: str = QDRANT_COLLECTION):
        self.collection = collection

        try:
            self.qdrant = QdrantClient(url=qdrant_url, api_key=QDRANT_API_KEY)
            logger.info(f"Connected to Qdrant [{qdrant_url}]")
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant: {e}")
            self.qdrant = None

        try:
            self.embedder = EmbeddingModel()
            logger.info("Embedding model initialized")
        except Exception as e:
            logger.warning(f"Embedding model initialization failed: {e}")
            self.embedder = None

    def detect_intent(self, query: str) -> str:
        """Rule-based intent detection."""
        q = normalize_text(query).lower()
        if any(tok in q for tok in ("forecast", "predict", "trend", "estimate")):
            return "forecast"
        if any(tok in q for tok in ("anomaly", "spike", "unexpected", "outlier")):
            return "anomaly"
        if any(tok in q for tok in ("optimi", "save", "recommend", "right-size", "reduce")):
            return "optimization"
        return "insight"

    def embed_query(self, query: str) -> Optional[List[float]]:
        """Generate embedding vector."""
        if not self.embedder:
            return None

        try:
            import numpy as np
            embedding = self.embedder.encode([query])
            
            # Handle numpy array return
            if isinstance(embedding, np.ndarray):
                if len(embedding) > 0:
                    result = embedding[0].tolist() if hasattr(embedding[0], 'tolist') else embedding[0]
                    logger.info("Query embedding generated")
                    return result
            elif isinstance(embedding, list) and len(embedding):
                return embedding[0] if isinstance(embedding[0], list) else embedding
                
            return None
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return None

    def fetch_context(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top-k similar items from Qdrant."""
        if query_embedding is None or not self.qdrant:
            logger.debug("No Qdrant connection or embedding available — returning empty context.")
            return []

        try:
            results = self.qdrant.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
            )

            context = []
            for r in results:
                payload = r.payload or {}
                context.append({
                    "id": getattr(r, "id", None),
                    "score": getattr(r, "score", None),
                    **payload,
                })

            logger.info(f"Retrieved {len(context)} context items")
            return context
        except Exception as e:
            logger.error(f"Failed to fetch context: {e}")
            return []

    def analyze(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        """Analyze query and retrieve context."""
        intent = self.detect_intent(user_query)
        embedding = self.embed_query(user_query)
        context = self.fetch_context(embedding, top_k=top_k)
        
        logger.info(f"Analysis complete - intent: {intent}, context_items: {len(context)}")
        return {
            "intent": intent,
            "query_embedding": embedding,
            "context": context,
        }


if __name__ == "__main__":
    qa = QueryAnalyzer()
    result = qa.analyze("Predict next month's S3 cost trends.")
    print(result)
