"""
dem_qdrant.py
-------------
Connects to a local Qdrant instance, lists collections, counts records,
and fetches sample points for inspection.
"""

import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import CollectionDescription

# --------------------------- Logging Configuration --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def connect_qdrant(url: str = "http://localhost:6333") -> Optional[QdrantClient]:
    """Connect to a local Qdrant instance."""
    try:
        client = QdrantClient(url=url, check_compatibility=False)
        logger.info("Connected to Qdrant at %s", url)
        return client
    except Exception as e:
        logger.error("Failed to connect to Qdrant: %s", e, exc_info=True)
        return None


def list_collections(client: QdrantClient) -> list[CollectionDescription]:
    """List all collections and their vector info."""
    try:
        response = client.get_collections()
        collections = response.collections or []

        if not collections:
            logger.warning("No collections found in Qdrant.")
            return []

        logger.info("Found %d collections:", len(collections))
        for col in collections:
            vectors_info = getattr(col, "vectors", None)
            size = getattr(vectors_info, "size", "unknown")
            distance = getattr(vectors_info, "distance", "unknown")
            logger.info("• %s (vector size: %s, distance: %s)", col.name, size, distance)

        return collections
    except Exception as e:
        logger.error("Error listing collections: %s", e, exc_info=True)
        return []


def inspect_collection(client: QdrantClient, collection_name: str, sample_limit: int = 5) -> None:
    """Count records and fetch sample points from a collection."""
    try:
        count = client.count(collection_name)
        logger.info("Collection '%s' contains %d records.", collection_name, count.count)

        points, _ = client.scroll(collection_name=collection_name, limit=sample_limit)
        if not points:
            logger.warning("No points found in collection '%s'.", collection_name)
            return

        logger.info("Sample records (up to %d):", sample_limit)
        for idx, pt in enumerate(points, start=1):
            logger.info("[%d] %s", idx, pt.payload)

    except Exception as e:
        logger.error("Error inspecting collection '%s': %s", collection_name, e, exc_info=True)


def main() -> None:
    """Main execution flow."""
    client = connect_qdrant()
    if not client:
        return

    collections = list_collections(client)
    if not collections:
        return

    first_collection = collections[0].name
    inspect_collection(client, first_collection)


if __name__ == "__main__":
    try:
        main()
        logger.info("✅ Qdrant demo complete.")
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as err:
        logger.exception("Unexpected error occurred: %s", err)
