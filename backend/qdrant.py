from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer


class Qdrant:
    collection: str
    client: QdrantClient
    model: SentenceTransformer

    def __init__(self, collection, host, port, embeddings_model_name):
        self.collection = collection
        self.client = QdrantClient(host=host, port=port)
        self.model = SentenceTransformer(embeddings_model_name)

    def search(self, text: str):
        # Convert text query into vector
        vector = self.model.encode(text).tolist()

        # Use `vector` for search for closest vectors in the collection
        search_result = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            query_filter=models.Filter(
                must_not=[
                    models.FieldCondition(key="text", match=models.MatchValue(value=""))
                ]
            ),
            limit=5
        )
        # `search_result` contains found vector ids with similarity scores along with the stored payload
        # In this function we are interested in payload only
        payloads = [hit.payload for hit in search_result]
        return payloads
