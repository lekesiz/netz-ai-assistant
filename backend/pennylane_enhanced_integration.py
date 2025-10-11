"""
Enhanced PennyLane Integration for NETZ AI
Adds missing features from PennyLane to AI training
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass
from pathlib import Path
import logging

from lightweight_rag import LightweightRAG
from simple_config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PennyLaneFeature:
    """Represents a PennyLane feature to integrate"""
    name: str
    description: str
    api_endpoint: str
    training_data: List[Dict[str, str]]
    importance: int  # 1-5, 5 being most important


class PennyLaneEnhancedIntegration:
    """Enhanced integration to sync ALL PennyLane features with AI"""
    
    def __init__(self):
        self.api_key = settings.pennylane_api_key or "eyJhbGciOiJIUzI1NiJ9.eyJjb21wYW55X3V1aWQiOiIyMjA1MjA1My05OWI2LTRkMGEtODA2NC1hYWE0MTg5MTAzNTEiLCJzY29wZSI6ImFwaV9jbGllbnRfYWNjZXNzIiwiaWF0IjoxNzU2ODk4ODU4LCJleHAiOjQzODA0OTg4NTh9.fMBrHZjJoZSFOzMQxHgQjNNBBvR19vdvvEJCN0YJ_Rk"
        self.base_url = "https://app.pennylane.com/api/external/v1"
        self.rag = LightweightRAG()
        self.missing_features = []
        
    async def analyze_missing_features(self) -> List[PennyLaneFeature]:
        """Analyze what PennyLane features are missing in AI"""
        
        # Define all PennyLane features that should be in AI
        all_features = [
            PennyLaneFeature(
                name="Invoice Management",
                description="Complete invoice creation, editing, payment tracking",
                api_endpoint="/customer_invoices",
                training_data=[
                    {"q": "Comment créer une facture dans PennyLane?", "a": "Pour créer une facture: 1) Allez dans Ventes > Factures, 2) Cliquez sur 'Nouvelle facture', 3) Sélectionnez le client, 4) Ajoutez les produits/services, 5) Définissez les conditions de paiement, 6) Envoyez ou téléchargez la facture."},
                    {"q": "Comment suivre les paiements de factures?", "a": "Dans PennyLane, allez dans Ventes > Factures. Les statuts sont: 'En attente' (non payée), 'En retard' (échéance dépassée), 'Payée' (règlement reçu). Vous pouvez filtrer par statut et envoyer des relances automatiques."},
                    {"q": "Qu'est-ce qu'un avoir dans PennyLane?", "a": "Un avoir est une facture négative pour annuler ou modifier une facture existante. Créez-le depuis la facture originale via 'Créer un avoir'. Il sera automatiquement lié à la facture d'origine."},
                ],
                importance=5
            ),
            PennyLaneFeature(
                name="Quote Management",
                description="Devis creation, conversion to invoices, tracking",
                api_endpoint="/quotes",
                training_data=[
                    {"q": "Comment faire un devis dans PennyLane?", "a": "Pour créer un devis: 1) Ventes > Devis, 2) 'Nouveau devis', 3) Remplissez les informations client, 4) Ajoutez les lignes de produits/services, 5) Définissez la durée de validité, 6) Envoyez par email ou téléchargez le PDF."},
                    {"q": "Comment transformer un devis en facture?", "a": "Ouvrez le devis accepté, cliquez sur 'Transformer en facture'. Toutes les informations seront reprises automatiquement. Vous pouvez modifier si nécessaire avant de finaliser la facture."},
                    {"q": "Quelle est la durée de validité d'un devis?", "a": "Par défaut 30 jours dans PennyLane, mais personnalisable. Après expiration, le devis passe en statut 'Expiré'. Vous pouvez le dupliquer pour en créer un nouveau avec une nouvelle date."},
                ],
                importance=5
            ),
            PennyLaneFeature(
                name="Customer Management",
                description="Customer database, contact info, history",
                api_endpoint="/customers",
                training_data=[
                    {"q": "Comment ajouter un nouveau client?", "a": "Allez dans Ventes > Clients > 'Nouveau client'. Remplissez: nom/raison sociale, adresse, email, téléphone, conditions de paiement, numéro SIRET/TVA. Vous pouvez aussi importer depuis un fichier CSV."},
                    {"q": "Comment voir l'historique d'un client?", "a": "Dans la fiche client, vous voyez: toutes les factures, devis, avoirs, paiements reçus, documents échangés. Un graphique montre l'évolution du CA avec ce client."},
                    {"q": "Comment gérer les conditions de paiement client?", "a": "Dans la fiche client, définissez: comptant, 30 jours, 60 jours, ou personnalisé. Ces conditions s'appliquent automatiquement aux nouvelles factures. Modifiables au cas par cas."},
                ],
                importance=5
            ),
            PennyLaneFeature(
                name="Product Catalog",
                description="Product/service management, pricing, inventory",
                api_endpoint="/products",
                training_data=[
                    {"q": "Comment créer un produit ou service?", "a": "Configuration > Produits > 'Nouveau produit'. Définissez: nom, description, prix HT, taux de TVA, unité de mesure, catégorie comptable. Pour un service, décochez 'Gérer le stock'."},
                    {"q": "Comment gérer les tarifs et remises?", "a": "Dans la fiche produit, définissez le prix de base. Lors de la facturation, vous pouvez appliquer des remises en % ou montant fixe. Créez des grilles tarifaires pour des remises volume."},
                    {"q": "Comment suivre le stock?", "a": "Si la gestion de stock est activée, PennyLane suit automatiquement les entrées/sorties. Définissez un seuil d'alerte. Les mouvements sont visibles dans l'historique du produit."},
                ],
                importance=4
            ),
            PennyLaneFeature(
                name="Bank Synchronization",
                description="Bank account sync, transaction matching",
                api_endpoint="/bank_accounts",
                training_data=[
                    {"q": "Comment synchroniser mon compte bancaire?", "a": "Trésorerie > Comptes bancaires > 'Connecter un compte'. Choisissez votre banque, suivez l'authentification sécurisée. La synchronisation est automatique quotidienne."},
                    {"q": "Comment rapprocher les transactions?", "a": "Dans Trésorerie > Rapprochement, PennyLane propose des correspondances automatiques entre transactions bancaires et factures. Validez ou modifiez manuellement."},
                    {"q": "Que faire si la synchro bancaire ne fonctionne plus?", "a": "Vérifiez la connexion dans Paramètres > Banques. Reconnectez-vous si nécessaire. Causes fréquentes: changement de mot de passe bancaire, mise à jour sécurité banque."},
                ],
                importance=4
            ),
            PennyLaneFeature(
                name="Expense Management",
                description="Expense tracking, receipts, reimbursements",
                api_endpoint="/supplier_invoices",
                training_data=[
                    {"q": "Comment enregistrer une dépense?", "a": "Achats > Dépenses > 'Nouvelle dépense'. Prenez en photo le reçu ou uploadez le PDF. Remplissez: montant, TVA, catégorie, fournisseur. L'OCR extrait automatiquement les infos."},
                    {"q": "Comment gérer les notes de frais?", "a": "Les collaborateurs uploadent leurs reçus via l'app mobile. Validez dans Achats > Notes de frais. Exportez pour remboursement. Intégration automatique en comptabilité."},
                    {"q": "Comment catégoriser les dépenses?", "a": "PennyLane propose des catégories comptables standards. Personnalisez dans Configuration > Plan comptable. L'IA apprend et suggère la bonne catégorie automatiquement."},
                ],
                importance=4
            ),
            PennyLaneFeature(
                name="VAT Management",
                description="VAT calculation, declaration, reporting",
                api_endpoint="/vat",
                training_data=[
                    {"q": "Comment préparer ma déclaration de TVA?", "a": "Comptabilité > TVA affiche le montant à déclarer. PennyLane calcule automatiquement TVA collectée - TVA déductible. Exportez le détail pour votre déclaration."},
                    {"q": "Quels sont les taux de TVA en France?", "a": "Taux normal: 20%, Taux intermédiaire: 10%, Taux réduit: 5.5%, Taux super-réduit: 2.1%. PennyLane applique automatiquement selon le type de produit/service."},
                    {"q": "Comment gérer la TVA intracommunautaire?", "a": "Pour les ventes UE, renseignez le numéro de TVA du client. PennyLane applique l'exonération automatiquement. Générez la DEB depuis Comptabilité > Déclarations."},
                ],
                importance=5
            ),
            PennyLaneFeature(
                name="Reporting & Analytics",
                description="Financial reports, dashboards, KPIs",
                api_endpoint="/reports",
                training_data=[
                    {"q": "Quels rapports sont disponibles?", "a": "Tableau de bord: CA, dépenses, résultat. Rapports détaillés: P&L, bilan, grand livre, balance, journaux. Export en PDF/Excel. Personnalisez les périodes."},
                    {"q": "Comment suivre ma rentabilité?", "a": "Le tableau de bord affiche: marge brute, charges, résultat net. Analysez par client, produit, période. Graphiques d'évolution et comparaisons N-1."},
                    {"q": "Comment exporter mes données comptables?", "a": "Comptabilité > Exports permet FEC, grand livre, balance. Formats: PDF, Excel, CSV. Utile pour votre expert-comptable ou analyses personnalisées."},
                ],
                importance=3
            ),
            PennyLaneFeature(
                name="Document Management",
                description="Document storage, sharing, electronic signatures",
                api_endpoint="/documents",
                training_data=[
                    {"q": "Comment stocker mes documents?", "a": "Glissez-déposez dans Documents ou utilisez l'app mobile. Organisation automatique par type, date, client. Recherche par mots-clés dans le contenu."},
                    {"q": "Comment partager des documents?", "a": "Depuis un document, cliquez 'Partager' pour générer un lien sécurisé. Définissez une expiration. Pour les factures, utilisez le lien public client."},
                    {"q": "La signature électronique est-elle disponible?", "a": "Oui, pour devis et contrats. Activez dans le document, envoyez au client. Signature légalement valide avec horodatage et certificat."},
                ],
                importance=3
            ),
            PennyLaneFeature(
                name="API Integration",
                description="API usage, webhooks, third-party integrations",
                api_endpoint="/api_info",
                training_data=[
                    {"q": "Comment utiliser l'API PennyLane?", "a": "Obtenez votre clé API dans Paramètres > API. Documentation sur developers.pennylane.com. Endpoints pour factures, clients, produits. Limite: 1000 req/heure."},
                    {"q": "Quelles intégrations sont disponibles?", "a": "Natives: Stripe, PayPal, WooCommerce, Shopify, Prestashop. Via Zapier: 1000+ apps. Webhooks pour événements temps réel (nouvelle facture, paiement)."},
                    {"q": "Comment automatiser avec PennyLane?", "a": "Utilisez: règles d'automatisation (factures récurrentes), API pour intégrations custom, webhooks pour déclencher des actions, exports programmés."},
                ],
                importance=3
            )
        ]
        
        # Check which features are already in RAG
        for feature in all_features:
            # Test if AI knows about this feature
            test_query = f"PennyLane {feature.name}"
            results = await self.rag.search(test_query, top_k=5)
            
            if not results or len(results) < 3:
                self.missing_features.append(feature)
                logger.info(f"Missing feature detected: {feature.name}")
            else:
                logger.info(f"Feature already present: {feature.name}")
        
        return self.missing_features
    
    async def fetch_live_data(self, endpoint: str) -> Optional[Dict]:
        """Fetch live data from PennyLane API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"API error {response.status_code}: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Failed to fetch from {endpoint}: {str(e)}")
                return None
    
    async def train_on_missing_features(self):
        """Train AI on missing PennyLane features"""
        logger.info("Starting training on missing PennyLane features...")
        
        # First analyze what's missing
        missing = await self.analyze_missing_features()
        logger.info(f"Found {len(missing)} missing features")
        
        trained_count = 0
        
        for feature in missing:
            logger.info(f"Training on feature: {feature.name}")
            
            # Add training data for this feature
            for qa_pair in feature.training_data:
                metadata = {
                    "source": "pennylane_training",
                    "feature": feature.name,
                    "importance": feature.importance,
                    "type": "faq",
                    "language": "fr",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Create comprehensive content
                content = f"Question: {qa_pair['q']}\nRéponse: {qa_pair['a']}\nFonctionnalité: {feature.name}"
                
                # Add to RAG
                await self.rag.add_document(
                    content=content,
                    metadata=metadata
                )
                
                trained_count += 1
            
            # Also fetch and add live data if available
            if feature.api_endpoint:
                live_data = await self.fetch_live_data(feature.api_endpoint)
                if live_data:
                    # Create training content from live data
                    self._process_live_data(live_data, feature)
        
        logger.info(f"Training completed. Added {trained_count} training examples.")
        return trained_count
    
    def _process_live_data(self, data: Dict, feature: PennyLaneFeature):
        """Process live API data for training"""
        # Extract relevant information based on feature type
        if feature.name == "Invoice Management" and "invoices" in data:
            for invoice in data.get("invoices", [])[:5]:  # Sample 5 invoices
                content = self._create_invoice_training_content(invoice)
                metadata = {
                    "source": "pennylane_live",
                    "feature": feature.name,
                    "type": "example",
                    "timestamp": datetime.utcnow().isoformat()
                }
                asyncio.create_task(self.rag.add_document(content, metadata))
    
    def _create_invoice_training_content(self, invoice: Dict) -> str:
        """Create training content from invoice data"""
        return f"""
        Exemple de facture PennyLane:
        - Numéro: {invoice.get('invoice_number', 'N/A')}
        - Client: {invoice.get('customer', {}).get('name', 'N/A')}
        - Montant: {invoice.get('amount', '0')} {invoice.get('currency', 'EUR')}
        - Statut: {invoice.get('status', 'unknown')}
        - Date: {invoice.get('date', 'N/A')}
        - Échéance: {invoice.get('deadline', 'N/A')}
        
        Informations importantes:
        - Les factures peuvent avoir les statuts: draft (brouillon), sent (envoyée), paid (payée), late (en retard)
        - Le numéro de facture suit le format configuré dans les paramètres
        - Les conditions de paiement sont définies par client
        """
    
    async def create_comprehensive_training_set(self):
        """Create a comprehensive training dataset for all PennyLane features"""
        training_set = []
        
        # Add general PennyLane information
        general_info = [
            {
                "question": "Qu'est-ce que PennyLane?",
                "answer": "PennyLane est une solution de comptabilité en ligne complète pour TPE/PME. Elle permet de gérer facturation, dépenses, trésorerie, déclarations, et collaborer avec votre expert-comptable en temps réel.",
                "category": "general"
            },
            {
                "question": "Comment se connecter à PennyLane?",
                "answer": "Connectez-vous sur app.pennylane.com avec votre email et mot de passe. Activez l'authentification à deux facteurs pour plus de sécurité. L'app mobile est disponible sur iOS/Android.",
                "category": "general"
            },
            {
                "question": "Quel est le prix de PennyLane?",
                "answer": "PennyLane propose plusieurs forfaits: Starter (34€/mois), Standard (69€/mois), Premium (149€/mois). Essai gratuit 30 jours. Tarifs dégressifs pour plusieurs entreprises.",
                "category": "pricing"
            },
            {
                "question": "PennyLane remplace-t-il mon expert-comptable?",
                "answer": "Non, PennyLane facilite la collaboration avec votre expert-comptable. Il a un accès dédié pour valider, corriger et établir vos comptes annuels. L'outil automatise la saisie, pas l'expertise.",
                "category": "general"
            }
        ]
        
        for info in general_info:
            training_set.append({
                "content": f"Q: {info['question']}\nR: {info['answer']}",
                "metadata": {
                    "source": "pennylane_kb",
                    "category": info['category'],
                    "type": "faq",
                    "language": "fr"
                }
            })
        
        # Add all missing features training data
        for feature in await self.analyze_missing_features():
            for qa in feature.training_data:
                training_set.append({
                    "content": f"Q: {qa['q']}\nR: {qa['a']}",
                    "metadata": {
                        "source": "pennylane_features",
                        "feature": feature.name,
                        "importance": feature.importance,
                        "type": "feature_training"
                    }
                })
        
        # Save training set
        output_file = Path("pennylane_complete_training_set.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(training_set, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Created training set with {len(training_set)} examples")
        return training_set
    
    def generate_integration_report(self) -> Dict:
        """Generate report on PennyLane integration completeness"""
        total_features = 10  # Total PennyLane features we identified
        integrated_features = total_features - len(self.missing_features)
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "integration_status": {
                "total_features": total_features,
                "integrated_features": integrated_features,
                "missing_features": len(self.missing_features),
                "completion_percentage": (integrated_features / total_features) * 100
            },
            "missing_features_detail": [
                {
                    "name": f.name,
                    "description": f.description,
                    "importance": f.importance,
                    "training_examples": len(f.training_data)
                }
                for f in self.missing_features
            ],
            "recommendations": [
                "Complete training on high-importance missing features first",
                "Set up regular sync to keep data current",
                "Add webhook integration for real-time updates",
                "Create specialized responses for common PennyLane queries"
            ]
        }
        
        return report


async def enhance_pennylane_integration():
    """Main function to enhance PennyLane integration"""
    integrator = PennyLaneEnhancedIntegration()
    
    # Analyze and train on missing features
    await integrator.train_on_missing_features()
    
    # Create comprehensive training set
    training_set = await integrator.create_comprehensive_training_set()
    
    # Generate report
    report = integrator.generate_integration_report()
    
    # Save report
    with open("pennylane_integration_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    logger.info("PennyLane integration enhancement completed")
    logger.info(f"Integration completeness: {report['integration_status']['completion_percentage']:.1f}%")
    
    return report


if __name__ == "__main__":
    asyncio.run(enhance_pennylane_integration())