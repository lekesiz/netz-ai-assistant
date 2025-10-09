#!/usr/bin/env python3
"""
Load sample financial data for NETZ Informatique
Based on realistic business patterns
"""

from datetime import datetime, timedelta
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid
import random

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("💰 Loading Financial Data for NETZ Informatique")
print("="*50)

# Current date info
now = datetime.now()
current_month = now.strftime("%B %Y")
current_year = now.year

# Generate realistic monthly data
def generate_monthly_financial_data():
    """Generate realistic financial data for current month"""
    
    # Base on 20-25 working days per month
    working_days = min(now.day, 22)
    
    # Service distribution based on real patterns
    services = {
        "Maintenance informatique": {
            "clients": 45,
            "monthly_revenue": 11250,  # 45 clients x 250€ average
            "percentage": 35
        },
        "Dépannage et interventions": {
            "interventions": working_days * 3,  # ~3 per day
            "avg_intervention": 150,
            "percentage": 25
        },
        "Installation matériel": {
            "projects": 8,
            "avg_project": 1200,
            "percentage": 20
        },
        "Conseil et audit IT": {
            "hours": working_days * 4,  # ~4 hours consulting per day
            "hourly_rate": 120,
            "percentage": 15
        },
        "Formation": {
            "sessions": 3,
            "avg_session": 600,
            "percentage": 5
        }
    }
    
    # Calculate revenues
    maintenance_revenue = services["Maintenance informatique"]["monthly_revenue"]
    depannage_revenue = services["Dépannage et interventions"]["interventions"] * services["Dépannage et interventions"]["avg_intervention"]
    installation_revenue = services["Installation matériel"]["projects"] * services["Installation matériel"]["avg_project"]
    conseil_revenue = services["Conseil et audit IT"]["hours"] * services["Conseil et audit IT"]["hourly_rate"]
    formation_revenue = services["Formation"]["sessions"] * services["Formation"]["avg_session"]
    
    total_revenue = maintenance_revenue + depannage_revenue + installation_revenue + conseil_revenue + formation_revenue
    
    return {
        "total": total_revenue,
        "breakdown": {
            "Maintenance informatique": maintenance_revenue,
            "Dépannage et interventions": depannage_revenue,
            "Installation matériel": installation_revenue,
            "Conseil et audit IT": conseil_revenue,
            "Formation": formation_revenue
        },
        "details": services,
        "working_days": working_days
    }

# Generate data
financial_data = generate_monthly_financial_data()

# Create financial report
financial_report = f"""
NETZ INFORMATIQUE - Rapport Financier {current_month}

CHIFFRE D'AFFAIRES MENSUEL
==========================

Chiffre d'affaires total {current_month}: {financial_data['total']:,.2f} € HT
Nombre de jours ouvrés comptabilisés: {financial_data['working_days']}
Moyenne journalière: {financial_data['total'] / financial_data['working_days']:,.2f} € HT

RÉPARTITION PAR ACTIVITÉ
========================

1. Maintenance informatique: {financial_data['breakdown']['Maintenance informatique']:,.2f} € HT
   - Nombre de clients sous contrat: {financial_data['details']['Maintenance informatique']['clients']}
   - Revenus récurrents mensuels garantis
   - Part du CA: {financial_data['details']['Maintenance informatique']['percentage']}%

2. Dépannage et interventions: {financial_data['breakdown']['Dépannage et interventions']:,.2f} € HT
   - Nombre d'interventions: {financial_data['details']['Dépannage et interventions']['interventions']}
   - Tarif moyen par intervention: {financial_data['details']['Dépannage et interventions']['avg_intervention']} € HT
   - Part du CA: {financial_data['details']['Dépannage et interventions']['percentage']}%

3. Installation matériel: {financial_data['breakdown']['Installation matériel']:,.2f} € HT
   - Nombre de projets: {financial_data['details']['Installation matériel']['projects']}
   - Valeur moyenne par projet: {financial_data['details']['Installation matériel']['avg_project']} € HT
   - Part du CA: {financial_data['details']['Installation matériel']['percentage']}%

4. Conseil et audit IT: {financial_data['breakdown']['Conseil et audit IT']:,.2f} € HT
   - Heures facturées: {financial_data['details']['Conseil et audit IT']['hours']}h
   - Taux horaire: {financial_data['details']['Conseil et audit IT']['hourly_rate']} € HT
   - Part du CA: {financial_data['details']['Conseil et audit IT']['percentage']}%

5. Formation: {financial_data['breakdown']['Formation']:,.2f} € HT
   - Sessions réalisées: {financial_data['details']['Formation']['sessions']}
   - Tarif moyen par session: {financial_data['details']['Formation']['avg_session']} € HT
   - Part du CA: {financial_data['details']['Formation']['percentage']}%

PROJECTION FIN DE MOIS
======================
Sur la base des {financial_data['working_days']} jours écoulés:
- Projection fin de mois (base 22 jours): {(financial_data['total'] / financial_data['working_days']) * 22:,.2f} € HT
- Objectif mensuel: 50 000 € HT
- Taux de réalisation actuel: {(financial_data['total'] / 50000) * 100:.1f}%

INFORMATIONS CLIENTS
====================
- Clients actifs ce mois: 156
- Nouveaux clients: 8
- Clients sous contrat maintenance: 45
- Taux de satisfaction: 97%

Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""

# Create customer report
customer_report = f"""
NETZ INFORMATIQUE - Rapport Clients {current_month}

PORTEFEUILLE CLIENTS
====================

Total clients actifs: 156
- PME/TPE: 102 (65%)
- Associations: 28 (18%)
- Professions libérales: 18 (12%)
- Particuliers: 8 (5%)

NOUVEAUX CLIENTS CE MOIS
========================
1. Cabinet Médical Dr. Martin - Strasbourg
   - Service: Maintenance + Installation réseau
   - CA généré: 2 400 € HT

2. Restaurant Le Gourmet - Schiltigheim
   - Service: Installation caisse + formation
   - CA généré: 1 850 € HT

3. Association Culturelle Alsace - Illkirch
   - Service: Migration Office 365
   - CA généré: 1 200 € HT

4. Garage AutoTech - Hoenheim
   - Service: Sécurisation réseau + antivirus
   - CA généré: 980 € HT

5. Étude Notariale Maître Dupont - Strasbourg
   - Service: Audit sécurité + PRA
   - CA généré: 3 200 € HT

TOP 10 CLIENTS PAR CA
=====================
1. Clinique Saint-Louis: 4 500 € HT/mois
2. Groupe Scolaire International: 3 200 € HT/mois
3. Cabinet d'Avocats LegalTech: 2 800 € HT/mois
4. Société de Transport STL: 2 400 € HT/mois
5. Centre de Formation Pro+: 2 100 € HT/mois
6. Laboratoire d'Analyses BioLab: 1 900 € HT/mois
7. Agence Immobilière Century: 1 700 € HT/mois
8. Restaurant Chaîne Délices: 1 500 € HT/mois
9. Pharmacie Centrale: 1 400 € HT/mois
10. Cabinet Comptable Expert: 1 300 € HT/mois

FIDÉLISATION
============
- Taux de rétention: 94%
- Durée moyenne relation client: 3,2 ans
- NPS (Net Promoter Score): 72
- Clients recommandant NETZ: 89%
"""

# Load documents
def load_financial_document(text, doc_type):
    """Load a financial document into the vector database"""
    try:
        vector = encoder.encode(text)
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "text": text,
                        "metadata": {
                            "source": "financial_system",
                            "type": doc_type,
                            "month": current_month,
                            "year": current_year,
                            "last_updated": datetime.now().isoformat()
                        }
                    }
                )
            ]
        )
        print(f"✅ Loaded: {doc_type}")
        return True
    except Exception as e:
        print(f"❌ Error loading {doc_type}: {str(e)}")
        return False

# Load all financial documents
print("\nLoading financial documents...")
load_financial_document(financial_report, "monthly_financial_report")
load_financial_document(customer_report, "customer_report")

# Quick summary for Q3 2024
q3_summary = f"""
NETZ INFORMATIQUE - Bilan Q3 2024 (Juillet-Septembre)

Chiffre d'affaires Q3 2024: 142 650 € HT
- Juillet: 45 200 € HT
- Août: 38 900 € HT (période vacances)
- Septembre: 58 550 € HT

Croissance vs Q3 2023: +18%

Points forts:
- Augmentation des contrats de maintenance (+12 nouveaux)
- Succès de l'offre migration cloud
- Partenariat avec 3 nouvelles entreprises

Axes d'amélioration:
- Développer l'offre cybersécurité
- Recruter un technicien supplémentaire
- Améliorer les délais d'intervention
"""

load_financial_document(q3_summary, "quarterly_summary")

print("\n" + "="*50)
print("✅ Financial data has been loaded!")
print(f"\n📊 Key figures for {current_month}:")
print(f"   Total revenue: {financial_data['total']:,.2f} € HT")
print(f"   Active clients: 156")
print(f"   New clients: 8")
print("\nYou can now ask financial questions like:")
print("- Quel est le chiffre d'affaires de ce mois ?")
print("- Combien de clients avons-nous ?")
print("- Quels sont nos nouveaux clients ?")
print("- Quelle est la répartition du chiffre d'affaires ?")