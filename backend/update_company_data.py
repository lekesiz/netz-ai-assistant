#!/usr/bin/env python3
"""
Update NETZ Informatique company data with real information
Please edit the values below with your actual company data
"""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("📝 NETZ Informatique - Real Data Update")
print("="*50)
print("⚠️  IMPORTANT: Please edit this file with your real company data!")
print("="*50)

# ========================================
# PLEASE UPDATE THESE WITH YOUR REAL DATA
# ========================================

# 1. COMPANY INFORMATION (Update with real values)
REAL_COMPANY_DATA = {
    "name": "NETZ INFORMATIQUE",
    "legal_form": "SASU",  # Update if different
    "siret": "XXX XXX XXX XXXXX",  # ← ENTER YOUR REAL SIRET
    "ape_code": "XXXXX",  # ← ENTER YOUR REAL APE CODE
    "vat_number": "FRXXXXXXXXXX",  # ← ENTER YOUR VAT NUMBER
    "capital": "X XXX €",  # ← ENTER YOUR CAPITAL
    
    "address": {
        "street": "YOUR STREET ADDRESS",  # ← ENTER REAL ADDRESS
        "postal_code": "XXXXX",  # ← ENTER POSTAL CODE
        "city": "YOUR CITY",  # ← ENTER CITY
        "country": "France"
    },
    
    "contact": {
        "phone": "+33 X XX XX XX XX",  # ← ENTER REAL PHONE
        "email": "contact@netzinformatique.fr",  # ← UPDATE IF DIFFERENT
        "website": "www.netzinformatique.fr"
    },
    
    "director": "Mikail LEKESIZ",  # ← UPDATE IF DIFFERENT
    "creation_date": "XX/XX/XXXX",  # ← ENTER CREATION DATE
    
    "certifications": [
        # ← ADD YOUR REAL CERTIFICATIONS
        "Certification 1",
        "Certification 2",
    ]
}

# 2. SERVICES (Update with your real services)
REAL_SERVICES = [
    {
        "name": "Service Name 1",  # ← ENTER SERVICE NAME
        "description": "Detailed description",  # ← ENTER DESCRIPTION
        "price": "Price information",  # ← ENTER PRICE
        "sla": "Response time"  # ← ENTER SLA
    },
    {
        "name": "Service Name 2",
        "description": "Detailed description",
        "price": "Price information",
        "sla": "Response time"
    },
    # ← ADD MORE SERVICES
]

# 3. PRICING (Update with your real pricing)
REAL_PRICING = {
    "hourly_rates": {
        "standard": "XX €/hour",  # ← ENTER RATE
        "urgent": "XX €/hour",  # ← ENTER RATE
        "weekend": "XX €/hour"  # ← ENTER RATE
    },
    "maintenance_packages": [
        {
            "name": "Package 1",  # ← ENTER NAME
            "price": "XXX €/month",  # ← ENTER PRICE
            "includes": ["Feature 1", "Feature 2"]  # ← ENTER FEATURES
        },
        # ← ADD MORE PACKAGES
    ],
    "travel_fees": "Your travel fee policy"  # ← ENTER POLICY
}

# ========================================
# DO NOT MODIFY BELOW THIS LINE
# ========================================

def create_company_document():
    """Create company information document"""
    doc = f"""
{REAL_COMPANY_DATA['name']} - Informations Officielles

Forme juridique: {REAL_COMPANY_DATA['legal_form']}
SIRET: {REAL_COMPANY_DATA['siret']}
Code APE: {REAL_COMPANY_DATA['ape_code']}
TVA Intracommunautaire: {REAL_COMPANY_DATA['vat_number']}
Capital social: {REAL_COMPANY_DATA['capital']}

Siège social:
{REAL_COMPANY_DATA['address']['street']}
{REAL_COMPANY_DATA['address']['postal_code']} {REAL_COMPANY_DATA['address']['city']}
{REAL_COMPANY_DATA['address']['country']}

Contact:
Téléphone: {REAL_COMPANY_DATA['contact']['phone']}
Email: {REAL_COMPANY_DATA['contact']['email']}
Site web: {REAL_COMPANY_DATA['contact']['website']}

Dirigeant: {REAL_COMPANY_DATA['director']}
Date de création: {REAL_COMPANY_DATA['creation_date']}

Certifications:
"""
    for cert in REAL_COMPANY_DATA['certifications']:
        doc += f"- {cert}\n"
    
    return doc

def create_services_document():
    """Create services catalog document"""
    doc = f"{REAL_COMPANY_DATA['name']} - Catalogue des Services\n\n"
    
    for i, service in enumerate(REAL_SERVICES, 1):
        doc += f"""
{i}. {service['name'].upper()}
Description: {service['description']}
Tarif: {service['price']}
SLA: {service['sla']}
"""
    
    return doc

def create_pricing_document():
    """Create pricing document"""
    doc = f"""
{REAL_COMPANY_DATA['name']} - Grille Tarifaire

TARIFS HORAIRES:
- Intervention standard: {REAL_PRICING['hourly_rates']['standard']}
- Intervention urgente: {REAL_PRICING['hourly_rates']['urgent']}
- Intervention weekend: {REAL_PRICING['hourly_rates']['weekend']}

FORFAITS MAINTENANCE:
"""
    
    for package in REAL_PRICING['maintenance_packages']:
        doc += f"\n{package['name']}: {package['price']}\n"
        doc += "Inclus:\n"
        for feature in package['includes']:
            doc += f"- {feature}\n"
    
    doc += f"\nFRAIS DE DÉPLACEMENT:\n{REAL_PRICING['travel_fees']}\n"
    
    return doc

# Check if data has been updated
if REAL_COMPANY_DATA['siret'] == "XXX XXX XXX XXXXX":
    print("\n❌ ERROR: Please edit this file and enter your real company data!")
    print("   File location: backend/update_company_data.py")
    print("\n   Required information:")
    print("   - SIRET number")
    print("   - Company address")
    print("   - Services list")
    print("   - Pricing information")
    exit(1)

# Load documents into vector database
def load_document(text, doc_type):
    """Load document into vector database"""
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
                            "source": "company_data",
                            "type": doc_type,
                            "last_updated": datetime.now().isoformat()
                        }
                    }
                )
            ]
        )
        print(f"✅ Loaded: {doc_type}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Create and load documents
print("\nCreating documents from your data...")
company_doc = create_company_document()
services_doc = create_services_document()
pricing_doc = create_pricing_document()

print("\nLoading into database...")
load_document(company_doc, "company_information")
load_document(services_doc, "services_catalog")
load_document(pricing_doc, "pricing_information")

print("\n" + "="*50)
print("✅ Company data updated successfully!")
print("\nThe AI assistant will now use your real company information.")