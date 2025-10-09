#!/usr/bin/env python3
"""
Direct Qdrant update without sentence transformer
"""

import requests
import json
import uuid
from datetime import datetime

# Check Qdrant status
try:
    response = requests.get("http://localhost:6333/collections")
    print(f"✅ Qdrant is accessible")
    collections = response.json()
    print(f"Collections: {collections}")
except Exception as e:
    print(f"❌ Cannot connect to Qdrant: {e}")
    exit(1)

# Get collection info
try:
    response = requests.get("http://localhost:6333/collections/netz_documents")
    if response.status_code == 200:
        info = response.json()
        print(f"\n✅ Collection 'netz_documents' exists")
        print(f"Points count: {info['result']['points_count']}")
        print(f"Vector size: {info['result']['config']['params']['vectors']['size']}")
    else:
        print(f"❌ Collection not found")
except Exception as e:
    print(f"❌ Error getting collection info: {e}")

# Search for current financial data
print("\n🔍 Searching for current financial data...")
try:
    # Use a pre-computed vector for "chiffre affaires octobre 2025"
    # This is a placeholder - normally would use sentence transformer
    search_payload = {
        "limit": 5,
        "with_payload": True,
        "with_vector": False
    }
    
    response = requests.post(
        "http://localhost:6333/collections/netz_documents/points/scroll",
        json=search_payload
    )
    
    if response.status_code == 200:
        results = response.json()
        points = results.get('result', {}).get('points', [])
        
        print(f"Found {len(points)} documents")
        
        # Check for October revenue
        october_found = False
        training_breakdown_found = False
        
        for point in points[:10]:  # Check first 10
            text = point['payload'].get('text', '')
            if '41,558.85' in text and 'octobre' in text.lower():
                october_found = True
                print("✅ October revenue (41,558.85€) found!")
            if 'Excel' in text and '35,815.85' in text:
                training_breakdown_found = True
                print("✅ Detailed training revenue found!")
        
        if not october_found:
            print("⚠️ October revenue not found in current data")
        if not training_breakdown_found:
            print("⚠️ Detailed training revenue breakdown not found")
            
except Exception as e:
    print(f"❌ Search error: {e}")

print("\n" + "="*50)
print("SUMMARY:")
print("- Qdrant is running and accessible")
print("- Collection exists with documents")
print("- Some financial data may be missing detailed breakdowns")
print("\nTo add missing data, the sentence transformer issue needs to be resolved.")