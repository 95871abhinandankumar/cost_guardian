"""Ingest cost data from SQLite to Qdrant for semantic search."""

import os
import sqlite3
import logging
from typing import List, Dict
from vector_db.embedding_model import EmbeddingModel
from vector_db.qdrant_client_connector import QdrantConnector

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def create_text(record: Dict) -> str:
    """Convert record to searchable text."""
    tags_str = f", tags: {record.get('tags', '')}" if record.get('tags') else ""
    return (
        f"{record['service_name']} usage on {record['usage_date']} "
        f"in {record.get('region', 'unknown')}, cost: ${record.get('cost', 0):.2f}, "
        f"usage: {record.get('usage_quantity', 0)}, account: {record['account_id']}"
        f"{tags_str}, anomaly: {'yes' if record.get('anomaly_flag') else 'no'}"
    )


def load_data_from_sqlite() -> List[Dict]:
    """Load data from SQLite database."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cost_guardian.db')
    
    if not os.path.exists(db_path):
        logger.error("Database file not found: %s", db_path)
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_usage ORDER BY usage_date DESC")
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        logger.info("Loaded %d records", len(records))
        return records
    except Exception as e:
        logger.error("Failed to load data: %s", e)
        return []


def ingest_database_to_qdrant() -> None:
    """Ingest data to Qdrant vector database."""
    try:
        data = load_data_from_sqlite()
        if not data:
            return
        
        texts: List[str] = [create_text(r) for r in data]
        model = EmbeddingModel()
        embeddings = model.encode(texts)
        
        qdrant = QdrantConnector()
        qdrant.recreate_collection(vector_size=embeddings.shape[1])
        qdrant.upsert_points(embeddings, data)
        
        logger.info("Successfully ingested %d records", len(data))
    except Exception as e:
        logger.error("Failed to ingest: %s", e, exc_info=True)


if __name__ == "__main__":
    try:
        ingest_database_to_qdrant()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as err:
        logger.exception("Error: %s", err)
