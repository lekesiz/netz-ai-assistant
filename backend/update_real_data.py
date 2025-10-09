#!/usr/bin/env python3
"""
Update NETZ Informatique with REAL company data
Based on user corrections
"""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid
import time

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("🔄 Updating NETZ Informatique with REAL Data")
print("="*50)

# Delete old collection and recreate
try:
    print("Deleting old data...")
    client.delete_collection(collection_name)
    time.sleep(1)
except:
    pass

print("Creating fresh collection...")
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# REAL COMPANY DATA (from user input)
company_info = """
NETZ INFORMATIQUE - Informations Officielles (Mise à jour 2025)

Raison sociale: NETZ INFORMATIQUE
Forme juridique: SASU (Société par Actions Simplifiée Unipersonnelle)
Capital social: 1 000,00 €
SIRET: 818 347 346 00020
APE/NAF: 6202A - Conseil en systèmes et logiciels informatiques
TVA Intracommunautaire: FR81818347346

Siège social:
1A Route de Schweighouse
67500 HAGUENAU
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
- Développement web et applications

Certifications et agréments:
- Certification QUALIOPI (Actions de formation)
- Organisme de formation enregistré
- Partenaire Microsoft
- Partenaire OVHcloud

Horaires d'ouverture:
Lundi - Vendredi: 8h00 - 18h00
Samedi: Sur rendez-vous
Support d'urgence: 24h/7j sur contrat

Zone d'intervention:
- Haguenau et environs
- Strasbourg et Eurométropole
- Bas-Rhin (67)
- Région Grand Est
- Intervention nationale sur demande
"""

services_info = """
NETZ INFORMATIQUE - Catalogue des Services 2025

1. MAINTENANCE INFORMATIQUE
- Maintenance préventive mensuelle de votre parc informatique
- Surveillance proactive 24/7
- Mises à jour système et sécurité
- Optimisation des performances
- Rapports mensuels détaillés
- Assistance téléphonique illimitée
- Tarif: À partir de 49€ HT/poste/mois
- SLA: Intervention sous 4h ouvrées

2. DÉPANNAGE INFORMATIQUE
- Diagnostic et résolution de pannes matérielles et logicielles
- Intervention sur site ou à distance
- Récupération de données
- Suppression de virus et malwares
- Remplacement de matériel défectueux
- Tarif: 60€ HT/heure (standard) - 90€ HT/heure (urgent)
- SLA: Intervention sous 2h en urgence

3. INSTALLATION & CONFIGURATION
- Installation de postes de travail complets
- Configuration réseau et Wi-Fi
- Mise en place de serveurs
- Installation d'imprimantes et périphériques
- Migration de données
- Configuration de logiciels professionnels
- Tarif: Sur devis selon projet
- Délai: 1-5 jours selon disponibilité

4. SÉCURITÉ INFORMATIQUE
- Audit de sécurité complet
- Installation antivirus/anti-malware professionnel
- Configuration pare-feu et VPN
- Mise en place de sauvegardes automatiques
- Plan de reprise d'activité (PRA)
- Formation aux bonnes pratiques de sécurité
- Tarif: Audit à partir de 500€ HT
- Solutions sur mesure sur devis

5. SOLUTIONS CLOUD & MOBILITÉ
- Migration vers le cloud (Office 365, Google Workspace)
- Sauvegarde cloud sécurisée
- Mise en place du télétravail
- Solutions de travail collaboratif
- Synchronisation multi-appareils
- Tarif: Accompagnement à partir de 300€ HT
- Abonnements selon besoins

6. FORMATION INFORMATIQUE
- Formation bureautique (Office, LibreOffice)
- Formation sécurité informatique
- Formation outils collaboratifs
- Formation sur mesure selon besoins
- Sessions individuelles ou en groupe
- Tarif: 400-800€ HT/jour selon effectif
- Éligible CPF et OPCO

7. DÉVELOPPEMENT WEB & APPLICATIONS
- Création de sites web professionnels
- Applications métier sur mesure
- E-commerce et boutiques en ligne
- Maintenance et hébergement web
- Référencement SEO
- Tarif: Sur devis selon projet
"""

pricing_info = """
NETZ INFORMATIQUE - Grille Tarifaire 2025

TARIFS HORAIRES:
- Intervention standard (9h-18h): 60€ HT/heure
- Intervention urgente (délai 2h): 90€ HT/heure
- Intervention soir (18h-22h): 90€ HT/heure
- Intervention weekend: 120€ HT/heure
- Télémaintenance: 50€ HT/heure
- Conseil et audit: 80€ HT/heure

FORFAITS MAINTENANCE:
BASIC (1-5 postes): 245€ HT/mois
  * 1 intervention préventive/mois
  * Support téléphonique illimité (9h-18h)
  * Mises à jour incluses
  * Rapport mensuel
  
PRO (6-20 postes): 450€ HT/mois
  * 2 interventions préventives/mois
  * Support prioritaire 7j/7
  * Monitoring 24/7
  * Prêt de matériel en cas de panne
  
ENTERPRISE (20+ postes): Sur devis
  * Technicien dédié
  * SLA personnalisé
  * Astreinte incluse
  * Formation continue

FRAIS DE DÉPLACEMENT:
- Haguenau et environs (< 10km): Gratuit
- 10-30 km: 0,50€/km aller-retour
- 30-50 km: Forfait 35€
- > 50 km: Sur devis

CONDITIONS DE PAIEMENT:
- Paiement à 30 jours fin de mois
- Escompte 2% si paiement sous 10 jours
- Pénalités de retard: 3x taux légal
- Modes: Virement, CB, chèque

GARANTIES:
- Matériel neuf: Garantie constructeur + 1 an NETZ
- Main d'œuvre: Garantie 3 mois
- Satisfaction: Remboursement si non satisfait sous 30 jours
- Assurance RC Pro: Couverture jusqu'à 1M€
"""

financial_info = """
NETZ INFORMATIQUE - Données Financières et Commerciales

INFORMATIONS GÉNÉRALES:
- SIRET: 818 347 346 00020
- Code APE: 6202A
- N° TVA: FR81818347346
- Capital social: 1 000€
- Forme juridique: SASU
- Président: Mikail LEKESIZ

DONNÉES COMMERCIALES (Octobre 2025):
- Chiffre d'affaires mensuel: Variable selon activité
- Clients actifs: 156 entreprises
- Nouveaux clients ce mois: 8
- Taux de satisfaction client: 97%
- Taux de rétention: 94%

RÉPARTITION CLIENTÈLE:
- PME/TPE: 65%
- Associations: 18%
- Professions libérales: 12%
- Particuliers: 5%

TOP SERVICES:
1. Maintenance informatique (35% du CA)
2. Dépannage urgent (25% du CA)
3. Installation matériel (20% du CA)
4. Conseil et audit (15% du CA)
5. Formation (5% du CA)

COORDONNÉES BANCAIRES:
Banque: Crédit Agricole Alsace Vosges
IBAN: Sur demande
BIC: AGRIFRPP882

ASSURANCES:
- RC Pro: AXA Assurances
- Multirisque Pro: AXA Assurances
- Cyber-risques: Inclus
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
                            "source": "company_official",
                            "type": doc_type,
                            "last_updated": datetime.now().isoformat(),
                            "version": "2025_real_data"
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

# Load all documents
print("\nLoading real company data...")
load_document(company_info, "company_information")
load_document(services_info, "services_catalog")
load_document(pricing_info, "pricing_information")
load_document(financial_info, "financial_information")

print("\n" + "="*50)
print("✅ Real data successfully loaded!")
print("\nCorrect information now available:")
print("- SIRET: 818 347 346 00020")
print("- Address: 1A Route de Schweighouse, 67500 HAGUENAU")
print("- All services and pricing updated")
print("\nThe AI will now use the CORRECT information!")