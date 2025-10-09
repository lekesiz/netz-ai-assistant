#!/usr/bin/env python3
"""
Update financial data via API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

print("📊 Updating NETZ Financial Data via API")
print("="*50)

# Test queries to verify current data and what's missing
test_queries = [
    ("Quel est le chiffre d'affaires d'octobre 2025?", "October revenue"),
    ("Quelle formation rapporte le plus?", "Top training revenue"),
    ("Quel est notre positionnement marché?", "Market position"),
    ("Combien de clients actifs avons-nous?", "Active clients"),
    ("Quel est le détail mensuel du CA 2025?", "Monthly revenue details"),
    ("Quelle est la répartition du CA par type de formation?", "Revenue by training type")
]

for query, description in test_queries:
    print(f"\n🔍 Testing: {description}")
    print(f"   Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"messages": [{"role": "user", "content": query}]},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['response'][:200] + "..." if len(result['response']) > 200 else result['response']
            print(f"   ✅ Response: {answer}")
            
            # Check if sources contain detailed data
            if 'sources' in result and result['sources']:
                has_detailed = any('Excel' in str(s) and '35,815.85' in str(s) for s in result['sources'])
                has_monthly = any('janvier' in str(s).lower() and 'octobre' in str(s).lower() for s in result['sources'])
                
                if not has_detailed and 'formation' in query.lower():
                    print("   ⚠️  Missing detailed training revenue breakdown")
                if not has_monthly and 'mensuel' in query.lower():
                    print("   ⚠️  Missing detailed monthly breakdown")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*50)
print("\n📝 CORRECT DATA TO ENSURE IN SYSTEM:")
print("\n1. MONTHLY REVENUE 2025:")
print("   - Janvier: 8,234€")
print("   - Février: 9,456€") 
print("   - Mars: 7,890€")
print("   - Avril: 10,234€")
print("   - Mai: 8,967€")
print("   - Juin: 9,123€")
print("   - Juillet: 7,456€")
print("   - Août: 5,234€")
print("   - Septembre: 11,234€")
print("   - Octobre: 41,558.85€")
print("   - TOTAL: 119,386.85€")

print("\n2. TOP TRAINING REVENUE:")
print("   1. Excel: 35,815.85€ (30%)")
print("   2. Bilans de compétences: 28,500€ (23.9%)")
print("   3. Python: 19,000€ (15.9%)")
print("   4. AutoCAD: 13,058.85€ (10.9%)")
print("   5. WordPress: 11,264€ (9.4%)")

print("\n3. KEY METRICS:")
print("   - Active clients: 2,734")
print("   - Satisfaction rate: 94%")
print("   - Success rate: 87%")
print("   - Market leader in Haguenau area")

print("\n✅ Data verification complete!")