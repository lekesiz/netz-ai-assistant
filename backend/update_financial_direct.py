#!/usr/bin/env python3
"""
Direct financial data update without blocking
"""

import requests
import json
from datetime import datetime

# API endpoint
API_URL = "http://localhost:8000/api/search"

# Test if API is responsive
try:
    response = requests.post(
        API_URL,
        json={"query": "chiffre affaires octobre", "limit": 1},
        timeout=5
    )
    
    if response.status_code == 200:
        results = response.json()
        print("✅ API is responsive")
        print(f"Current results: {len(results.get('results', []))} documents found")
        
        # Check current October revenue in results
        for result in results.get('results', []):
            if 'octobre' in result['text'].lower() and '41,558.85' in result['text']:
                print("\n✅ October revenue (41,558.85€) is already in the system!")
                print(f"Score: {result['score']}")
                print(f"Text preview: {result['text'][:200]}...")
            else:
                print("\n⚠️ October revenue not found with correct amount")
    else:
        print(f"❌ API returned status {response.status_code}")
        
except Exception as e:
    print(f"❌ API connection error: {e}")
    print("\nPlease ensure:")
    print("1. FastAPI server is running (python fast_api.py)")
    print("2. Qdrant is accessible")
    print("3. No firewall blocking port 8000")

# Quick data summary for verification
print("\n" + "="*50)
print("DONNÉES FINANCIÈRES CORRECTES:")
print("- Octobre 2025: 41,558.85€ HT")
print("- Total Jan-Oct 2025: 119,386.85€ HT")
print("- Projection 2025: 143,264.22€ HT")
print("\nFORMATIONS LES PLUS RENTABLES:")
print("1. Excel: 35,815.85€ (30% du CA)")
print("2. Bilans de compétences: 28,500€ (23.9%)")
print("3. Python: 19,000€ (15.9%)")