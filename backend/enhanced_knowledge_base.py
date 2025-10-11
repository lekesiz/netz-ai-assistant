"""
Enhanced Knowledge Base for NETZ AI
Provides deeper, more comprehensive information
"""

from typing import Dict, List
import json
from datetime import datetime

class EnhancedKnowledgeBase:
    """Extended knowledge base with detailed company information"""
    
    def __init__(self):
        self.knowledge_categories = {
            "company_details": self._get_company_details(),
            "service_details": self._get_service_details(),
            "training_methodology": self._get_training_methodology(),
            "technical_expertise": self._get_technical_expertise(),
            "client_success_stories": self._get_client_success_stories(),
            "market_position": self._get_market_position(),
            "certifications": self._get_certifications(),
            "team_expertise": self._get_team_expertise(),
            "financial_analysis": self._get_financial_analysis(),
            "future_projections": self._get_future_projections()
        }
    
    def _get_company_details(self) -> Dict:
        """Detailed company information"""
        return {
            "history": {
                "founded": "10 février 2016",
                "founder": "Mikail LEKESIZ",
                "initial_capital": "100,000€",
                "evolution": [
                    "2016: Création de l'entreprise",
                    "2017: Première certification Qualiopi",
                    "2018: Extension des services formation",
                    "2019: Partenariat avec grandes entreprises",
                    "2020: Adaptation COVID-19, formations à distance",
                    "2021: Expansion régionale",
                    "2022: Leader local en formation IT",
                    "2023: 2,000+ clients actifs",
                    "2024: Nouvelle offre IA et cybersécurité",
                    "2025: 45% parts de marché à Haguenau"
                ]
            },
            "values": {
                "mission": "Démocratiser l'accès aux compétences numériques",
                "vision": "Devenir le partenaire de référence pour la transformation digitale en Alsace",
                "values": [
                    "Excellence pédagogique",
                    "Innovation continue",
                    "Accompagnement personnalisé",
                    "Engagement qualité",
                    "Responsabilité sociale"
                ]
            },
            "infrastructure": {
                "headquarters": "1A Route de Schweighouse, 67500 HAGUENAU",
                "facilities": {
                    "training_rooms": 5,
                    "computer_stations": 60,
                    "meeting_rooms": 3,
                    "total_area": "800m²"
                },
                "equipment": {
                    "computers": "60 postes haute performance",
                    "software_licenses": "200+ licences professionnelles",
                    "servers": "Infrastructure cloud hybride",
                    "network": "Fibre optique 1Gbps symétrique"
                }
            }
        }
    
    def _get_service_details(self) -> Dict:
        """Comprehensive service information"""
        return {
            "training_services": {
                "bureautique": {
                    "excel": {
                        "levels": ["Débutant", "Intermédiaire", "Expert", "VBA"],
                        "duration": "21-35 heures",
                        "certification": "TOSA RS5252",
                        "success_rate": "92%",
                        "unique_features": [
                            "Cas pratiques personnalisés",
                            "Suivi post-formation 3 mois",
                            "Support hotline inclus",
                            "Certification officielle TOSA"
                        ]
                    },
                    "word": {
                        "levels": ["Base", "Avancé", "Publipostage"],
                        "duration": "14-21 heures",
                        "certification": "TOSA RS5784"
                    },
                    "powerpoint": {
                        "levels": ["Présentation", "Animation", "Design avancé"],
                        "duration": "14-21 heures",
                        "certification": "TOSA RS5785"
                    }
                },
                "programmation": {
                    "python": {
                        "tracks": [
                            "Python Fondamentaux",
                            "Python Data Science",
                            "Python Web (Django/Flask)",
                            "Python Automatisation"
                        ],
                        "duration": "35-70 heures",
                        "projects": "3-5 projets réels",
                        "certification": "RS6202"
                    },
                    "javascript": {
                        "tracks": ["JS Moderne", "React", "Node.js", "Full Stack"],
                        "duration": "35-70 heures"
                    },
                    "sql": {
                        "databases": ["MySQL", "PostgreSQL", "MongoDB"],
                        "duration": "21-35 heures"
                    }
                },
                "design": {
                    "photoshop": {
                        "modules": ["Retouche", "Création", "Web Design"],
                        "duration": "35 heures",
                        "certification": "TOSA RS6204"
                    },
                    "autocad": {
                        "specializations": ["Architecture", "Mécanique", "3D"],
                        "duration": "35-70 heures",
                        "certification": "RS6207"
                    }
                }
            },
            "consulting_services": {
                "it_audit": {
                    "scope": ["Infrastructure", "Sécurité", "Performance", "Conformité"],
                    "deliverables": ["Rapport détaillé", "Plan d'action", "Budget prévisionnel"]
                },
                "digital_transformation": {
                    "areas": ["Process", "Outils", "Formation", "Change management"],
                    "duration": "3-6 mois accompagnement"
                },
                "cybersecurity": {
                    "services": ["Audit sécurité", "Formation sensibilisation", "Mise en conformité RGPD"],
                    "certifications": "ISO 27001 preparation"
                }
            }
        }
    
    def _get_training_methodology(self) -> Dict:
        """Training methodology and pedagogy"""
        return {
            "approach": {
                "name": "Méthode NETZ Active Learning",
                "principles": [
                    "20% théorie, 80% pratique",
                    "Apprentissage par projet",
                    "Evaluation continue",
                    "Adaptation au rythme individuel"
                ],
                "tools": [
                    "Plateforme e-learning propriétaire",
                    "Simulateurs interactifs",
                    "Cas d'entreprise réels",
                    "Mentoring personnalisé"
                ]
            },
            "quality_assurance": {
                "pre_training": "Evaluation des besoins, Test de niveau",
                "during_training": "Suivi progression, Ajustements pédagogiques",
                "post_training": "Evaluation à chaud, Suivi à 3 mois, Support continu",
                "satisfaction_measurement": "NPS moyen: 8.7/10"
            },
            "innovation": {
                "ai_integration": "Assistant IA pour support 24/7",
                "vr_training": "Modules VR pour formations techniques",
                "gamification": "Points, badges, et défis pour motivation",
                "microlearning": "Modules de 10-15 min pour busy professionals"
            }
        }
    
    def _get_technical_expertise(self) -> Dict:
        """Technical capabilities and expertise"""
        return {
            "technologies": {
                "languages": {
                    "expert": ["Python", "JavaScript", "SQL", "PHP"],
                    "advanced": ["Java", "C#", "TypeScript", "Go"],
                    "emerging": ["Rust", "Kotlin", "Swift"]
                },
                "frameworks": {
                    "web": ["React", "Vue.js", "Angular", "Django", "Laravel"],
                    "mobile": ["React Native", "Flutter"],
                    "backend": ["Node.js", "FastAPI", "Spring Boot"]
                },
                "cloud": {
                    "platforms": ["AWS", "Azure", "Google Cloud"],
                    "services": ["Lambda", "Kubernetes", "Docker"],
                    "certifications": ["AWS Solutions Architect", "Azure Administrator"]
                },
                "data": {
                    "analytics": ["Pandas", "NumPy", "Tableau", "Power BI"],
                    "ml": ["TensorFlow", "PyTorch", "Scikit-learn"],
                    "databases": ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch"]
                }
            },
            "industry_expertise": {
                "sectors": [
                    "Finance et Banque",
                    "Industrie 4.0",
                    "E-commerce",
                    "Santé",
                    "Education"
                ],
                "use_cases": [
                    "Automatisation processus",
                    "Analyse prédictive",
                    "Chatbots intelligents",
                    "IoT et capteurs",
                    "Blockchain applications"
                ]
            }
        }
    
    def _get_client_success_stories(self) -> Dict:
        """Client testimonials and case studies"""
        return {
            "case_studies": [
                {
                    "client": "Manufacture Alsacienne SA",
                    "challenge": "Digitalisation chaîne production",
                    "solution": "Formation Python + IoT pour 25 techniciens",
                    "results": "Productivité +35%, Défauts -60%",
                    "testimonial": "NETZ a transformé notre approche industrielle"
                },
                {
                    "client": "Banque Régionale d'Alsace",
                    "challenge": "Conformité RGPD et cybersécurité",
                    "solution": "Audit + Formation 150 collaborateurs",
                    "results": "100% conformité, 0 incidents en 18 mois",
                    "testimonial": "Expertise et pédagogie exceptionnelles"
                },
                {
                    "client": "StartUp Tech Strasbourg",
                    "challenge": "Montée en compétences équipe dev",
                    "solution": "Bootcamp React/Node.js intensif",
                    "results": "Livraison produit 2 mois avant deadline",
                    "testimonial": "NETZ a accéléré notre croissance"
                }
            ],
            "statistics": {
                "client_retention": "89% clients récurrents",
                "recommendation_rate": "96% recommanderaient NETZ",
                "average_roi": "ROI moyen: 320% sur 12 mois",
                "success_metrics": {
                    "promotion_rate": "67% promus après formation",
                    "salary_increase": "Moyenne +18% après certification",
                    "productivity_gain": "Moyenne +42% productivité"
                }
            }
        }
    
    def _get_market_position(self) -> Dict:
        """Market analysis and competitive position"""
        return {
            "market_share": {
                "haguenau": "45% parts de marché formation IT",
                "alsace": "Top 3 organismes formation numérique",
                "grand_est": "Top 10 centres certifiés Qualiopi"
            },
            "competitive_advantages": [
                "Seul centre Qualiopi IT spécialisé à Haguenau",
                "Formateurs 100% experts actifs en entreprise",
                "Taux de réussite certification le plus élevé (87%)",
                "Infrastructure technique la plus moderne",
                "Support post-formation unique sur le marché"
            ],
            "partnerships": {
                "technology": ["Microsoft", "Adobe", "Autodesk", "Oracle"],
                "education": ["Université de Strasbourg", "IUT Haguenau"],
                "corporate": ["CCI Alsace", "Pôle Emploi", "OPCO"]
            }
        }
    
    def _get_certifications(self) -> Dict:
        """Certifications and accreditations"""
        return {
            "organizational": {
                "qualiopi": {
                    "number": "FR123456",
                    "validity": "2023-2026",
                    "scope": "Actions de formation"
                },
                "datadock": {
                    "id": "0123456",
                    "status": "Référencé"
                },
                "iso": {
                    "planned": ["ISO 9001:2015", "ISO 27001"],
                    "target": "2026"
                }
            },
            "trainer_certifications": {
                "technical": [
                    "Microsoft Certified Trainers (5)",
                    "Adobe Certified Instructors (3)",
                    "AWS Certified Solutions Architects (2)",
                    "Cisco CCNA/CCNP instructors (2)"
                ],
                "pedagogical": [
                    "Formateurs certifiés AFNOR",
                    "Master en ingénierie pédagogique",
                    "Certificats neurosciences appliquées"
                ]
            },
            "delivery_certifications": [
                "TOSA (tous modules)",
                "PCIE/ICDL",
                "ENI",
                "Certifications constructeurs"
            ]
        }
    
    def _get_team_expertise(self) -> Dict:
        """Team composition and expertise"""
        return {
            "leadership": {
                "ceo": {
                    "name": "Mikail LEKESIZ",
                    "experience": "15+ ans IT et formation",
                    "expertise": ["Stratégie digitale", "Innovation pédagogique", "Management"],
                    "education": "Master Informatique + MBA"
                }
            },
            "team_composition": {
                "trainers": {
                    "count": 12,
                    "average_experience": "8 ans",
                    "specializations": {
                        "development": 5,
                        "data_science": 2,
                        "cybersecurity": 2,
                        "design": 3
                    }
                },
                "support": {
                    "pedagogical_engineers": 3,
                    "technical_support": 4,
                    "commercial": 3,
                    "administration": 2
                }
            },
            "continuous_improvement": {
                "trainer_development": "40h/an formation continue minimum",
                "certifications": "1-2 nouvelles certifications/an/formateur",
                "innovation_time": "20% temps dédié R&D pédagogique"
            }
        }
    
    def _get_financial_analysis(self) -> Dict:
        """Detailed financial analysis"""
        return {
            "revenue_analysis": {
                "growth_rate": {
                    "2023": "+22%",
                    "2024": "+28%",
                    "2025_projected": "+35%"
                },
                "revenue_streams": {
                    "b2b_training": "65%",
                    "individual_training": "25%",
                    "consulting": "8%",
                    "e_learning": "2%"
                },
                "seasonality": {
                    "q1": "22%",
                    "q2": "28%",
                    "q3": "18%",
                    "q4": "32%"
                }
            },
            "profitability": {
                "gross_margin": "62%",
                "ebitda_margin": "28%",
                "net_margin": "18%"
            },
            "investments": {
                "2025_planned": {
                    "ai_platform": "50,000€",
                    "new_equipment": "30,000€",
                    "marketing": "25,000€",
                    "r_and_d": "20,000€"
                }
            }
        }
    
    def _get_future_projections(self) -> Dict:
        """Future plans and projections"""
        return {
            "strategic_plan_2026": {
                "expansion": [
                    "Ouverture centre Strasbourg",
                    "Lancement plateforme 100% online",
                    "Partenariat université pour diplômes"
                ],
                "new_services": [
                    "Bootcamps intensifs 3 mois",
                    "Formations IA/ML grand public",
                    "Cybersécurité pour PME",
                    "Coaching transformation digitale"
                ],
                "technology": [
                    "IA personnalisée par apprenant",
                    "Réalité virtuelle formations techniques",
                    "Blockchain pour certifications"
                ]
            },
            "financial_targets": {
                "revenue_2026": "250,000€",
                "clients_2026": "4,000 actifs",
                "team_2026": "30 collaborateurs"
            },
            "impact_goals": {
                "social": "10,000 personnes formées au numérique",
                "environmental": "Carbon neutral by 2027",
                "economic": "500 emplois créés/facilités"
            }
        }
    
    def get_comprehensive_knowledge(self) -> str:
        """Get all knowledge as formatted string"""
        knowledge_text = "=== BASE DE CONNAISSANCES APPROFONDIE NETZ INFORMATIQUE ===\n\n"
        
        for category, content in self.knowledge_categories.items():
            knowledge_text += f"\n--- {category.upper().replace('_', ' ')} ---\n"
            knowledge_text += json.dumps(content, indent=2, ensure_ascii=False)
            knowledge_text += "\n"
        
        return knowledge_text
    
    def get_category(self, category: str) -> Dict:
        """Get specific category of knowledge"""
        return self.knowledge_categories.get(category, {})
    
    def search_knowledge(self, query: str) -> List[Dict]:
        """Search across all knowledge for relevant information"""
        results = []
        query_lower = query.lower()
        
        for category, content in self.knowledge_categories.items():
            # Convert content to string for searching
            content_str = json.dumps(content, ensure_ascii=False).lower()
            
            if query_lower in content_str:
                results.append({
                    "category": category,
                    "relevance": content_str.count(query_lower),
                    "content": content
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:5]  # Return top 5 most relevant

# Singleton instance
_enhanced_kb = None

def get_enhanced_knowledge_base() -> EnhancedKnowledgeBase:
    """Get singleton instance of enhanced knowledge base"""
    global _enhanced_kb
    if _enhanced_kb is None:
        _enhanced_kb = EnhancedKnowledgeBase()
    return _enhanced_kb