"""
Query Analysis Module

Responsibilities:
- Detect query intent (forecast, anomaly, optimization, insight)
- Generate embeddings using local or remote model
- Retrieve contextual data from Qdrant for grounding
- Act as the first stage of the Agentic AI pipeline before LLM/SageMaker
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Any, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter
from src.vector_db.embedding_model import EmbeddingModel
from src.vector_db.qdrant_client_connector import QdrantConnector

from .utils import normalize_text

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# -----------------------------------------------------------------------------
# Environment Configs
# -----------------------------------------------------------------------------
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "cost_data")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)  # Optional if using cloud Qdrant

# -----------------------------------------------------------------------------
# Query Analyzer
# -----------------------------------------------------------------------------
class QueryAnalyzer:
    """
    Core analysis engine to extract intent, embeddings, and relevant context.
    """

    def __init__(self, qdrant_url: str = QDRANT_URL, collection: str = QDRANT_COLLECTION):
        self.collection = collection

        # Initialize Qdrant connection
        try:
            self.qdrant = QdrantClient(
                url=qdrant_url,
                api_key=QDRANT_API_KEY
            )
            logger.info(f"✅ Connected to Qdrant [{qdrant_url}] (collection={collection})")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Qdrant: {e}")
            self.qdrant = None

        # Initialize embedding model (SageMaker or local)
        try:
            self.embedder = EmbeddingModel()
            logger.info("✅ Embedding model initialized.")
        except Exception as e:
            logger.warning(f"⚠️ Embedding model initialization failed: {e}")
            self.embedder = None

    # -------------------------------------------------------------------------
    # Intent Detection
    # -------------------------------------------------------------------------
    def detect_intent(self, query: str) -> str:
        """Basic rule-based intent detection (extendable with Bedrock in future)."""
        q = normalize_text(query).lower()

        if any(tok in q for tok in ("forecast", "predict", "trend", "estimate")):
            return "forecast"
        if any(tok in q for tok in ("anomaly", "spike", "unexpected", "outlier")):
            return "anomaly"
        if any(tok in q for tok in ("optimi", "save", "recommend", "right-size", "reduce")):
            return "optimization"
        return "insight"

    # -------------------------------------------------------------------------
    # Embedding Generation
    # -------------------------------------------------------------------------
    def embed_query(self, query: str) -> Optional[List[float]]:
        """Return embedding vector using embedding model."""
        if not self.embedder:
            logger.debug("Embedding model unavailable — skipping vectorization.")
            return None

        try:
            embedding = self.embedder.encode([query])
            if isinstance(embedding, list) and len(embedding):
                logger.info("🔢 Query embedding generated successfully.")
                return embedding[0]
            logger.warning("⚠️ Empty embedding returned.")
            return None
        except Exception as e:
            logger.exception(f"Embedding generation failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Qdrant Context Retrieval
    # -------------------------------------------------------------------------
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

            logger.info(f"📦 Retrieved {len(context)} context items from Qdrant.")
            return context
        except Exception as e:
            logger.error(f"❌ Failed to fetch context: {e}")
            return []

    # -------------------------------------------------------------------------
    # Combined Analysis Pipeline
    # -------------------------------------------------------------------------
    def analyze(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Full pipeline:
        1. Detect intent
        2. Generate embedding
        3. Retrieve top-k similar context from Qdrant
        """
        intent = self.detect_intent(user_query)
        embedding = self.embed_query(user_query)
        context = self.fetch_context(embedding, top_k=top_k)

        logger.info(f"🧭 Analysis complete — intent: {intent}, context_items: {len(context)}")

        return {
            "intent": intent,
            "query_embedding": embedding,
            "context": context,
        }

# -----------------------------------------------------------------------------
# Quick Local Test
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    qa = QueryAnalyzer()
    result = qa.analyze("Predict next month's S3 cost trends.")
    print(result)
