#!/usr/bin/env python3
"""
Simple demo data injection for NETZ AI Assistant
"""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from datetime import datetime
import random
import uuid

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

# Generate current month financial data
current_date = datetime.now()
current_month = current_date.strftime("%B %Y")
total_revenue = sum([random.randint(2000, 8000) for _ in range(current_date.day)])

# Financial report text
financial_text = f"""
Rapport Financier NETZ Informatique - {current_month}

CHIFFRE D'AFFAIRES DU MOIS EN COURS ({current_month}): {total_revenue:,} EUR

Détails financiers:
- Chiffre d'affaires total: {total_revenue:,} EUR
- Moyenne journalière: {total_revenue // current_date.day:,} EUR  
- Projection fin de mois: {(total_revenue // current_date.day) * 30:,} EUR

Répartition par service:
- Maintenance informatique: {int(total_revenue * 0.35):,} EUR (35%)
- Dépannage urgent: {int(total_revenue * 0.25):,} EUR (25%)
- Installation matériel: {int(total_revenue * 0.20):,} EUR (20%)
- Conseil et audit IT: {int(total_revenue * 0.15):,} EUR (15%)
- Formation: {int(total_revenue * 0.05):,} EUR (5%)

Informations clients:
- Clients actifs ce mois: 156
- Nouveaux clients: 12
- Taux de satisfaction: 96%

Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""

# Company info text
company_text = """
NETZ Informatique - Votre partenaire IT depuis 2015

Services proposés:
- Maintenance informatique préventive et corrective
- Dépannage rapide (intervention sous 2-4h)
- Installation et configuration de matériel
- Solutions réseau et sécurité
- Migration cloud et virtualisation
- Formation personnalisée

Certifications: QUALIOPI, ISO 9001, Microsoft Partner

Contact:
- Téléphone: +33 3 67 31 02 01
- Email: contact@netzinformatique.fr
- Adresse: Strasbourg, France

Horaires: Lundi-Vendredi 8h-18h, Support d'urgence 24/7
"""

try:
    # Check collection
    try:
        collection = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' exists with {collection.points_count} points")
    except:
        print(f"Collection '{collection_name}' not found")
        
    # Inject financial data
    financial_vector = encoder.encode(financial_text)
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=financial_vector.tolist(),
                payload={
                    "text": financial_text,
                    "metadata": {
                        "source": "financial_data",
                        "type": "monthly_report",
                        "month": current_month
                    }
                }
            )
        ]
    )
    print("✅ Financial data injected")
    
    # Inject company data
    company_vector = encoder.encode(company_text)
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=company_vector.tolist(),
                payload={
                    "text": company_text,
                    "metadata": {
                        "source": "company_info",
                        "type": "general_info"
                    }
                }
            )
        ]
    )
    print("✅ Company data injected")
    
    print(f"\n✅ Demo data successfully injected!")
    print(f"You can now ask about the revenue for {current_month}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")