#!/usr/bin/env python3
"""
NETZ Employee Knowledge Interface
Çalışanlar için offline bilgi erişim sistemi
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class EmployeeQuery(BaseModel):
    query: str
    category: Optional[str] = None
    language: Optional[str] = "fr"

class QuickAccessRequest(BaseModel):
    info_type: str  # "pricing", "services", "financials", "contacts"

class EmployeeKnowledgeInterface:
    """Çalışanlar için bilgi arayüzü"""
    
    def __init__(self, learning_system=None):
        self.learning_system = learning_system
        
        # Hızlı erişim bilgileri
        self.quick_access_data = {
            "pricing": {
                "formation": {
                    "individuel": "45€/h",
                    "groupe": "250€/demi-journée", 
                    "cpf_eligible": True,
                    "opco_eligible": True
                },
                "depannage": {
                    "particulier": "55€/h",
                    "entreprise": "75€/h",
                    "diagnostic": "GRATUIT",
                    "garantie": "3 mois"
                },
                "maintenance": {
                    "particulier": "39€/mois",
                    "entreprise": "69€/mois/poste",
                    "support": "24/7 prioritaire"
                }
            },
            "services": {
                "formation": {
                    "excel": {"prix": "45€/h", "duree": "Variable", "certification": "QUALIOPI"},
                    "python": {"prix": "45€/h", "duree": "40h", "certification": "QUALIOPI"},
                    "word": {"prix": "45€/h", "duree": "16h", "certification": "QUALIOPI"},
                    "cybersecurite": {"prix": "45€/h", "duree": "24h", "certification": "QUALIOPI"},
                    "autocad": {"prix": "45€/h", "duree": "32h", "certification": "QUALIOPI"}
                },
                "depannage": {
                    "reparation_pc": "Diagnostic gratuit + réparation",
                    "virus_malware": "Nettoyage complet + protection",
                    "recuperation_donnees": "Analyse + récupération si possible",
                    "installation_logiciels": "Installation + configuration",
                    "mise_a_niveau": "Upgrade hardware/software"
                },
                "maintenance": {
                    "maintenance_preventive": "Nettoyage + optimisation",
                    "mises_a_jour": "Windows + logiciels + antivirus",
                    "sauvegarde": "Configuration + vérification",
                    "support": "Assistance téléphonique prioritaire"
                }
            },
            "contacts": {
                "principal": {
                    "nom": "Mikail LEKESIZ",
                    "telephone": "07 67 74 49 03",
                    "email": "contact@netzinformatique.fr",
                    "whatsapp": "07 67 74 49 03"
                },
                "urgences": {
                    "telephone": "07 67 74 49 03",
                    "email": "urgence@netzinformatique.fr",
                    "disponibilite": "24/7 pour clients maintenance"
                },
                "commercial": {
                    "email": "commercial@netzinformatique.fr",
                    "telephone": "07 67 74 49 03"
                }
            },
            "company": {
                "nom": "NETZ INFORMATIQUE",
                "siret": "818 347 346 00020",
                "adresse": "1A Route de Schweighouse, 67500 HAGUENAU",
                "horaires": "Lun-Ven: 8h-18h, Sam: 9h-16h",
                "zone_intervention": "Haguenau et 30km alentour",
                "certifications": ["QUALIOPI", "Datadock"],
                "assurance": "Responsabilité civile professionnelle"
            }
        }
        
        # Güncel finansal veriler (2025)
        self.financial_data = {
            "2025": {
                "octobre": {
                    "chiffre_affaires": 41558.85,
                    "detail": {
                        "formation_excel": 12425.35,
                        "bilans_competences": 9966.86,
                        "formation_python": 6649.42,
                        "formation_autocad": 4532.11,
                        "formation_wordpress": 3902.54,
                        "depannage": 4082.57
                    }
                },
                "janvier_octobre": {
                    "total": 119386.85,
                    "projection_annuelle": 143264.22,
                    "croissance": "+23% vs 2024"
                },
                "kpis": {
                    "clients_actifs": 2734,
                    "taux_satisfaction": "98.2%",
                    "panier_moyen": "43.67€",
                    "retention_clients": "89.4%"
                }
            }
        }
        
        # Sık sorulan sorular ve cevaplar
        self.common_qa = {
            "formation": [
                {
                    "question": "Comment financer une formation ?",
                    "reponse": "Nos formations sont éligibles CPF et OPCO. Nous vous accompagnons dans les démarches de financement.",
                    "tags": ["cpf", "opco", "financement"]
                },
                {
                    "question": "Quelles sont les modalités de formation ?",
                    "reponse": "Formation en présentiel ou à distance, individuelle ou en groupe. Planning flexible selon vos disponibilités.",
                    "tags": ["modalites", "planning", "distance"]
                },
                {
                    "question": "Les formations sont-elles certifiantes ?",
                    "reponse": "Oui, toutes nos formations sont certifiées QUALIOPI et donnent lieu à une attestation de formation.",
                    "tags": ["certification", "qualiopi", "attestation"]
                }
            ],
            "depannage": [
                {
                    "question": "Combien coûte un diagnostic ?",
                    "reponse": "Le diagnostic est GRATUIT. Vous ne payez que si vous acceptez la réparation.",
                    "tags": ["diagnostic", "gratuit", "prix"]
                },
                {
                    "question": "Quelle est la garantie sur les réparations ?",
                    "reponse": "Toutes nos réparations sont garanties 3 mois pièces et main d'œuvre.",
                    "tags": ["garantie", "reparation", "3mois"]
                },
                {
                    "question": "Intervenez-vous à domicile ?",
                    "reponse": "Oui, nous intervenons à domicile dans un rayon de 30km autour de Haguenau.",
                    "tags": ["domicile", "deplacement", "haguenau"]
                }
            ],
            "maintenance": [
                {
                    "question": "Que comprend l'abonnement maintenance ?",
                    "reponse": "Mises à jour, optimisation, nettoyage, sauvegarde, support téléphonique prioritaire 24/7.",
                    "tags": ["maintenance", "inclus", "support"]
                },
                {
                    "question": "Peut-on résilier l'abonnement ?",
                    "reponse": "Oui, résiliation possible à tout moment avec préavis de 30 jours.",
                    "tags": ["resiliation", "preavis", "flexible"]
                }
            ]
        }
    
    def get_quick_info(self, info_type: str) -> Dict[str, Any]:
        """Hızlı bilgi erişimi"""
        if info_type not in self.quick_access_data:
            raise HTTPException(status_code=404, detail=f"Info type '{info_type}' not found")
        
        result = {
            "type": info_type,
            "data": self.quick_access_data[info_type],
            "timestamp": datetime.now().isoformat()
        }
        
        # Finansal veriler için özel işlem
        if info_type == "financials":
            result["data"] = self.financial_data
        
        return result
    
    def search_knowledge(self, query: str, category: str = None, language: str = "fr") -> Dict[str, Any]:
        """Bilgi arama"""
        results = {
            "query": query,
            "category": category,
            "language": language,
            "results": [],
            "suggestions": [],
            "timestamp": datetime.now().isoformat()
        }
        
        query_lower = query.lower()
        
        # Hızlı erişim verilerinde ara
        for data_type, data in self.quick_access_data.items():
            matches = self._search_in_dict(data, query_lower, data_type)
            results["results"].extend(matches)
        
        # Sık sorulan sorularda ara
        for qa_category, questions in self.common_qa.items():
            if category and category != qa_category:
                continue
                
            for qa in questions:
                if (query_lower in qa["question"].lower() or 
                    query_lower in qa["reponse"].lower() or
                    any(tag in query_lower for tag in qa["tags"])):
                    results["results"].append({
                        "type": "faq",
                        "category": qa_category,
                        "question": qa["question"],
                        "answer": qa["reponse"],
                        "relevance": self._calculate_relevance(query_lower, qa),
                        "tags": qa["tags"]
                    })
        
        # Learning system'den ara (varsa)
        if self.learning_system:
            similar_entries = self.learning_system.find_similar_queries(query, limit=5)
            for entry in similar_entries:
                results["results"].append({
                    "type": "learned",
                    "category": entry["category"],
                    "query": entry["query"],
                    "answer": entry["response"],
                    "confidence": entry["confidence"],
                    "similarity": entry["similarity"]
                })
        
        # Sonuçları relevance'a göre sırala
        results["results"].sort(key=lambda x: x.get("relevance", x.get("similarity", 0)), reverse=True)
        
        # Öneriler oluştur
        results["suggestions"] = self._generate_suggestions(query_lower, category)
        
        return results
    
    def _search_in_dict(self, data: Dict, query: str, data_type: str, path: str = "") -> List[Dict]:
        """Dictionary'de recursive arama"""
        results = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}/{key}" if path else key
                
                # Key'de ara
                if query in key.lower():
                    results.append({
                        "type": "quick_access",
                        "category": data_type,
                        "path": current_path,
                        "key": key,
                        "value": value,
                        "relevance": self._calculate_text_relevance(query, key.lower())
                    })
                
                # Value'da ara (eğer string ise)
                if isinstance(value, str) and query in value.lower():
                    results.append({
                        "type": "quick_access",
                        "category": data_type,
                        "path": current_path,
                        "key": key,
                        "value": value,
                        "relevance": self._calculate_text_relevance(query, value.lower())
                    })
                
                # Recursive arama
                elif isinstance(value, dict):
                    results.extend(self._search_in_dict(value, query, data_type, current_path))
                    
        return results
    
    def _calculate_relevance(self, query: str, qa: Dict) -> float:
        """QA relevance hesapla"""
        score = 0.0
        
        # Question match
        if query in qa["question"].lower():
            score += 0.5
        
        # Answer match
        if query in qa["reponse"].lower():
            score += 0.3
        
        # Tag match
        for tag in qa["tags"]:
            if tag.lower() in query:
                score += 0.2
        
        # Word overlap
        query_words = set(query.split())
        question_words = set(qa["question"].lower().split())
        answer_words = set(qa["reponse"].lower().split())
        
        overlap_q = len(query_words & question_words) / max(len(query_words), 1)
        overlap_a = len(query_words & answer_words) / max(len(query_words), 1)
        
        score += overlap_q * 0.3 + overlap_a * 0.2
        
        return min(score, 1.0)
    
    def _calculate_text_relevance(self, query: str, text: str) -> float:
        """Text relevance hesapla"""
        if query in text:
            return 1.0
        
        query_words = set(query.split())
        text_words = set(text.split())
        
        overlap = len(query_words & text_words)
        return overlap / max(len(query_words), 1)
    
    def _generate_suggestions(self, query: str, category: str = None) -> List[str]:
        """Arama önerileri oluştur"""
        suggestions = []
        
        # Kategori bazlı öneriler
        if not category:
            if any(word in query for word in ["prix", "tarif", "coût", "euro"]):
                suggestions.extend(["pricing - Voir tous les tarifs", "formation - Tarifs formation", "depannage - Tarifs dépannage"])
            
            if any(word in query for word in ["formation", "cours", "apprendre"]):
                suggestions.extend(["formation excel", "formation python", "certification QUALIOPI"])
            
            if any(word in query for word in ["dépannage", "réparer", "panne"]):
                suggestions.extend(["diagnostic gratuit", "garantie 3 mois", "intervention domicile"])
            
            if any(word in query for word in ["maintenance", "abonnement"]):
                suggestions.extend(["maintenance préventive", "support 24/7", "résiliation flexible"])
        
        # Popüler arama terimleri
        popular_terms = [
            "tarifs formation",
            "financement CPF",
            "diagnostic gratuit",
            "intervention domicile", 
            "garantie réparation",
            "certification QUALIOPI",
            "support maintenance",
            "contact urgence"
        ]
        
        # Query'ye benzer terimleri ekle
        for term in popular_terms:
            if len(suggestions) < 5 and term not in suggestions:
                if any(word in term.lower() for word in query.split()):
                    suggestions.append(term)
        
        return suggestions[:5]
    
    def get_employee_dashboard(self) -> Dict[str, Any]:
        """Çalışan dashboard verileri"""
        today = datetime.now()
        
        dashboard = {
            "timestamp": today.isoformat(),
            "quick_stats": {
                "active_clients": self.financial_data["2025"]["kpis"]["clients_actifs"],
                "monthly_revenue": self.financial_data["2025"]["octobre"]["chiffre_affaires"],
                "satisfaction_rate": self.financial_data["2025"]["kpis"]["taux_satisfaction"],
                "retention_rate": self.financial_data["2025"]["kpis"]["retention_clients"]
            },
            "top_services": [
                {"name": "Formation Excel", "revenue": 12425.35, "percentage": 30},
                {"name": "Bilans Compétences", "revenue": 9966.86, "percentage": 24},
                {"name": "Formation Python", "revenue": 6649.42, "percentage": 16},
                {"name": "Formation AutoCAD", "revenue": 4532.11, "percentage": 11},
                {"name": "Dépannage", "revenue": 4082.57, "percentage": 10}
            ],
            "quick_actions": [
                {"title": "Nouveau devis", "action": "create_quote", "icon": "document"},
                {"title": "Planifier intervention", "action": "schedule_visit", "icon": "calendar"},
                {"title": "Voir planning", "action": "view_schedule", "icon": "schedule"},
                {"title": "Contacts clients", "action": "client_contacts", "icon": "contacts"},
                {"title": "Tarifs services", "action": "view_pricing", "icon": "euro"},
                {"title": "Support technique", "action": "tech_support", "icon": "support"}
            ],
            "recent_activity": self._get_recent_activity(),
            "alerts": self._get_alerts(),
            "weather": f"Haguenau - {today.strftime('%d/%m/%Y')}"
        }
        
        return dashboard
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Son aktiviteler (mock data)"""
        return [
            {
                "time": "09:30",
                "type": "intervention",
                "description": "Dépannage PC - M. Dupont",
                "status": "en_cours"
            },
            {
                "time": "14:00",
                "type": "formation",
                "description": "Formation Excel - Groupe 5 personnes",
                "status": "planifie"
            },
            {
                "time": "16:30",
                "type": "devis",
                "description": "Devis maintenance - Entreprise XYZ",
                "status": "envoye"
            }
        ]
    
    def _get_alerts(self) -> List[Dict[str, Any]]:
        """Alerts (mock data)"""
        return [
            {
                "type": "info",
                "message": "5 nouveaux clients ce mois",
                "priority": "low"
            },
            {
                "type": "warning", 
                "message": "Planning formation Excel complet cette semaine",
                "priority": "medium"
            }
        ]
    
    def get_client_info_quick(self, client_query: str) -> Dict[str, Any]:
        """Client bilgi hızlı erişim"""
        # Bu gerçek bir client database'i olmadığı için mock data
        mock_clients = {
            "dupont": {
                "nom": "M. Dupont",
                "telephone": "03 88 XX XX XX",
                "adresse": "Haguenau",
                "services": ["Dépannage", "Maintenance"],
                "derniere_intervention": "15/01/2025",
                "statut": "Actif"
            },
            "martin": {
                "nom": "Mme Martin",
                "telephone": "06 XX XX XX XX", 
                "adresse": "Bischwiller",
                "services": ["Formation Excel"],
                "derniere_intervention": "10/01/2025",
                "statut": "Actif"
            }
        }
        
        query_lower = client_query.lower()
        
        for key, client in mock_clients.items():
            if (key in query_lower or 
                query_lower in client["nom"].lower() or
                query_lower in client["adresse"].lower()):
                
                return {
                    "found": True,
                    "client": client,
                    "search_query": client_query
                }
        
        return {
            "found": False,
            "message": "Client non trouvé",
            "search_query": client_query,
            "suggestions": ["Vérifiez l'orthographe", "Essayez avec le numéro de téléphone"]
        }

# FastAPI routes pour employee interface
def add_employee_routes(app: FastAPI, learning_system=None):
    """Employee interface routes ekle"""
    
    employee_interface = EmployeeKnowledgeInterface(learning_system)
    
    @app.get("/employee/dashboard")
    async def get_employee_dashboard():
        """Çalışan dashboard"""
        return employee_interface.get_employee_dashboard()
    
    @app.get("/employee/quick-info/{info_type}")
    async def get_quick_info(info_type: str):
        """Hızlı bilgi erişimi"""
        return employee_interface.get_quick_info(info_type)
    
    @app.post("/employee/search")
    async def search_knowledge(query_data: EmployeeQuery):
        """Bilgi arama"""
        return employee_interface.search_knowledge(
            query_data.query, 
            query_data.category, 
            query_data.language
        )
    
    @app.get("/employee/client-search/{client_query}")
    async def search_client(client_query: str):
        """Client arama"""
        return employee_interface.get_client_info_quick(client_query)
    
    @app.get("/employee/faq/{category}")
    async def get_faq_by_category(category: str):
        """Kategori bazlı FAQ"""
        if category not in employee_interface.common_qa:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return {
            "category": category,
            "questions": employee_interface.common_qa[category],
            "count": len(employee_interface.common_qa[category])
        }
    
    @app.get("/employee/all-faq")
    async def get_all_faq():
        """Tüm FAQ'ler"""
        return employee_interface.common_qa

if __name__ == "__main__":
    # Test
    interface = EmployeeKnowledgeInterface()
    
    # Dashboard test
    dashboard = interface.get_employee_dashboard()
    print("Dashboard:", json.dumps(dashboard, indent=2, ensure_ascii=False))
    
    # Arama test
    search_result = interface.search_knowledge("formation prix")
    print("Search result:", json.dumps(search_result, indent=2, ensure_ascii=False))
    
    # Hızlı erişim test
    pricing = interface.get_quick_info("pricing")
    print("Pricing:", json.dumps(pricing, indent=2, ensure_ascii=False))