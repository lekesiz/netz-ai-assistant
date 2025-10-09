#!/usr/bin/env python3
"""
Clean old data and reload with accurate information
"""

from qdrant_client import QdrantClient
import time

# Initialize client
client = QdrantClient(url="http://localhost:6333")
collection_name = "netz_documents"

print("🧹 Cleaning and rebuilding NETZ AI data...")
print("="*50)

# Delete and recreate collection
try:
    print("Deleting old collection...")
    client.delete_collection(collection_name)
    time.sleep(1)
    print("✅ Old data cleared")
except Exception as e:
    print(f"⚠️  No existing collection to delete: {e}")

# Recreate collection
from qdrant_client.models import VectorParams, Distance

print("\nCreating new collection...")
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)
print("✅ Collection created")

print("\n" + "="*50)
print("✅ Database cleaned!")
print("\nNow run these commands to load fresh data:")
print("1. python load_real_data.py      # Company information")
print("2. python load_sample_financial.py  # Financial data")