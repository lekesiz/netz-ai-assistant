#!/usr/bin/env python3
"""
Load real company data into NETZ AI Assistant
"""

import os
import json
from datetime import datetime
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("📚 Loading Real Company Data into NETZ AI")
print("="*50)

# 1. Company Information
company_info = """
NETZ INFORMATIQUE - Informations Officielles

Raison sociale: NETZ INFORMATIQUE
Forme juridique: SASU (Société par Actions Simplifiée Unipersonnelle)
Capital social: 1 000,00 €
SIRET: 810 351 353 00026
APE/NAF: 6202A - Conseil en systèmes et logiciels informatiques
TVA Intracommunautaire: FR67810351353

Siège social:
3 Rue Jean Monnet
67201 ECKBOLSHEIM
France

Contact:
Téléphone: +33 3 67 31 02 01
Email: contact@netzinformatique.fr
Site web: www.netzinformatique.fr

Dirigeant:
Mikail LEKESIZ - Président

Date de création: 23/02/2015

Activités principales:
- Conseil en systèmes informatiques
- Maintenance et dépannage informatique
- Installation de matériel informatique
- Formation informatique
- Solutions de sauvegarde et sécurité
- Services cloud et virtualisation

Certifications et agréments:
- Certification QUALIOPI (Actions de formation)
- Organisme de formation enregistré sous le n° 44670598567
- Partenaire Microsoft
- Partenaire OVHcloud

Horaires d'ouverture:
Lundi - Vendredi: 8h00 - 18h00
Support d'urgence: 24h/7j sur contrat

Zone d'intervention:
- Strasbourg et Eurométropole
- Bas-Rhin (67)
- Région Grand Est
- Intervention nationale sur demande
"""

# 2. Services détaillés
services_info = """
NETZ INFORMATIQUE - Catalogue des Services

1. MAINTENANCE INFORMATIQUE
- Maintenance préventive mensuelle
- Mise à jour des systèmes
- Surveillance proactive
- Rapports mensuels détaillés
- Tarif: À partir de 49€ HT/poste/mois
- SLA: Intervention sous 4h ouvrées

2. DÉPANNAGE INFORMATIQUE
- Diagnostic et résolution de pannes
- Intervention sur site ou à distance
- Récupération de données
- Remplacement de matériel défectueux
- Tarif: 60-120€ HT/heure selon urgence
- SLA: Intervention sous 2h en urgence

3. INSTALLATION & CONFIGURATION
- Installation de postes de travail
- Configuration réseau
- Mise en place de serveurs
- Installation d'imprimantes et périphériques
- Tarif: Sur devis selon projet
- Délai: 1-5 jours selon disponibilité

4. SÉCURITÉ INFORMATIQUE
- Audit de sécurité
- Installation antivirus/firewall
- Mise en place de sauvegardes
- Plan de reprise d'activité (PRA)
- Formation aux bonnes pratiques
- Tarif: Audit à partir de 500€ HT

5. SOLUTIONS CLOUD
- Migration vers le cloud
- Office 365 / Google Workspace
- Sauvegarde cloud
- Travail collaboratif
- Tarif: Accompagnement à partir de 300€ HT

6. FORMATION INFORMATIQUE
- Formation bureautique (Office, LibreOffice)
- Formation sécurité informatique
- Formation outils collaboratifs
- Formation sur mesure
- Tarif: 400-800€ HT/jour selon effectif
- Éligible CPF et OPCO
"""

# 3. Tarifs et conditions
pricing_info = """
NETZ INFORMATIQUE - Grille Tarifaire 2025

TARIFS HORAIRES:
- Intervention standard (9h-18h): 60€ HT/heure
- Intervention urgente (2h): 90€ HT/heure
- Intervention soir/weekend: 120€ HT/heure
- Télémaintenance: 50€ HT/heure

FORFAITS MAINTENANCE:
- BASIC (5 postes max): 245€ HT/mois
  * 1 intervention préventive/mois
  * Support téléphonique illimité
  * Mises à jour incluses
  
- PRO (10 postes max): 450€ HT/mois
  * 2 interventions préventives/mois
  * Support prioritaire
  * Monitoring 24/7
  
- ENTERPRISE (illimité): Sur devis
  * Technicien dédié
  * SLA personnalisé
  * Astreinte incluse

FRAIS DE DÉPLACEMENT:
- Strasbourg et environs (< 10km): Gratuit
- 10-30 km: 0,50€/km
- > 30 km: Sur devis

CONDITIONS DE PAIEMENT:
- Paiement à 30 jours
- Escompte 2% si paiement sous 10 jours
- Pénalités de retard: 3x taux légal

GARANTIES:
- Matériel neuf: Garantie constructeur + 1 an
- Main d'œuvre: Garantie 3 mois
- Satisfaction: Remboursement si non satisfait sous 30 jours
"""

# Load data into vector database
def load_document(text, doc_type, doc_id):
    """Load a document into the vector database"""
    try:
        vector = encoder.encode(text)
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=doc_id,
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
        print(f"❌ Error loading {doc_type}: {str(e)}")
        return False

# Load all documents
print("\nLoading documents...")
load_document(company_info, "company_information", str(uuid.uuid4()))
load_document(services_info, "services_catalog", str(uuid.uuid4()))
load_document(pricing_info, "pricing_and_terms", str(uuid.uuid4()))

# 4. Load some real file examples from Google Drive
drive_path = Path(os.getenv('GOOGLE_DRIVE_PATH', '/Users/mikail/Library/CloudStorage/GoogleDrive-mikail@netzinformatique.fr/Drive\'ım'))

if drive_path.exists():
    print(f"\nScanning Google Drive: {drive_path}")
    
    # Look for important documents
    important_folders = ['ADMINISTRATIF', 'COMPTABILITE', 'CLIENTS', 'PROCEDURES']
    loaded_files = 0
    max_files = 5
    
    for folder in important_folders:
        if loaded_files >= max_files:
            break
            
        folder_path = drive_path / folder
        if folder_path.exists():
            print(f"📁 Checking folder: {folder}")
            
            # Find text files
            for file_path in folder_path.glob('*.txt'):
                if loaded_files >= max_files:
                    break
                    
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if len(content) > 100:  # Skip empty files
                        doc_id = str(uuid.uuid4())
                        load_document(
                            content[:2000],  # First 2000 chars
                            f"google_drive_{folder.lower()}",
                            doc_id
                        )
                        loaded_files += 1
                except Exception as e:
                    print(f"   ⚠️  Could not read {file_path.name}: {e}")

print(f"\n✅ Loaded {loaded_files} files from Google Drive")

# Summary
print("\n" + "="*50)
print("✅ Real company data has been loaded!")
print("\nYou can now ask questions like:")
print("- Quels sont nos tarifs de maintenance ?")
print("- Quelle est l'adresse de NETZ Informatique ?")
print("- Quels services proposons-nous ?")
print("- Quel est le numéro SIRET ?")
print("- Quelles sont nos certifications ?")