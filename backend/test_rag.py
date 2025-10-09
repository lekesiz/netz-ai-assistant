from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import numpy as np

# Test Qdrant connection
client = QdrantClient("localhost", port=6333)

# Check collections
collections = client.get_collections()
print(f"Collections: {[col.name for col in collections.collections]}")

# Create a simple test collection
test_collection = "test_netz"
try:
    client.create_collection(
        collection_name=test_collection,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print(f"Created collection: {test_collection}")
except Exception as e:
    print(f"Collection might already exist: {e}")

# Add some test data
test_points = [
    PointStruct(
        id=1,
        vector=np.random.rand(384).tolist(),
        payload={
            "text": "NETZ Informatique est une société spécialisée dans les services informatiques à Haguenau.",
            "type": "company_info"
        }
    ),
    PointStruct(
        id=2,
        vector=np.random.rand(384).tolist(),
        payload={
            "text": "Nous proposons des formations QUALIOPI certifiées en bureautique et informatique.",
            "type": "service"
        }
    ),
    PointStruct(
        id=3,
        vector=np.random.rand(384).tolist(),
        payload={
            "text": "SIREN: 818 347 346 - Mikail Lekesiz est le gérant de NETZ Informatique.",
            "type": "legal_info"
        }
    )
]

# Insert points
client.upsert(collection_name=test_collection, points=test_points)
print(f"Inserted {len(test_points)} test points")

# Test search
search_result = client.search(
    collection_name=test_collection,
    query_vector=np.random.rand(384).tolist(),
    limit=2
)

print("\nSearch results:")
for result in search_result:
    print(f"- Score: {result.score:.3f}, Text: {result.payload['text'][:50]}...")

print("\nQdrant is working correctly!")