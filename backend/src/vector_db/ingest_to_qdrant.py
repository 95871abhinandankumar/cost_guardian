"""
ingest_to_qdrant.py
-------------------
Load raw data, generate embeddings, and ingest into Qdrant.
"""

import json
import os
import logging
from typing import List, Dict
from vector_db.embedding_model import EmbeddingModel
from vector_db.qdrant_client_connector import QdrantConnector

# --------------------------- Logging Configuration --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_text(record: Dict) -> str:
    """
    Convert a raw data record to descriptive text for embedding.

    Args:
        record (Dict): Single raw data record.

    Returns:
        str: Concatenated descriptive text.
    """
    tags = ", ".join(f"{k}: {v}" for k, v in record.get("tags", {}).items())
    return f"{record['service_name']} usage on {record['usage_date']} in {record['region']}, {tags}, account: {record['account_id']}"


def ingest_raw_data_to_qdrant() -> None:
    """
    Load raw data, generate embeddings using SentenceTransformer,
    and ingest them into Qdrant.
    """
    try:
        # Load raw data
        data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_data.json')
        if not os.path.exists(data_file):
            logger.error("Raw data file not found: %s", data_file)
            return

        with open(data_file, "r") as f:
            raw_data: List[Dict] = json.load(f)
        if not raw_data:
            logger.warning("No data found in raw_data.json")
            return

        # Convert records to descriptive text
        texts: List[str] = [create_text(r) for r in raw_data]

        # Generate embeddings
        model = EmbeddingModel()
        embeddings = model.encode(texts)

        # Push to Qdrant
        qdrant = QdrantConnector()
        qdrant.recreate_collection(vector_size=embeddings.shape[1])
        qdrant.upsert_points(embeddings, raw_data)

        logger.info("✅ Successfully ingested %d records to Qdrant", len(raw_data))

    except Exception as e:
        logger.error("Failed to ingest data to Qdrant: %s", e, exc_info=True)


# --------------------------- Direct Execution --------------------------- #
if __name__ == "__main__":
    try:
        ingest_raw_data_to_qdrant()
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as err:
        logger.exception("Unexpected error occurred: %s", err)
