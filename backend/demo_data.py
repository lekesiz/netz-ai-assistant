"""
Demo data for NETZ AI Assistant
Creates sample financial and company data for demonstration
"""

import json
from datetime import datetime, timedelta
import random
from rag_service import get_rag_service

def create_demo_financial_data():
    """Create demo financial data for the current month"""
    
    current_date = datetime.now()
    current_month = current_date.strftime("%B %Y")
    
    # Generate demo revenue data
    daily_revenues = []
    total_revenue = 0
    
    for day in range(1, current_date.day + 1):
        daily_revenue = random.randint(2000, 8000)  # Between 2k and 8k per day
        daily_revenues.append({
            "date": f"{day:02d}/{current_date.month:02d}/{current_date.year}",
            "revenue": daily_revenue,
            "invoices": random.randint(3, 15)
        })
        total_revenue += daily_revenue
    
    # Create financial summary
    financial_data = {
        "company": "NETZ Informatique",
        "month": current_month,
        "currency": "EUR",
        "revenue": {
            "total": total_revenue,
            "average_daily": total_revenue / current_date.day,
            "projection_month": (total_revenue / current_date.day) * 30,
            "daily_breakdown": daily_revenues
        },
        "top_services": [
            {"name": "Maintenance Informatique", "revenue": int(total_revenue * 0.35)},
            {"name": "Dépannage", "revenue": int(total_revenue * 0.25)},
            {"name": "Installation Matériel", "revenue": int(total_revenue * 0.20)},
            {"name": "Conseil IT", "revenue": int(total_revenue * 0.15)},
            {"name": "Formation", "revenue": int(total_revenue * 0.05)}
        ],
        "customer_stats": {
            "total_customers": 156,
            "new_customers": 12,
            "recurring_customers": 144
        },
        "last_updated": datetime.now().isoformat()
    }
    
    return financial_data

def create_demo_company_data():
    """Create demo company information"""
    
    company_data = {
        "name": "NETZ Informatique",
        "address": "123 Rue de la Technologie, 67000 Strasbourg",
        "phone": "+33 3 67 31 02 01",
        "email": "contact@netzinformatique.fr",
        "website": "www.netzinformatique.fr",
        "founded": "2015",
        "employees": 12,
        "certifications": ["QUALIOPI", "ISO 9001", "Microsoft Partner"],
        "services": [
            {
                "name": "Maintenance Informatique",
                "description": "Maintenance préventive et corrective de votre parc informatique",
                "sla": "Intervention sous 4h",
                "price_range": "50-150€/heure"
            },
            {
                "name": "Dépannage",
                "description": "Résolution rapide de tous vos problèmes informatiques",
                "sla": "Intervention sous 2h en urgence",
                "price_range": "80-200€/intervention"
            },
            {
                "name": "Installation Matériel",
                "description": "Installation et configuration de matériel informatique",
                "sla": "Sur rendez-vous",
                "price_range": "100-500€/installation"
            },
            {
                "name": "Conseil IT",
                "description": "Accompagnement dans vos projets de transformation digitale",
                "sla": "Sur rendez-vous",
                "price_range": "150-300€/heure"
            },
            {
                "name": "Formation",
                "description": "Formation sur mesure pour vos équipes",
                "sla": "Planning flexible",
                "price_range": "500-2000€/jour"
            }
        ],
        "expertise": [
            "Infrastructure réseau",
            "Sécurité informatique",
            "Solutions cloud",
            "Virtualisation",
            "Sauvegarde et récupération",
            "Support utilisateur"
        ]
    }
    
    return company_data

def inject_demo_data():
    """Inject demo data into the RAG system"""
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import VectorParams, Distance, PointStruct
        from sentence_transformers import SentenceTransformer
        import uuid
        
        # Initialize services
        client = QdrantClient(url="http://localhost:6333")
        encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        collection_name = "netz_documents"
        
        # Ensure collection exists
        try:
            collection_info = client.get_collection(collection_name)
            print(f"Using existing collection: {collection_name}")
        except:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"Created new collection: {collection_name}")
        
        # Get demo data
        financial_data = create_demo_financial_data()
        company_data = create_demo_company_data()
        
        # Format financial summary
        financial_text = f"""
Rapport Financier - {financial_data['month']}
NETZ Informatique

Chiffre d'affaires total du mois en cours ({financial_data['month']}): {financial_data['revenue']['total']:,} EUR

Détails:
- Chiffre d'affaires moyen par jour: {financial_data['revenue']['average_daily']:,.0f} EUR
- Projection fin de mois: {financial_data['revenue']['projection_month']:,.0f} EUR
- Nombre de jours comptabilisés: {len(financial_data['revenue']['daily_breakdown'])}

Répartition par service:
"""
        
        for service in financial_data['top_services']:
            financial_text += f"- {service['name']}: {service['revenue']:,} EUR\n"
        
        financial_text += f"""
Statistiques clients:
- Clients actifs: {financial_data['customer_stats']['total_customers']}
- Nouveaux clients ce mois: {financial_data['customer_stats']['new_customers']}
- Clients récurrents: {financial_data['customer_stats']['recurring_customers']}

Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""
        
        # Add financial data to vector store
        financial_embedding = encoder.encode(financial_text)
        
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=financial_embedding.tolist(),
                    payload={
                        "text": financial_text,
                        "metadata": {
                            "source": "pennylane_demo",
                            "type": "financial_report",
                            "month": financial_data['month'],
                            "last_updated": financial_data['last_updated']
                        }
                    }
                )
            ]
        )
        
        # Format company information
        company_text = f"""
NETZ Informatique - Présentation de l'entreprise

{company_data['name']} est une entreprise spécialisée dans les services informatiques depuis {company_data['founded']}.

Coordonnées:
- Adresse: {company_data['address']}
- Téléphone: {company_data['phone']}
- Email: {company_data['email']}
- Site web: {company_data['website']}

Effectif: {company_data['employees']} collaborateurs

Certifications:
"""
        
        for cert in company_data['certifications']:
            company_text += f"- {cert}\n"
        
        company_text += "\nNos Services:\n"
        
        for service in company_data['services']:
            company_text += f"""
{service['name']}:
- Description: {service['description']}
- SLA: {service['sla']}
- Tarifs: {service['price_range']}
"""
        
        company_text += "\nDomaines d'expertise:\n"
        for expertise in company_data['expertise']:
            company_text += f"- {expertise}\n"
        
        # Add company data to vector store
        company_embedding = encoder.encode(company_text)
        
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=company_embedding.tolist(),
                    payload={
                        "text": company_text,
                        "metadata": {
                            "source": "company_info",
                            "type": "company_presentation",
                            "last_updated": datetime.now().isoformat()
                        }
                    }
                )
            ]
        )
        
        print("Demo data successfully injected into RAG system")
        return True
        
    except Exception as e:
        print(f"Error injecting demo data: {str(e)}")
        return False

if __name__ == "__main__":
    inject_demo_data()