#!/usr/bin/env python3
"""
NETZ AI Advanced Offline Learning System
Sürekli öğrenim ve hafıza geliştirme sistemi
"""

import os
import json
import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import pickle
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LearningEntry:
    """Öğrenim verisi yapısı"""
    id: str
    query: str
    response: str
    category: str
    language: str
    confidence: float
    timestamp: datetime
    source: str
    context: Dict[str, Any]
    feedback_score: Optional[float] = None
    tags: List[str] = None

class AdvancedOfflineLearning:
    """Gelişmiş offline öğrenim sistemi"""
    
    def __init__(self, data_dir: str = "learning_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Veritabanı bağlantısı
        self.db_path = self.data_dir / "netz_learning.db"
        self._init_database()
        
        # Hafıza dosyaları
        self.knowledge_file = self.data_dir / "netz_knowledge.json"
        self.patterns_file = self.data_dir / "learned_patterns.pkl"
        self.stats_file = self.data_dir / "learning_stats.json"
        
        # Hafızada tutulacak veriler
        self.knowledge_base = self._load_knowledge_base()
        self.learned_patterns = self._load_patterns()
        self.learning_stats = self._load_stats()
        
        # Thread pool for background processing
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info(f"NETZ AI Offline Learning System initialized with {len(self.knowledge_base)} entries")
    
    def _init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ana öğrenim tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_entries (
            id TEXT PRIMARY KEY,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            category TEXT,
            language TEXT,
            confidence REAL,
            timestamp TEXT,
            source TEXT,
            context TEXT,
            feedback_score REAL,
            tags TEXT
        )
        ''')
        
        # İstatistik tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_stats (
            date TEXT PRIMARY KEY,
            total_queries INTEGER,
            successful_responses INTEGER,
            avg_confidence REAL,
            categories TEXT,
            languages TEXT
        )
        ''')
        
        # İndeksler
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON learning_entries(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_language ON learning_entries(language)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON learning_entries(timestamp)')
        
        conn.commit()
        conn.close()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """NETZ bilgi tabanını yükle"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Knowledge base yüklenemedi: {e}")
        
        # Default NETZ bilgileri
        return {
            "company": {
                "name": "NETZ INFORMATIQUE",
                "siret": "818 347 346 00020",
                "address": "1A Route de Schweighouse, 67500 HAGUENAU",
                "phone": "07 67 74 49 03",
                "email": "contact@netzinformatique.fr",
                "website": "www.netzinformatique.fr",
                "founder": "Mikail LEKESIZ"
            },
            "services": {
                "formation": {
                    "price_individual": "45€/h",
                    "price_group": "250€/demi-journée",
                    "subjects": ["Excel", "Python", "Word", "PowerPoint", "Cybersécurité"],
                    "certification": "QUALIOPI",
                    "eligible": "CPF et OPCO"
                },
                "depannage": {
                    "price_private": "55€/h",
                    "price_business": "75€/h",
                    "diagnostic": "GRATUIT",
                    "warranty": "3 mois"
                },
                "maintenance": {
                    "price_private": "39€/mois",
                    "price_business": "69€/mois/poste",
                    "features": ["Mises à jour", "Optimisation", "Support 24/7"]
                }
            },
            "financials_2025": {
                "october_revenue": 41558.85,
                "ytd_total": 119386.85,
                "projection": 143264.22,
                "top_services": {
                    "excel_formation": 30,
                    "bilans_competences": 24,
                    "python_formation": 16,
                    "autocad_formation": 11,
                    "wordpress_formation": 9
                },
                "active_clients": 2734
            }
        }
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Öğrenilmiş kalıpları yükle"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Patterns yüklenemedi: {e}")
        
        return {
            "common_queries": {},
            "response_templates": {},
            "user_preferences": {},
            "successful_patterns": {}
        }
    
    def _load_stats(self) -> Dict[str, Any]:
        """Öğrenim istatistiklerini yükle"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Stats yüklenemedi: {e}")
        
        return {
            "total_interactions": 0,
            "successful_responses": 0,
            "avg_confidence": 0.0,
            "categories": {},
            "languages": {"fr": 0, "en": 0, "tr": 0},
            "daily_usage": {},
            "learning_rate": 0.0
        }
    
    def add_learning_entry(self, 
                          query: str, 
                          response: str, 
                          category: str = "general",
                          language: str = "fr",
                          confidence: float = 0.8,
                          source: str = "user",
                          context: Dict[str, Any] = None,
                          feedback_score: Optional[float] = None) -> str:
        """Yeni öğrenim verisi ekle"""
        
        entry_id = hashlib.md5(f"{query}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        entry = LearningEntry(
            id=entry_id,
            query=query.strip(),
            response=response.strip(),
            category=category,
            language=language,
            confidence=confidence,
            timestamp=datetime.now(),
            source=source,
            context=context or {},
            feedback_score=feedback_score,
            tags=[]
        )
        
        # Veritabanına kaydet
        self._save_to_database(entry)
        
        # Hafızaya ekle (asenkron)
        self.executor.submit(self._update_memory, entry)
        
        logger.info(f"Learning entry added: {entry_id} ({category}, {language})")
        return entry_id
    
    def _save_to_database(self, entry: LearningEntry):
        """Veritabanına kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO learning_entries 
        (id, query, response, category, language, confidence, timestamp, source, context, feedback_score, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.id,
            entry.query,
            entry.response,
            entry.category,
            entry.language,
            entry.confidence,
            entry.timestamp.isoformat(),
            entry.source,
            json.dumps(entry.context),
            entry.feedback_score,
            json.dumps(entry.tags or [])
        ))
        
        conn.commit()
        conn.close()
    
    def _update_memory(self, entry: LearningEntry):
        """Hafıza güncelle"""
        # İstatistikleri güncelle
        self.learning_stats["total_interactions"] += 1
        
        if entry.confidence > 0.7:
            self.learning_stats["successful_responses"] += 1
        
        # Kategori istatistikleri
        if entry.category not in self.learning_stats["categories"]:
            self.learning_stats["categories"][entry.category] = 0
        self.learning_stats["categories"][entry.category] += 1
        
        # Dil istatistikleri
        if entry.language in self.learning_stats["languages"]:
            self.learning_stats["languages"][entry.language] += 1
        
        # Günlük kullanım
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.learning_stats["daily_usage"]:
            self.learning_stats["daily_usage"][today] = 0
        self.learning_stats["daily_usage"][today] += 1
        
        # Ortalama güven skoru
        total = self.learning_stats["total_interactions"]
        current_avg = self.learning_stats["avg_confidence"]
        new_avg = (current_avg * (total - 1) + entry.confidence) / total
        self.learning_stats["avg_confidence"] = new_avg
        
        # Öğrenme oranı hesapla
        success_rate = self.learning_stats["successful_responses"] / total
        self.learning_stats["learning_rate"] = success_rate
        
        # Ortak sorguları güncelle
        query_hash = hashlib.md5(entry.query.lower().encode()).hexdigest()[:8]
        if query_hash not in self.learned_patterns["common_queries"]:
            self.learned_patterns["common_queries"][query_hash] = {
                "query": entry.query,
                "count": 0,
                "responses": [],
                "avg_confidence": 0.0
            }
        
        pattern = self.learned_patterns["common_queries"][query_hash]
        pattern["count"] += 1
        pattern["responses"].append({
            "response": entry.response,
            "confidence": entry.confidence,
            "timestamp": entry.timestamp.isoformat()
        })
        
        # En fazla 5 yanıt sakla
        if len(pattern["responses"]) > 5:
            pattern["responses"] = pattern["responses"][-5:]
        
        # Ortalama güveni güncelle
        confidences = [r["confidence"] for r in pattern["responses"]]
        pattern["avg_confidence"] = sum(confidences) / len(confidences)
        
        # Dosyaları kaydet
        self._save_all_data()
    
    def _save_all_data(self):
        """Tüm verileri dosyalara kaydet"""
        try:
            # Knowledge base
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
            
            # Patterns
            with open(self.patterns_file, 'wb') as f:
                pickle.dump(self.learned_patterns, f)
            
            # Stats
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_stats, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Veri kaydedilirken hata: {e}")
    
    def find_similar_queries(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Benzer sorguları bul"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basit benzerlik araması (gerçek üretimde daha gelişmiş algoritma kullanılır)
        words = query.lower().split()
        similar_entries = []
        
        cursor.execute('SELECT * FROM learning_entries ORDER BY confidence DESC')
        entries = cursor.fetchall()
        
        for entry in entries[:100]:  # İlk 100 girişi kontrol et
            entry_words = entry[1].lower().split()  # query field
            common_words = set(words) & set(entry_words)
            
            if len(common_words) > 0:
                similarity = len(common_words) / max(len(words), len(entry_words))
                
                if similarity > 0.3:  # %30 benzerlik eşiği
                    similar_entries.append({
                        "id": entry[0],
                        "query": entry[1],
                        "response": entry[2],
                        "category": entry[3],
                        "confidence": entry[5],
                        "similarity": similarity
                    })
        
        # Benzerlik skoruna göre sırala
        similar_entries.sort(key=lambda x: x["similarity"], reverse=True)
        
        conn.close()
        return similar_entries[:limit]
    
    def get_knowledge_for_context(self, category: str = None, language: str = None) -> Dict[str, Any]:
        """Bağlam için bilgi getir"""
        result = {"base_knowledge": self.knowledge_base}
        
        if category:
            # Kategori-specific bilgi
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT query, response, confidence FROM learning_entries WHERE category = ?"
            params = [category]
            
            if language:
                query += " AND language = ?"
                params.append(language)
            
            query += " ORDER BY confidence DESC LIMIT 10"
            
            cursor.execute(query, params)
            entries = cursor.fetchall()
            
            result["category_examples"] = [
                {"query": entry[0], "response": entry[1], "confidence": entry[2]}
                for entry in entries
            ]
            
            conn.close()
        
        # İstatistikler ekle
        result["stats"] = self.learning_stats
        
        return result
    
    def get_employee_knowledge_interface(self) -> Dict[str, Any]:
        """Çalışanlar için bilgi arayüzü"""
        return {
            "company_info": self.knowledge_base.get("company", {}),
            "services": self.knowledge_base.get("services", {}),
            "financials": self.knowledge_base.get("financials_2025", {}),
            "common_queries": list(self.learned_patterns["common_queries"].values())[:20],
            "statistics": {
                "total_knowledge_entries": len(self.learned_patterns["common_queries"]),
                "success_rate": self.learning_stats.get("learning_rate", 0),
                "languages_supported": list(self.learning_stats["languages"].keys()),
                "categories": list(self.learning_stats["categories"].keys())
            },
            "quick_access": {
                "pricing": self.knowledge_base.get("services", {}),
                "contact_info": self.knowledge_base.get("company", {}),
                "latest_stats": self.learning_stats
            }
        }
    
    def update_knowledge_base(self, category: str, data: Dict[str, Any]):
        """Bilgi tabanını güncelle"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        self.knowledge_base[category].update(data)
        
        # Dosyaya kaydet
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Knowledge base updated: {category}")
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """Öğrenim raporu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Son 7 günün istatistikleri
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('''
        SELECT COUNT(*), AVG(confidence), category, language
        FROM learning_entries 
        WHERE timestamp > ?
        GROUP BY category, language
        ''', (week_ago,))
        
        recent_stats = cursor.fetchall()
        
        # En popüler sorgular
        cursor.execute('''
        SELECT query, COUNT(*) as count, AVG(confidence) as avg_conf
        FROM learning_entries 
        WHERE timestamp > ?
        GROUP BY query
        ORDER BY count DESC
        LIMIT 10
        ''', (week_ago,))
        
        popular_queries = cursor.fetchall()
        
        conn.close()
        
        return {
            "summary": {
                "total_entries": self.learning_stats["total_interactions"],
                "success_rate": f"{self.learning_stats['learning_rate']*100:.1f}%",
                "avg_confidence": f"{self.learning_stats['avg_confidence']:.2f}",
                "languages": self.learning_stats["languages"],
                "categories": self.learning_stats["categories"]
            },
            "recent_activity": {
                "last_7_days": [
                    {
                        "category": stat[2],
                        "language": stat[3],
                        "count": stat[0],
                        "avg_confidence": stat[1]
                    } for stat in recent_stats
                ]
            },
            "popular_queries": [
                {
                    "query": query[0],
                    "count": query[1],
                    "avg_confidence": query[2]
                } for query in popular_queries
            ],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Gelişim önerileri"""
        recommendations = []
        
        success_rate = self.learning_stats.get("learning_rate", 0)
        if success_rate < 0.8:
            recommendations.append("Yanıt kalitesini artırmak için daha fazla training data gerekli")
        
        categories = self.learning_stats.get("categories", {})
        if len(categories) < 5:
            recommendations.append("Daha fazla kategori eklenerek bilgi çeşitliliği artırılabilir")
        
        languages = self.learning_stats.get("languages", {})
        if languages.get("tr", 0) < languages.get("fr", 0) * 0.1:
            recommendations.append("Türkçe içerik artırılması önerilir")
        
        if self.learning_stats.get("total_interactions", 0) < 1000:
            recommendations.append("Daha fazla kullanıcı etkileşimi ile sistem gelişecek")
        
        return recommendations

# Global instance
netz_learning_system = None

def get_learning_system() -> AdvancedOfflineLearning:
    """Learning system instance'ını getir"""
    global netz_learning_system
    if netz_learning_system is None:
        netz_learning_system = AdvancedOfflineLearning()
    return netz_learning_system

def init_learning_system(data_dir: str = "learning_data") -> AdvancedOfflineLearning:
    """Learning system'i başlat"""
    global netz_learning_system
    netz_learning_system = AdvancedOfflineLearning(data_dir)
    return netz_learning_system

if __name__ == "__main__":
    # Test
    learning_system = AdvancedOfflineLearning("test_learning")
    
    # Test verileri ekle
    learning_system.add_learning_entry(
        query="NETZ'in hizmetleri nelerdir?",
        response="NETZ Informatique formation, dépannage ve maintenance hizmetleri sunar.",
        category="services",
        language="tr",
        confidence=0.9
    )
    
    learning_system.add_learning_entry(
        query="Quels sont les tarifs de formation?",
        response="Formation individuelle 45€/h, formation groupe 250€/demi-journée.",
        category="pricing",
        language="fr",
        confidence=0.95
    )
    
    # Rapor oluştur
    report = learning_system.generate_learning_report()
    print("Learning Report:", json.dumps(report, indent=2, ensure_ascii=False))
    
    # Benzer sorguları test et
    similar = learning_system.find_similar_queries("NETZ hizmetleri")
    print("Similar queries:", similar)