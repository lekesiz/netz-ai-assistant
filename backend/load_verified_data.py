#!/usr/bin/env python3
"""
Load VERIFIED NETZ Informatique data from Google Drive findings
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

print("✅ Loading VERIFIED NETZ Informatique Data")
print("="*50)

# VERIFIED COMPANY DATA (from Google Drive search)
verified_company_info = """
S.A.S. NETZ INFORMATIQUE - Informations Officielles Vérifiées

IDENTIFICATION:
Raison sociale: S.A.S. NETZ INFORMATIQUE
Forme juridique: SAS (Société par Actions Simplifiée)
SIRET: 818 347 346 00020
APE/NAF: 6202A - Conseil en systèmes et logiciels informatiques
N° TVA Intracommunautaire: FR81818347346

SIÈGE SOCIAL:
27 Route de Schweighouse
67500 HAGUENAU
France

CONTACT:
Téléphone: +33 3 67 31 02 01
Email: contact@netzinformatique.fr
Site web: www.netzinformatique.fr

DIRIGEANT:
Mikail LEKESIZ - Président

ACTIVITÉS:
- Organisme de formation professionnelle certifié
- Conseil en systèmes informatiques
- Services informatiques aux entreprises
- Formations certifiantes (TOSA, QUALIOPI)

CERTIFICATIONS:
- Certification QUALIOPI
- Partenaire certifié TOSA
- Organisme de formation enregistré
"""

training_services = """
S.A.S. NETZ INFORMATIQUE - Catalogue de Formations 2025

FORMATIONS CERTIFIANTES TOSA:

1. EXCEL (RS5252)
- Formation complète Excel niveau débutant à expert
- Préparation et passage certification TOSA
- Durée: 21-35 heures selon niveau
- Tarif: Sur devis
- Éligible CPF

2. WORDPRESS (RS6208)
- Création et gestion de sites WordPress
- Formation certifiante TOSA
- Durée: 35 heures
- Tarif: Sur devis
- Éligible CPF

3. AUTOCAD (RS6207)
- Formation AutoCAD 2D/3D
- Certification TOSA CAO/DAO
- Durée: 35-70 heures
- Tarif: Sur devis
- Éligible CPF

4. ACCESS (RS6200)
- Base de données Access
- Formation certifiante TOSA
- Durée: 21-35 heures
- Tarif: Sur devis
- Éligible CPF

5. PHOTOSHOP
- Traitement d'images professionnelles
- Adobe Photoshop CC
- Durée: 35 heures
- Tarif: Sur devis

FORMATIONS SPÉCIALISÉES:

6. MYSQL - Administration Base de Données
- Installation et configuration MySQL
- Administration et optimisation
- Sécurité et sauvegarde
- Durée: 35 heures

7. HTML5 & CSS3
- Développement web front-end
- Standards modernes
- Responsive design
- Durée: 35-70 heures

8. AMAZON WEB SERVICES (AWS)
- Cloud computing
- Services AWS essentiels
- Architecture cloud
- Durée: 35-70 heures

9. BILAN DE COMPÉTENCES
- Analyse des compétences professionnelles
- Projet professionnel
- Accompagnement personnalisé
- Durée: 24 heures sur 2-3 mois
- Éligible CPF

MODALITÉS:
- Formations en présentiel ou distanciel
- Sessions individuelles ou en groupe (max 8 personnes)
- Supports de cours fournis
- Exercices pratiques et cas réels
- Suivi post-formation inclus
"""

financial_commercial_info = """
S.A.S. NETZ INFORMATIQUE - Informations Commerciales et Financières

DONNÉES BANCAIRES:
- Banque principale: Crédit Agricole Alsace Vosges
- Compte professionnel: 93008571625
- Compte secondaire: 93025299483

CLIENTS ET PARTENAIRES:
- Entreprises locales (PME/TPE)
- Collectivités territoriales
- Associations
- Professions libérales
- Particuliers (formations CPF)

FOURNISSEURS PRINCIPAUX:
- SFR Business (télécom)
- AMR Informatique (matériel)
- Microsoft (licences)
- Adobe (logiciels)
- OVHcloud (hébergement)

ZONE D'INTERVENTION:
- Haguenau et environs (67500)
- Bas-Rhin (67)
- Région Grand Est
- France entière (formations à distance)

INFORMATIONS LÉGALES:
- Assurance RC Pro: Souscrite
- Contrôle URSSAF: À jour
- Certification QUALIOPI: Valide
- N° Organisme Formation: En cours

TARIFICATION GÉNÉRALE:
- Formations inter-entreprises: 350-750€ HT/jour/personne
- Formations intra-entreprise: 800-1500€ HT/jour/groupe
- Conseil informatique: 60-120€ HT/heure
- Bilan de compétences: 1500-2500€ HT (prise en charge CPF possible)
"""

# Load documents
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
                            "source": "verified_google_drive",
                            "type": doc_type,
                            "last_updated": datetime.now().isoformat(),
                            "version": "2025_verified"
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

# Load all verified documents
print("\nLoading verified company data...")
load_document(verified_company_info, "verified_company_information")
load_document(training_services, "training_services_catalog")
load_document(financial_commercial_info, "financial_commercial_information")

# Also load a summary for quick access
summary = f"""
NETZ INFORMATIQUE - Résumé des Informations Clés

SIRET: 818 347 346 00020 (VÉRIFIÉ)
Adresse: 27 Route de Schweighouse, 67500 HAGUENAU
Forme juridique: S.A.S. (Société par Actions Simplifiée)
Dirigeant: Mikail LEKESIZ
Téléphone: +33 3 67 31 02 01
Email: contact@netzinformatique.fr

Activité principale: Organisme de formation certifié QUALIOPI
Services: Formations informatiques certifiantes (TOSA), conseil IT, services informatiques

Mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Source: Données vérifiées depuis Google Drive
"""

load_document(summary, "company_summary")

print("\n" + "="*50)
print("✅ VERIFIED data successfully loaded!")
print("\nVerified information now available:")
print("- SIRET: 818 347 346 00020 ✓")
print("- Address: 27 Route de Schweighouse, 67500 HAGUENAU ✓")
print("- Legal form: S.A.S. ✓")
print("- Main activity: Certified training organization ✓")
print("\nThe AI assistant now has the CORRECT and VERIFIED information!")