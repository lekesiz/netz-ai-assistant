"""
Quick training and testing script for NETZ AI
"""

import asyncio
import json
from datetime import datetime
from lightweight_rag import LightweightRAG
import httpx


async def quick_train_and_test():
    """Quick training and testing"""
    print("🚀 Starting NETZ AI Quick Training...")
    
    rag = LightweightRAG()
    
    # Add essential NETZ training data
    training_data = [
        {
            "content": "NETZ Informatique est une entreprise de services informatiques basée à Haguenau. Fondée par Mikail Lekesiz, elle propose dépannage, formation, maintenance et développement web. Contact: 07 67 74 49 03",
            "metadata": {"type": "company_info", "importance": "5"}
        },
        {
            "content": "Tarifs NETZ: Diagnostic gratuit. Dépannage 55€/h particuliers, 75€/h entreprises. Formations dès 45€/h. Maintenance dès 39€/mois.",
            "metadata": {"type": "pricing", "importance": "5"}
        },
        {
            "content": "NETZ est certifié QUALIOPI pour les formations. Formations éligibles CPF et OPCO. Catalogue: Excel, Word, Python, Cybersécurité.",
            "metadata": {"type": "training", "importance": "5"}
        },
        {
            "content": "Zone intervention: Haguenau et 30km. Déplacement gratuit dans Haguenau. Horaires: Lun-Ven 9h-19h, Sam 10h-17h.",
            "metadata": {"type": "service_area", "importance": "4"}
        },
        {
            "content": "Services NETZ: Dépannage rapide, formations professionnelles, maintenance préventive, développement web, vente matériel reconditionné.",
            "metadata": {"type": "services", "importance": "5"}
        }
    ]
    
    # Add training data
    print("\n📚 Adding training data...")
    for i, data in enumerate(training_data):
        rag.add_document(
            content=data["content"],
            title=f"NETZ Training {i+1}",
            source="quick_training", 
            doc_type="training",
            metadata=data["metadata"]
        )
    
    print(f"✅ Added {len(training_data)} training examples")
    
    # Test the AI
    print("\n🧪 Testing AI responses...")
    
    test_queries = [
        "Qu'est-ce que NETZ Informatique?",
        "Quels sont vos tarifs?",
        "Proposez-vous des formations?",
        "Quelle est votre zone d'intervention?",
        "Comment vous contacter?"
    ]
    
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ API is running")
                
                # Test queries
                for query in test_queries:
                    response = await client.post(
                        "http://localhost:8000/api/chat",
                        json={"messages": [{"role": "user", "content": query}]},
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"\n❓ Q: {query}")
                        print(f"✅ A: {result.get('response', 'No response')[:200]}...")
                    else:
                        print(f"\n❌ Error for query: {query}")
            else:
                print("❌ API health check failed")
                
    except Exception as e:
        print(f"⚠️  API not running. Please start with: uvicorn simple_api:app --reload")
        print(f"   Error: {str(e)}")
        
        # Test RAG directly
        print("\n📊 Testing RAG directly...")
        for query in test_queries[:2]:
            results = rag.search(query, k=3)
            print(f"\n❓ Query: {query}")
            if results:
                print(f"✅ Found {len(results)} relevant results")
                print(f"   Best match: {results[0]['content'][:100]}...")
            else:
                print("❌ No results found")
    
    print("\n✨ Quick training and testing complete!")


if __name__ == "__main__":
    asyncio.run(quick_train_and_test())