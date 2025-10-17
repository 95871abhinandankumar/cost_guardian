import json
import os
from vector_db.embedding_model import EmbeddingModel
from vector_db.qdrant_client_connector import QdrantConnector

def ingest_raw_data_to_qdrant():
    # Load raw data
    data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_data.json')
    with open(data_file, "r") as f:
        raw_data = json.load(f)

    # Convert each record to descriptive text
    def create_text(record):
        tags = ", ".join(f"{k}: {v}" for k, v in record.get("tags", {}).items())
        return f"{record['service_name']} usage on {record['usage_date']} in {record['region']}, {tags}, account: {record['account_id']}"

    texts = [create_text(r) for r in raw_data]

    # Generate embeddings
    model = EmbeddingModel()
    embeddings = model.encode(texts)

    # Push to Qdrant
    qdrant = QdrantConnector()
    qdrant.recreate_collection(vector_size=embeddings.shape[1])
    qdrant.upsert_points(embeddings, raw_data)

    print(f"✅ Successfully ingested {len(raw_data)} records to Qdrant")

# Run when executed directly
if __name__ == "__main__":
    ingest_raw_data_to_qdrant()
