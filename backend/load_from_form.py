#!/usr/bin/env python3
"""
Load company data from the filled form
"""

import os
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("📝 Loading NETZ Informatique Data from Form")
print("="*50)

# Read the form file
form_path = Path("/Users/mikail/Desktop/NETZ-AI-Project/ENTER_YOUR_DATA.md")

if not form_path.exists():
    print("❌ Error: Form file not found!")
    print(f"   Please fill out: {form_path}")
    exit(1)

# Read form content
with open(form_path, 'r', encoding='utf-8') as f:
    form_content = f.read()

# Check if form is filled
if form_content.count("_________________________________") > 20:
    print("❌ Error: Form appears to be unfilled!")
    print("   Please fill out all fields in ENTER_YOUR_DATA.md")
    exit(1)

# Clean collection first
try:
    print("\nCleaning old data...")
    client.delete_collection(collection_name)
    from qdrant_client.models import VectorParams, Distance
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    print("✅ Collection cleaned and recreated")
except Exception as e:
    print(f"⚠️  Collection clean failed: {e}")

# Load the form content as company data
def load_document(text, doc_type, doc_id=None):
    """Load document into vector database"""
    try:
        vector = encoder.encode(text)
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=doc_id or str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "text": text,
                        "metadata": {
                            "source": "company_form",
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

# Split form into sections
sections = form_content.split("\n## ")

# Load each section
for section in sections:
    if not section.strip():
        continue
        
    lines = section.strip().split('\n')
    title = lines[0].replace('🏢', '').replace('📍', '').replace('📞', '').replace('📜', '').replace('💼', '').replace('💰', '').replace('📊', '').strip()
    
    if title and len(lines) > 1:
        content = '\n'.join(lines[1:])
        if not content.count("_________________________________") > 3:  # Section has real content
            doc_text = f"NETZ Informatique - {title}\n\n{content}"
            load_document(doc_text, title.lower().replace(' ', '_'))

# Load the complete form as one document
load_document(form_content, "complete_company_information", "main_company_doc")

# Also load sample financial data
financial_report = f"""
NETZ INFORMATIQUE - Informations Financières

D'après les données disponibles:
- Forme juridique: Société par Actions Simplifiée Unipersonnelle (SASU)
- Dirigeant: Mikail LEKESIZ
- Activité: Conseil en systèmes et logiciels informatiques
- Services: Maintenance informatique, dépannage, formation, conseil IT
- Zone d'intervention: Strasbourg et région Grand Est

Note: Les informations financières détaillées seront mises à jour après connexion avec le système comptable.
"""

load_document(financial_report, "financial_information")

print("\n" + "="*50)
print("✅ Data loaded successfully!")
print("\nThe AI assistant will now use the information from your form.")
print("\nYou can test by asking questions like:")
print("- Quel est le numéro SIRET ?")
print("- Quelle est l'adresse de NETZ ?")
print("- Quels services proposez-vous ?")
print("- Quels sont vos tarifs ?")