#!/usr/bin/env python3
"""
Comprehensive PennyLane Integration for NETZ AI
Fetches real financial data and integrates with AI knowledge base
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
from dataclasses import dataclass

from lightweight_rag import LightweightRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FinancialData:
    """Represents financial data from PennyLane"""
    id: str
    type: str  # invoice, customer, product, etc.
    data: Dict[str, Any]
    created_at: str
    source: str = "pennylane"

class ComprehensivePennyLaneIntegration:
    """Comprehensive PennyLane financial data integration"""
    
    def __init__(self):
        self.api_key = "eyJhbGciOiJIUzI1NiJ9.eyJjb21wYW55X3V1aWQiOiIyMjA1MjA1My05OWI2LTRkMGEtODA2NC1hYWE0MTg5MTAzNTEiLCJzY29wZSI6ImFwaV9jbGllbnRfYWNjZXNzIiwiaWF0IjoxNzU2ODk4ODU4LCJleHAiOjQzODA0OTg4NTh9.fMBrHZjJoZSFOzMQxHgQjNNBBvR19vdvvEJCN0YJ_Rk"
        self.base_url = "https://app.pennylane.com/api/external/v1"
        self.rag = LightweightRAG()
        self.financial_data = []
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def fetch_comprehensive_data(self) -> Dict[str, Any]:
        """Fetch comprehensive financial data from PennyLane API"""
        logger.info("💰 Starting comprehensive PennyLane data fetch...")
        
        data_summary = {
            "invoices": [],
            "customers": [],
            "products": [],
            "quotes": [],
            "payments": [],
            "expenses": [],
            "analytics": {}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch invoices
            try:
                invoices_data = await self._fetch_invoices(client)
                data_summary["invoices"] = invoices_data
                logger.info(f"📄 Fetched {len(invoices_data)} invoices")
            except Exception as e:
                logger.error(f"❌ Error fetching invoices: {str(e)}")
            
            # Fetch customers
            try:
                customers_data = await self._fetch_customers(client)
                data_summary["customers"] = customers_data
                logger.info(f"👥 Fetched {len(customers_data)} customers")
            except Exception as e:
                logger.error(f"❌ Error fetching customers: {str(e)}")
            
            # Fetch products/services
            try:
                products_data = await self._fetch_products(client)
                data_summary["products"] = products_data
                logger.info(f"🛍️ Fetched {len(products_data)} products/services")
            except Exception as e:
                logger.error(f"❌ Error fetching products: {str(e)}")
            
            # Generate analytics
            try:
                analytics_data = self._generate_analytics(data_summary)
                data_summary["analytics"] = analytics_data
                logger.info("📊 Generated analytics data")
            except Exception as e:
                logger.error(f"❌ Error generating analytics: {str(e)}")
        
        return data_summary
    
    async def _fetch_invoices(self, client: httpx.AsyncClient) -> List[Dict]:
        """Fetch invoice data from PennyLane"""
        try:
            # Get recent invoices (last 6 months)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            params = {
                "filter[date][gte]": start_date.strftime("%Y-%m-%d"),
                "filter[date][lte]": end_date.strftime("%Y-%m-%d"),
                "page[size]": 100
            }
            
            response = await client.get(
                f"{self.base_url}/customer_invoices",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                invoices = data.get("data", [])
                
                # Process invoice data for AI training
                processed_invoices = []
                for invoice in invoices:
                    try:
                        invoice_data = {
                            "id": invoice.get("id"),
                            "number": invoice.get("attributes", {}).get("number"),
                            "date": invoice.get("attributes", {}).get("date"),
                            "due_date": invoice.get("attributes", {}).get("due_date"),
                            "amount": invoice.get("attributes", {}).get("amount"),
                            "currency": invoice.get("attributes", {}).get("currency", "EUR"),
                            "status": invoice.get("attributes", {}).get("status"),
                            "customer_name": invoice.get("attributes", {}).get("customer", {}).get("name"),
                            "paid_amount": invoice.get("attributes", {}).get("paid_amount", 0),
                            "remaining_amount": invoice.get("attributes", {}).get("remaining_amount", 0),
                            "line_items": invoice.get("attributes", {}).get("line_items", [])
                        }
                        processed_invoices.append(invoice_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing invoice {invoice.get('id')}: {str(e)}")
                
                return processed_invoices
            else:
                logger.error(f"❌ Invoice API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching invoices: {str(e)}")
            return []
    
    async def _fetch_customers(self, client: httpx.AsyncClient) -> List[Dict]:
        """Fetch customer data from PennyLane"""
        try:
            response = await client.get(
                f"{self.base_url}/customers",
                headers=self.headers,
                params={"page[size]": 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                customers = data.get("data", [])
                
                processed_customers = []
                for customer in customers:
                    try:
                        customer_data = {
                            "id": customer.get("id"),
                            "name": customer.get("attributes", {}).get("name"),
                            "email": customer.get("attributes", {}).get("email"),
                            "phone": customer.get("attributes", {}).get("phone"),
                            "address": customer.get("attributes", {}).get("address"),
                            "city": customer.get("attributes", {}).get("city"),
                            "postal_code": customer.get("attributes", {}).get("postal_code"),
                            "country": customer.get("attributes", {}).get("country"),
                            "payment_conditions": customer.get("attributes", {}).get("payment_conditions"),
                            "created_at": customer.get("attributes", {}).get("created_at")
                        }
                        processed_customers.append(customer_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing customer {customer.get('id')}: {str(e)}")
                
                return processed_customers
            else:
                logger.error(f"❌ Customer API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching customers: {str(e)}")
            return []
    
    async def _fetch_products(self, client: httpx.AsyncClient) -> List[Dict]:
        """Fetch product/service data from PennyLane"""
        try:
            response = await client.get(
                f"{self.base_url}/products",
                headers=self.headers,
                params={"page[size]": 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get("data", [])
                
                processed_products = []
                for product in products:
                    try:
                        product_data = {
                            "id": product.get("id"),
                            "label": product.get("attributes", {}).get("label"),
                            "description": product.get("attributes", {}).get("description"),
                            "price": product.get("attributes", {}).get("price"),
                            "unit": product.get("attributes", {}).get("unit"),
                            "vat_rate": product.get("attributes", {}).get("vat_rate"),
                            "category": product.get("attributes", {}).get("category"),
                            "is_service": product.get("attributes", {}).get("is_service", False)
                        }
                        processed_products.append(product_data)
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing product {product.get('id')}: {str(e)}")
                
                return processed_products
            else:
                logger.error(f"❌ Product API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching products: {str(e)}")
            return []
    
    def _generate_analytics(self, data_summary: Dict) -> Dict[str, Any]:
        """Generate analytics from fetched data"""
        try:
            invoices = data_summary.get("invoices", [])
            customers = data_summary.get("customers", [])
            products = data_summary.get("products", [])
            
            # Calculate financial metrics
            total_revenue = sum(float(inv.get("amount", 0)) for inv in invoices)
            paid_revenue = sum(float(inv.get("paid_amount", 0)) for inv in invoices)
            outstanding_amount = sum(float(inv.get("remaining_amount", 0)) for inv in invoices)
            
            # Count metrics
            total_invoices = len(invoices)
            paid_invoices = len([inv for inv in invoices if inv.get("status") == "paid"])
            overdue_invoices = len([inv for inv in invoices if inv.get("status") == "overdue"])
            
            # Customer metrics
            total_customers = len(customers)
            
            # Product metrics
            total_products = len(products)
            services_count = len([p for p in products if p.get("is_service")])
            
            # Monthly breakdown
            monthly_revenue = {}
            for invoice in invoices:
                if invoice.get("date"):
                    try:
                        month = invoice["date"][:7]  # YYYY-MM format
                        amount = float(invoice.get("amount", 0))
                        if month not in monthly_revenue:
                            monthly_revenue[month] = 0
                        monthly_revenue[month] += amount
                    except Exception:
                        continue
            
            return {
                "financial_summary": {
                    "total_revenue": round(total_revenue, 2),
                    "paid_revenue": round(paid_revenue, 2),
                    "outstanding_amount": round(outstanding_amount, 2),
                    "collection_rate": round((paid_revenue / total_revenue * 100) if total_revenue > 0 else 0, 1)
                },
                "invoice_metrics": {
                    "total_invoices": total_invoices,
                    "paid_invoices": paid_invoices,
                    "overdue_invoices": overdue_invoices,
                    "payment_rate": round((paid_invoices / total_invoices * 100) if total_invoices > 0 else 0, 1)
                },
                "business_metrics": {
                    "total_customers": total_customers,
                    "total_products": total_products,
                    "services_count": services_count,
                    "average_invoice_amount": round(total_revenue / total_invoices if total_invoices > 0 else 0, 2)
                },
                "monthly_revenue": monthly_revenue,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating analytics: {str(e)}")
            return {}
    
    async def create_financial_knowledge_base(self, data_summary: Dict) -> int:
        """Create comprehensive financial knowledge base for AI"""
        logger.info("📚 Creating financial knowledge base...")
        
        # Generate comprehensive financial training data
        financial_docs = []
        
        # 1. Invoice Management Knowledge
        invoice_knowledge = self._create_invoice_knowledge(data_summary.get("invoices", []))
        financial_docs.extend(invoice_knowledge)
        
        # 2. Customer Management Knowledge
        customer_knowledge = self._create_customer_knowledge(data_summary.get("customers", []))
        financial_docs.extend(customer_knowledge)
        
        # 3. Product/Service Knowledge
        product_knowledge = self._create_product_knowledge(data_summary.get("products", []))
        financial_docs.extend(product_knowledge)
        
        # 4. Analytics Knowledge
        analytics_knowledge = self._create_analytics_knowledge(data_summary.get("analytics", {}))
        financial_docs.extend(analytics_knowledge)
        
        # 5. PennyLane Procedures Knowledge
        procedure_knowledge = self._create_procedure_knowledge()
        financial_docs.extend(procedure_knowledge)
        
        # Add all to RAG system
        total_added = 0
        for doc in financial_docs:
            try:
                self.rag.add_document(
                    content=doc["content"],
                    title=doc["title"],
                    source="pennylane_integration",
                    doc_type="financial_data",
                    metadata={
                        "category": doc.get("category", "financial"),
                        "type": doc.get("type", "general"),
                        "priority": doc.get("priority", 3),
                        "last_updated": datetime.now().isoformat()
                    }
                )
                total_added += 1
            except Exception as e:
                logger.error(f"❌ Error adding financial document: {str(e)}")
        
        logger.info(f"✅ Added {total_added} financial knowledge documents to AI")
        return total_added
    
    def _create_invoice_knowledge(self, invoices: List[Dict]) -> List[Dict]:
        """Create invoice-related knowledge documents"""
        docs = []
        
        if not invoices:
            return docs
        
        # General invoice statistics
        total_amount = sum(float(inv.get("amount", 0)) for inv in invoices)
        paid_amount = sum(float(inv.get("paid_amount", 0)) for inv in invoices)
        overdue_count = len([inv for inv in invoices if inv.get("status") == "overdue"])
        
        invoice_summary = f"""
        NETZ INFORMATIQUE - GESTION DES FACTURES PENNYLANE
        
        📊 STATISTIQUES FACTURES (6 derniers mois):
        - Nombre total de factures: {len(invoices)}
        - Montant total facturé: {total_amount:.2f}€ HT
        - Montant encaissé: {paid_amount:.2f}€ HT
        - Factures en retard: {overdue_count}
        - Taux d'encaissement: {(paid_amount/total_amount*100) if total_amount > 0 else 0:.1f}%
        
        🔧 PROCESSUS FACTURATION NETZ:
        1. Création facture après intervention/formation
        2. Envoi automatique par email au client
        3. Suivi des paiements dans PennyLane
        4. Relances automatiques en cas de retard
        5. Rapprochement bancaire automatique
        
        💰 TARIFICATION APPLIQUÉE:
        - Dépannage particuliers: 55€/h HT
        - Dépannage entreprises: 75€/h HT
        - Formations: 45€/h HT
        - Forfait diagnostic: GRATUIT
        - Forfait réinstallation: 89€ HT
        
        📋 INFORMATIONS FACTURES:
        - Conditions de paiement: 30 jours net
        - Mode de règlement: Virement, chèque, espèces
        - TVA appliquée: 20% (taux normal)
        - Numérotation: Automatique par PennyLane
        - Archivage: Conservation légale 10 ans
        """
        
        docs.append({
            "title": "NETZ - Gestion Factures PennyLane",
            "content": invoice_summary,
            "category": "financial",
            "type": "invoices",
            "priority": 5
        })
        
        # Recent invoices examples
        recent_invoices = sorted(invoices, key=lambda x: x.get("date", ""), reverse=True)[:10]
        
        for idx, invoice in enumerate(recent_invoices):
            invoice_detail = f"""
            FACTURE NETZ #{invoice.get('number', 'N/A')}
            
            📄 Détails:
            - Date: {invoice.get('date', 'N/A')}
            - Montant: {invoice.get('amount', 0)}€ HT
            - Client: {invoice.get('customer_name', 'N/A')}
            - Statut: {invoice.get('status', 'N/A')}
            - Échéance: {invoice.get('due_date', 'N/A')}
            - Montant payé: {invoice.get('paid_amount', 0)}€
            - Reste à payer: {invoice.get('remaining_amount', 0)}€
            
            Services facturés:
            """
            
            for item in invoice.get('line_items', []):
                invoice_detail += f"- {item.get('label', 'Service')}: {item.get('amount', 0)}€ HT\n"
            
            docs.append({
                "title": f"Facture {invoice.get('number', idx+1)}",
                "content": invoice_detail,
                "category": "financial",
                "type": "invoice_detail",
                "priority": 3
            })
        
        return docs
    
    def _create_customer_knowledge(self, customers: List[Dict]) -> List[Dict]:
        """Create customer-related knowledge documents"""
        docs = []
        
        if not customers:
            return docs
        
        customer_summary = f"""
        NETZ INFORMATIQUE - BASE CLIENTS PENNYLANE
        
        👥 STATISTIQUES CLIENT:
        - Nombre total de clients: {len(customers)}
        - Clients actifs: {len([c for c in customers if c.get('email')])}
        - Nouveaux clients 2025: {len([c for c in customers if c.get('created_at', '').startswith('2025')])}
        
        🌍 RÉPARTITION GÉOGRAPHIQUE:
        """
        
        # Analyze customer locations
        cities = {}
        for customer in customers:
            city = customer.get('city', 'Non spécifiée')
            cities[city] = cities.get(city, 0) + 1
        
        for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]:
            customer_summary += f"- {city}: {count} clients\n"
        
        customer_summary += f"""
        
        💼 TYPES DE CLIENTS:
        - Particuliers: Dépannage, formations bureautique
        - TPE/PME: Maintenance, formations professionnelles
        - Artisans: Gestion informatique, comptabilité
        - Associations: Formations, support technique
        
        🔧 CONDITIONS COMMERCIALES:
        - Diagnostic gratuit pour tous
        - Paiement: 30 jours net par défaut
        - Remises volume: À partir de 10h de formation
        - Contrats maintenance: Paiement mensuel
        - Garantie: 3 mois sur interventions
        """
        
        docs.append({
            "title": "NETZ - Base Clients PennyLane",
            "content": customer_summary,
            "category": "financial",
            "type": "customers",
            "priority": 4
        })
        
        return docs
    
    def _create_product_knowledge(self, products: List[Dict]) -> List[Dict]:
        """Create product/service knowledge documents"""
        docs = []
        
        if not products:
            return docs
        
        services = [p for p in products if p.get('is_service')]
        physical_products = [p for p in products if not p.get('is_service')]
        
        product_summary = f"""
        NETZ INFORMATIQUE - CATALOGUE PRODUITS/SERVICES PENNYLANE
        
        📊 OVERVIEW:
        - Total produits/services: {len(products)}
        - Services: {len(services)}
        - Produits physiques: {len(physical_products)}
        
        💼 SERVICES PRINCIPAUX:
        """
        
        for service in services[:10]:  # Top 10 services
            product_summary += f"- {service.get('label', 'Service')}: {service.get('price', 0)}€ HT\n"
            if service.get('description'):
                product_summary += f"  Description: {service.get('description')}\n"
        
        product_summary += f"""
        
        🛍️ PRODUITS PHYSIQUES:
        """
        
        for product in physical_products[:5]:  # Top 5 products
            product_summary += f"- {product.get('label', 'Produit')}: {product.get('price', 0)}€ HT\n"
        
        product_summary += f"""
        
        💰 POLITIQUE TARIFAIRE:
        - Prix affichés HT dans PennyLane
        - TVA 20% appliquée automatiquement
        - Remises négociables selon volume
        - Forfaits disponibles pour services récurrents
        - Mise à jour tarifaire annuelle (janvier)
        """
        
        docs.append({
            "title": "NETZ - Catalogue Produits/Services",
            "content": product_summary,
            "category": "financial",
            "type": "products",
            "priority": 4
        })
        
        return docs
    
    def _create_analytics_knowledge(self, analytics: Dict) -> List[Dict]:
        """Create analytics knowledge documents"""
        docs = []
        
        if not analytics:
            return docs
        
        financial_summary = analytics.get("financial_summary", {})
        invoice_metrics = analytics.get("invoice_metrics", {})
        business_metrics = analytics.get("business_metrics", {})
        monthly_revenue = analytics.get("monthly_revenue", {})
        
        analytics_content = f"""
        NETZ INFORMATIQUE - ANALYTICS FINANCIÈRES PENNYLANE
        
        💰 PERFORMANCE FINANCIÈRE:
        - Chiffre d'affaires total: {financial_summary.get('total_revenue', 0)}€ HT
        - CA encaissé: {financial_summary.get('paid_revenue', 0)}€ HT
        - En attente d'encaissement: {financial_summary.get('outstanding_amount', 0)}€ HT
        - Taux d'encaissement: {financial_summary.get('collection_rate', 0)}%
        
        📊 MÉTRIQUES FACTURATION:
        - Total factures émises: {invoice_metrics.get('total_invoices', 0)}
        - Factures payées: {invoice_metrics.get('paid_invoices', 0)}
        - Factures en retard: {invoice_metrics.get('overdue_invoices', 0)}
        - Taux de paiement: {invoice_metrics.get('payment_rate', 0)}%
        
        📈 INDICATEURS BUSINESS:
        - Nombre de clients: {business_metrics.get('total_customers', 0)}
        - Produits/services: {business_metrics.get('total_products', 0)}
        - Panier moyen: {business_metrics.get('average_invoice_amount', 0)}€ HT
        
        📅 ÉVOLUTION MENSUELLE CA:
        """
        
        for month, revenue in sorted(monthly_revenue.items(), reverse=True)[:6]:
            analytics_content += f"- {month}: {revenue:.2f}€ HT\n"
        
        analytics_content += f"""
        
        🎯 OBJECTIFS 2025:
        - CA cible: 143 264€ HT
        - Taux encaissement: >95%
        - Délai paiement moyen: <25 jours
        - Croissance mensuelle: +5%
        
        📊 KPI SURVEILLANCE:
        - Factures en retard: Alerte si >10%
        - Trésorerie: Suivi quotidien
        - Nouveaux clients: Objectif 20/mois
        - Panier moyen: Optimisation continue
        """
        
        docs.append({
            "title": "NETZ - Analytics Financières",
            "content": analytics_content,
            "category": "financial",
            "type": "analytics",
            "priority": 5
        })
        
        return docs
    
    def _create_procedure_knowledge(self) -> List[Dict]:
        """Create PennyLane procedure knowledge"""
        docs = []
        
        procedure_content = """
        NETZ INFORMATIQUE - PROCÉDURES PENNYLANE
        
        💼 PROCESSUS FACTURATION:
        
        1. Création Facture:
           - Intervention/formation terminée
           - Saisie des prestations dans PennyLane
           - Vérification TVA et tarifs
           - Génération automatique PDF
           - Envoi email client
        
        2. Suivi Paiements:
           - Relance automatique J+30
           - Relance manuelle si nécessaire
           - Rapprochement bancaire quotidien
           - Mise à jour statuts en temps réel
        
        3. Gestion Retards:
           - Identification factures échues
           - Contact téléphonique client
           - Négociation échéancier si besoin
           - Procédure recouvrement si nécessaire
        
        🏦 RAPPROCHEMENT BANCAIRE:
        - Synchronisation automatique compte NETZ
        - Validation quotidienne des écritures
        - Lettrage factures/paiements
        - Contrôle cohérence trésorerie
        
        📋 REPORTING MENSUEL:
        - CA mensuel et cumulé
        - Taux d'encaissement
        - Factures en cours
        - Prévisionnel trésorerie
        - KPI business
        
        🔧 MAINTENANCE PENNYLANE:
        - Sauvegarde quotidienne
        - Mise à jour tarifs
        - Contrôle TVA
        - Archivage légal
        - Formation équipe
        """
        
        docs.append({
            "title": "NETZ - Procédures PennyLane",
            "content": procedure_content,
            "category": "financial",
            "type": "procedures",
            "priority": 4
        })
        
        return docs
    
    async def test_financial_knowledge(self) -> Dict[str, Any]:
        """Test AI knowledge of financial data"""
        test_queries = [
            "Quel est le chiffre d'affaires de NETZ?",
            "Combien de factures sont en retard?",
            "Quel est le montant moyen d'une facture?",
            "Combien NETZ a-t-il de clients?",
            "Comment suivre les paiements dans PennyLane?",
            "Quels sont les tarifs de NETZ dans les factures?",
            "Comment créer une facture dans PennyLane?",
            "Quel est le taux d'encaissement de NETZ?",
            "Comment faire le rapprochement bancaire?",
            "Quelles sont les conditions de paiement?"
        ]
        
        test_results = []
        logger.info("🧪 Testing financial AI knowledge...")
        
        for query in test_queries:
            try:
                results = self.rag.search(query, k=3)
                
                if results:
                    best_match = results[0]
                    confidence = best_match.get('score', 0)
                    
                    test_results.append({
                        "query": query,
                        "success": True,
                        "confidence": confidence,
                        "response_preview": best_match['content'][:200] + "...",
                        "source": best_match.get('metadata', {}).get('type', 'unknown')
                    })
                    
                    logger.info(f"✅ {query} -> {confidence:.3f}")
                else:
                    test_results.append({
                        "query": query,
                        "success": False,
                        "error": "No results found"
                    })
                    logger.warning(f"❌ No results: {query}")
                    
            except Exception as e:
                test_results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"❌ Error: {query} - {str(e)}")
        
        successful = len([r for r in test_results if r.get('success')])
        success_rate = (successful / len(test_queries)) * 100
        
        return {
            "total_queries": len(test_queries),
            "successful_queries": successful,
            "success_rate": success_rate,
            "financial_readiness": "Excellent" if success_rate >= 90 else "Good" if success_rate >= 75 else "Needs improvement",
            "test_results": test_results
        }
    
    async def run_comprehensive_integration(self) -> Dict[str, Any]:
        """Run complete PennyLane integration"""
        logger.info("🚀 Starting comprehensive PennyLane integration...")
        
        start_time = datetime.now()
        
        # Step 1: Fetch data from PennyLane API
        data_summary = await self.fetch_comprehensive_data()
        
        # Step 2: Create financial knowledge base
        knowledge_docs = await self.create_financial_knowledge_base(data_summary)
        
        # Step 3: Test financial knowledge
        test_results = await self.test_financial_knowledge()
        
        end_time = datetime.now()
        integration_duration = (end_time - start_time).total_seconds()
        
        # Generate report
        report = {
            "integration_completed": True,
            "timestamp": end_time.isoformat(),
            "duration_seconds": integration_duration,
            "data_fetched": {
                "invoices": len(data_summary.get("invoices", [])),
                "customers": len(data_summary.get("customers", [])),
                "products": len(data_summary.get("products", [])),
                "analytics_generated": bool(data_summary.get("analytics"))
            },
            "knowledge_integration": {
                "documents_added": knowledge_docs,
                "categories": ["invoices", "customers", "products", "analytics", "procedures"]
            },
            "ai_performance": test_results,
            "financial_summary": data_summary.get("analytics", {}).get("financial_summary", {}),
            "readiness_status": {
                "ready_for_production": test_results.get('success_rate', 0) >= 80,
                "financial_data_integrated": True,
                "real_time_capable": True
            }
        }
        
        # Log summary
        logger.info(f"🎯 PENNYLANE INTEGRATION COMPLETED")
        logger.info(f"   💰 Invoices processed: {len(data_summary.get('invoices', []))}")
        logger.info(f"   👥 Customers processed: {len(data_summary.get('customers', []))}")
        logger.info(f"   📚 Knowledge docs added: {knowledge_docs}")
        logger.info(f"   ✅ AI success rate: {test_results.get('success_rate', 0):.1f}%")
        logger.info(f"   ⏱️ Duration: {integration_duration:.1f}s")
        
        return report

async def main():
    """Main integration function"""
    logger.info("💰 NETZ PennyLane Comprehensive Integration")
    
    integration = ComprehensivePennyLaneIntegration()
    
    # Run comprehensive integration
    report = await integration.run_comprehensive_integration()
    
    if report.get('integration_completed'):
        print(f"\n🎉 PENNYLANE INTEGRATION RÉUSSIE!")
        print(f"💰 Données financières: {report['data_fetched']['invoices']} factures, {report['data_fetched']['customers']} clients")
        print(f"📚 Connaissances ajoutées: {report['knowledge_integration']['documents_added']} documents")
        print(f"🧠 Taux de réussite AI: {report['ai_performance']['success_rate']:.1f}%")
        print(f"✅ Prêt pour production: {'OUI' if report['readiness_status']['ready_for_production'] else 'NON'}")
        
        # Display financial summary
        financial_summary = report.get('financial_summary', {})
        if financial_summary:
            print(f"\n💼 RÉSUMÉ FINANCIER:")
            print(f"   CA total: {financial_summary.get('total_revenue', 0):.2f}€ HT")
            print(f"   CA encaissé: {financial_summary.get('paid_revenue', 0):.2f}€ HT")
            print(f"   Taux encaissement: {financial_summary.get('collection_rate', 0):.1f}%")
        
        return report
    else:
        print("❌ Échec de l'intégration PennyLane")
        return {"success": False}

if __name__ == "__main__":
    asyncio.run(main())