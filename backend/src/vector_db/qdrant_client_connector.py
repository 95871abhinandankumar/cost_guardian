from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams

class QdrantConnector:
    def __init__(self, url="http://localhost:6333", collection_name="cost_data"):
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name

    def recreate_collection(self, vector_size):
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance="Cosine")
        )

    def upsert_points(self, embeddings, payloads):
        points = [PointStruct(id=i, vector=embeddings[i].tolist(), payload=payloads[i])
                  for i in range(len(payloads))]
        self.client.upsert(collection_name=self.collection_name, points=points)
