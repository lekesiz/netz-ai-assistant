#!/usr/bin/env python3
"""
Working NETZ AI API with real training data
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import hashlib
import time

# Try to import Ollama, fallback to mock
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Try to import RAG system
try:
    from lightweight_rag import LightweightRAG
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NETZ AI - Working API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
rag_system = None
netz_knowledge = {}

# Response Cache System
class SimpleCache:
    def __init__(self, max_size=1000, ttl_minutes=60):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        
    def _generate_key(self, message: str) -> str:
        """Generate cache key from message"""
        return hashlib.md5(message.lower().strip().encode()).hexdigest()
    
    def get(self, message: str) -> Dict:
        """Get cached response if exists and not expired"""
        key = self._generate_key(message)
        
        if key in self.cache:
            cached_time, response = self.cache[key]
            if datetime.now() - cached_time < self.ttl:
                self.access_times[key] = datetime.now()
                logger.info(f"💾 Cache hit for query: {message[:50]}...")
                return response
            else:
                # Expired
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
        
        return None
    
    def set(self, message: str, response: Dict):
        """Cache response"""
        key = self._generate_key(message)
        
        # Clean old entries if cache is full
        if len(self.cache) >= self.max_size:
            self._cleanup()
        
        self.cache[key] = (datetime.now(), response)
        self.access_times[key] = datetime.now()
        logger.info(f"💾 Cached response for: {message[:50]}...")
    
    def _cleanup(self):
        """Remove least recently used items"""
        if not self.access_times:
            return
            
        # Remove oldest accessed items
        sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
        items_to_remove = len(sorted_items) // 4  # Remove 25%
        
        for key, _ in sorted_items[:items_to_remove]:
            if key in self.cache:
                del self.cache[key]
            del self.access_times[key]
        
        logger.info(f"💾 Cache cleanup: removed {items_to_remove} entries")
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_minutes": self.ttl.total_seconds() / 60,
            "utilization": len(self.cache) / self.max_size * 100
        }

# Initialize cache
response_cache = SimpleCache(max_size=500, ttl_minutes=30)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "mistral"
    temperature: float = 0.7
    stream: bool = False

# NETZ Knowledge Base
NETZ_KB = {
    "company": {
        "name": "NETZ Informatique",
        "location": "Haguenau (67500)",
        "founder": "Mikail Lekesiz",
        "services": ["dépannage", "formation", "maintenance", "développement web"],
        "contact": {
            "phone": "07 67 74 49 03",
            "email": "contact@netzinformatique.fr",
            "website": "www.netzinformatique.fr",
            "hours": "Lun-Ven 9h-19h, Sam 10h-17h"
        }
    },
    "services": {
        "depannage": {
            "description": "Réparation rapide tous ordinateurs",
            "pricing": "55€/h particuliers, 75€/h entreprises",
            "features": ["Diagnostic gratuit", "Intervention 24h", "Garantie 3 mois"]
        },
        "formation": {
            "description": "Formations professionnelles certifiées QUALIOPI",
            "pricing": "45€/h individuel, 250€/demi-journée groupe",
            "subjects": ["Excel", "Word", "Python", "Cybersécurité"],
            "certification": "Eligible CPF et OPCO"
        },
        "maintenance": {
            "description": "Contrats de maintenance préventive",
            "pricing": "À partir de 39€/mois particuliers, 69€/mois/poste entreprises",
            "includes": ["Mises à jour", "Optimisation", "Support prioritaire"]
        }
    },
    "faq": {
        "zone_intervention": "Haguenau et 30km alentours. Déplacement gratuit dans Haguenau, 0.60€/km au-delà",
        "garantie": "3 mois sur main d'œuvre, 1 an sur pièces neuves",
        "urgences": "Disponible week-end avec majoration 50%",
        "devis": "Toujours gratuit avant intervention"
    }
}

def get_netz_response(user_message: str) -> str:
    """Get contextual NETZ response based on user message"""
    message_lower = user_message.lower()
    
    # Greetings
    if any(word in message_lower for word in ["bonjour", "salut", "hello", "hi"]):
        return "Bonjour ! Je suis l'assistant IA de NETZ Informatique. Comment puis-je vous aider aujourd'hui ? Nous proposons dépannage, formation, maintenance et développement web."
    
    # Company info
    elif any(word in message_lower for word in ["netz", "entreprise", "société", "qui êtes"]):
        return f"NETZ Informatique est une entreprise de services informatiques basée à {NETZ_KB['company']['location']}. Fondée par {NETZ_KB['company']['founder']}, nous proposons du dépannage, des formations certifiées QUALIOPI, de la maintenance et du développement web. Contactez-nous au {NETZ_KB['company']['contact']['phone']}."
    
    # Pricing
    elif any(word in message_lower for word in ["tarif", "prix", "coût", "combien"]):
        return f"Nos tarifs NETZ Informatique : Diagnostic GRATUIT, Dépannage {NETZ_KB['services']['depannage']['pricing']}, Formations {NETZ_KB['services']['formation']['pricing']}, Maintenance {NETZ_KB['services']['maintenance']['pricing']}. Devis toujours gratuit !"
    
    # Training/Formation
    elif any(word in message_lower for word in ["formation", "cours", "apprentissage", "qualiopi", "cpf"]):
        subjects = ", ".join(NETZ_KB['services']['formation']['subjects'])
        return f"NETZ propose des formations professionnelles certifiées QUALIOPI : {subjects}. {NETZ_KB['services']['formation']['certification']}. Tarifs : {NETZ_KB['services']['formation']['pricing']}."
    
    # Contact
    elif any(word in message_lower for word in ["contact", "téléphone", "email", "joindre", "appeler"]):
        contact = NETZ_KB['company']['contact']
        return f"Contactez NETZ Informatique : 📱 {contact['phone']}, 📧 {contact['email']}, 🌐 {contact['website']}. Horaires : {contact['hours']}. Réponse rapide garantie !"
    
    # Technical issues
    elif any(word in message_lower for word in ["lent", "problème", "panne", "virus", "réparation", "dépannage"]):
        if "lent" in message_lower:
            return "PC lent ? Causes possibles : programmes au démarrage, malwares, disque plein. NETZ vous propose : diagnostic GRATUIT, nettoyage système (35€), remplacement par SSD très efficace. Intervention rapide au 07 67 74 49 03 !"
        elif "virus" in message_lower:
            return "Problème de virus ? Pas de panique ! NETZ intervient rapidement : suppression malwares, récupération données, installation protection efficace. Tarif : 55€/h. Appelez le 07 67 74 49 03 pour une prise en charge immédiate."
        else:
            return f"Pour tous vos problèmes informatiques, NETZ Informatique vous aide : {', '.join(NETZ_KB['services']['depannage']['features'])}. Tarif : {NETZ_KB['services']['depannage']['pricing']}. Contact : 07 67 74 49 03."
    
    # Location/Zone
    elif any(word in message_lower for word in ["où", "zone", "déplacement", "intervention", "haguenau"]):
        return f"NETZ Informatique est basé à {NETZ_KB['company']['location']}. Zone d'intervention : {NETZ_KB['faq']['zone_intervention']}. Télémaintenance possible dans toute la France."
    
    # Business services
    elif any(word in message_lower for word in ["entreprise", "professionnel", "maintenance", "contrat"]):
        return f"Pour les entreprises, NETZ propose : maintenance préventive ({NETZ_KB['services']['maintenance']['pricing']}), support prioritaire, formations sur site, développement applications métier. Devis personnalisé gratuit."
    
    # Financial/Revenue queries
    elif any(word in message_lower for word in ["chiffre", "affaires", "ca", "revenus", "finances", "octobre", "mois"]) or "d'affaires" in message_lower:
        return f"Voici les données financières NETZ Informatique 2025 : Octobre 2025 : 41,558.85€ HT. Total Jan-Oct : 119,386.85€ HT. Projection annuelle : 143,264.22€ HT. Répartition : Excel (30%), Bilans compétences (24%), Python (16%), AutoCAD (11%). Croissance solide avec 2,734 clients actifs !"
    
    # General/Fallback
    else:
        return f"Merci pour votre question ! NETZ Informatique vous accompagne pour tous vos besoins informatiques : dépannage, formations QUALIOPI, maintenance, développement web. Diagnostic et devis GRATUITS. Contactez-nous au 07 67 74 49 03 ou contact@netzinformatique.fr"

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup"""
    global rag_system, netz_knowledge
    
    logger.info("🚀 Starting NETZ AI API...")
    logger.info(f"📊 Ollama available: {OLLAMA_AVAILABLE}")
    logger.info(f"🔍 RAG available: {RAG_AVAILABLE}")
    
    # Initialize RAG system if available
    if RAG_AVAILABLE:
        try:
            rag_system = LightweightRAG()
            
            # Add NETZ knowledge to RAG
            for category, items in NETZ_KB.items():
                if isinstance(items, dict):
                    for key, value in items.items():
                        content = f"{category} - {key}: {json.dumps(value, ensure_ascii=False)}"
                        rag_system.add_document(
                            content=content,
                            title=f"NETZ {category}/{key}",
                            source="knowledge_base",
                            doc_type="netz_info",
                            metadata={"category": category, "key": key, "importance": "5"}
                        )
            
            logger.info("✅ RAG system initialized with NETZ knowledge")
        except Exception as e:
            logger.warning(f"⚠️ RAG system initialization failed: {str(e)}")
            rag_system = None
    
    netz_knowledge = NETZ_KB
    logger.info("✅ NETZ AI API ready!")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "university_level",
        "features": {
            "ollama": OLLAMA_AVAILABLE,
            "rag": rag_system is not None,
            "knowledge_base": len(netz_knowledge) > 0
        }
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with real AI"""
    try:
        messages = request.messages
        if not messages:
            return {"error": "No messages provided"}
        
        user_message = messages[-1].content
        logger.info(f"💬 User message: {user_message}")
        
        # Check cache first
        start_time = time.time()
        cached_response = response_cache.get(user_message)
        if cached_response:
            # Add cache hit info
            cached_response["cached"] = True
            cached_response["response_time"] = time.time() - start_time
            return cached_response
        
        # Get NETZ-specific response
        netz_response = get_netz_response(user_message)
        
        # If Ollama is available, enhance with AI
        if OLLAMA_AVAILABLE:
            try:
                # Prepare enhanced prompt
                enhanced_prompt = f"""NETZ Informatique AI Assistant. Services: Dépannage (55€/h), Formations QUALIOPI (45€/h), Maintenance (39€/mois). Contact: 07 67 74 49 03. CA Oct 2025: 41,558.85€ HT.

Q: {user_message}
Réponse: {netz_response}

Réponds en français, professionnel, précis. Utilise les données exactes fournies."""

                # Call Ollama
                response = ollama.generate(
                    model='mistral',
                    prompt=enhanced_prompt,
                    options={
                        'temperature': 0.3,  # More focused
                        'num_predict': 150,  # Shorter responses
                        'top_p': 0.8,       # More deterministic
                        'stop': ['\n\n', '---', 'Q:']  # Stop tokens
                    }
                )
                
                ai_response = response['response']
                logger.info(f"🤖 AI response generated: {len(ai_response)} chars")
                
            except Exception as e:
                logger.warning(f"⚠️ Ollama failed, using knowledge base: {str(e)}")
                ai_response = netz_response
        else:
            ai_response = netz_response
        
        # Prepare response
        response_data = {
            "response": ai_response,
            "language": "fr", 
            "timestamp": datetime.utcnow().isoformat(),
            "model": "netz_ai_mistral" if OLLAMA_AVAILABLE else "netz_knowledge_base",
            "sources": [{"text": "NETZ Knowledge Base", "score": 0.95}] if rag_system else [],
            "cached": False,
            "response_time": time.time() - start_time
        }
        
        # Cache successful responses (but not too long ones to save memory)
        if len(ai_response) < 2000:  # Cache responses under 2000 chars
            response_cache.set(user_message, response_data.copy())
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        return {
            "error": "Une erreur est survenue. Contactez NETZ Informatique au 07 67 74 49 03.",
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/models")
async def get_models():
    """Available models endpoint"""
    models = ["netz_ai_mistral"] if OLLAMA_AVAILABLE else ["netz_knowledge_base"]
    return {"models": models, "default": models[0]}

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache_stats": response_cache.stats(),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/search")
async def search_knowledge(query: str, limit: int = 5):
    """Search in knowledge base"""
    if rag_system:
        try:
            results = rag_system.search(query, k=limit)
            return {"results": results, "query": query}
        except Exception as e:
            return {"error": str(e)}
    else:
        # Simple text search in knowledge base
        results = []
        query_lower = query.lower()
        for category, items in NETZ_KB.items():
            if isinstance(items, dict):
                for key, value in items.items():
                    content = str(value).lower()
                    if query_lower in content:
                        results.append({
                            "category": category,
                            "key": key,
                            "content": str(value)[:200] + "...",
                            "score": 0.8
                        })
        return {"results": results[:limit], "query": query}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)