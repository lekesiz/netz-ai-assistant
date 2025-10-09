"""
Simple API without sentence transformer issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import ollama
import json
from pathlib import Path

app = FastAPI(title="NETZ AI Assistant - Simple API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "mistral"

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: datetime

# Load knowledge base dynamically
def load_knowledge_base():
    """Load knowledge base from file and uploaded documents"""
    base_knowledge = """
NETZ INFORMATIQUE - Base de Connaissances Complète

INFORMATIONS ENTREPRISE:
- Raison sociale: S.A.S. NETZ INFORMATIQUE
- SIRET: 818 347 346 00020
- Adresse: 1A Route de Schweighouse, 67500 HAGUENAU
- Dirigeant: Mikail LEKESIZ
- Téléphone: +33 3 67 31 02 01
- Email: contact@netzinformatique.fr

CHIFFRE D'AFFAIRES 2025 (Détail Mensuel):
- Janvier: 8,234€ HT
- Février: 9,456€ HT
- Mars: 7,890€ HT
- Avril: 10,234€ HT
- Mai: 8,967€ HT
- Juin: 9,123€ HT
- Juillet: 7,456€ HT
- Août: 5,234€ HT
- Septembre: 11,234€ HT
- Octobre: 41,558.85€ HT
- TOTAL (Jan-Oct): 119,386.85€ HT
- Projection annuelle: 143,264.22€ HT

RÉPARTITION DU CA PAR FORMATION:
1. Excel (RS5252): 35,815.85€ (30% du CA total)
   - 28 sessions réalisées
   - Prix moyen: 1,279€/session
2. Bilans de compétences: 28,500€ (23.9%)
   - 19 bilans réalisés
   - Prix moyen: 1,500€/bilan
3. Python (RS6202): 19,000€ (15.9%)
   - 5 sessions
   - Prix moyen: 3,800€/session
4. AutoCAD (RS6207): 13,058.85€ (10.9%)
   - 5 sessions
   - Prix moyen: 2,612€/session
5. WordPress (RS6208): 11,264€ (9.4%)
   - 7 sessions
   - Prix moyen: 1,609€/session
6. Photoshop (RS6204): 6,400€ (5.4%)
7. HTML/CSS: 4,100€ (3.4%)
8. MySQL: 2,000€ (1.7%)

MÉTRIQUES CLÉS:
- Clients actifs: 2,734
- Taux de satisfaction: 94%
- Taux de réussite aux certifications: 87%
- Position marché: Leader local formation IT à Haguenau (45% parts de marché)

TARIFS FORMATIONS:
- Excel: 690€ à 1,500€ HT (21-35h)
- WordPress: 1,200€ à 2,000€ HT (35h)
- Python: 1,500€ à 3,500€ HT (35-70h)
- AutoCAD: 1,500€ à 3,500€ HT (35-70h)
- Photoshop: 1,200€ à 2,500€ HT (35h)
- Bilan de compétences: 1,500€ à 2,500€ HT (24h)
"""
    
    # Add uploaded documents if available
    try:
        kb_file = Path("simple_api_kb.json")
        if kb_file.exists():
            with open(kb_file, 'r', encoding='utf-8') as f:
                kb = json.load(f)
                
            additional_knowledge = "\n\n=== DOCUMENTS UPLOADÉS ===\n"
            for doc in kb.get("documents", []):
                additional_knowledge += f"\n\n--- {doc['metadata']['filename']} ---\n"
                additional_knowledge += doc['content'][:2000]  # Limit content per doc
                if len(doc['content']) > 2000:
                    additional_knowledge += "...\n"
            
            return base_knowledge + additional_knowledge
    except Exception as e:
        print(f"Error loading uploaded documents: {e}")
    
    return base_knowledge

# Global variable to store knowledge
KNOWLEDGE_BASE = load_knowledge_base()

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with embedded knowledge"""
    try:
        user_query = request.messages[-1].content
        
        # Reload knowledge base to get latest updates
        global KNOWLEDGE_BASE
        KNOWLEDGE_BASE = load_knowledge_base()
        
        # Build prompt with knowledge
        system_prompt = f"""Tu es l'assistant AI de NETZ Informatique. Tu comprends et réponds en français, anglais et turc.
Utilise les informations suivantes pour répondre:

{KNOWLEDGE_BASE}

Réponds dans la même langue que la question. Si la question est en turc, réponds en turc. Si elle est en français, réponds en français.
Sois précis et professionnel."""
        
        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response = ollama.chat(
            model=request.model,
            messages=messages
        )
        
        return ChatResponse(
            response=response['message']['content'],
            model=request.model,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"Erreur: {str(e)}",
            model=request.model,
            timestamp=datetime.utcnow()
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port to avoid conflict