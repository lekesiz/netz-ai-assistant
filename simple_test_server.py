#!/usr/bin/env python3
"""
Simple test server for NETZ AI browser testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

app = FastAPI(title="NETZ AI Test Server")

# Enable CORS for browser testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "test_mode"
    }

@app.post("/api/chat")
async def chat_endpoint(request_data: dict):
    """Simple chat endpoint for testing"""
    try:
        messages = request_data.get("messages", [])
        if not messages:
            return {"error": "No messages provided"}
        
        user_message = messages[-1].get("content", "")
        
        # Simple response logic for testing
        if "bonjour" in user_message.lower():
            response = "Bonjour ! Je suis l'assistant IA de NETZ Informatique. Comment puis-je vous aider aujourd'hui ?"
        elif "netz" in user_message.lower():
            response = "NETZ Informatique est une entreprise de services informatiques basée à Haguenau. Nous proposons dépannage, formation, maintenance et développement web. Contact: 07 67 74 49 03"
        elif "tarif" in user_message.lower():
            response = "Nos tarifs: Diagnostic GRATUIT, Dépannage 55€/h particuliers, 75€/h entreprises. Formations dès 45€/h. Maintenance dès 39€/mois."
        elif "formation" in user_message.lower():
            response = "NETZ propose des formations certifiées QUALIOPI: Excel, Word, Python, Cybersécurité. Eligible CPF et OPCO. Formations individuelles ou en groupe."
        elif "contact" in user_message.lower():
            response = "Contactez NETZ Informatique: 📱 07 67 74 49 03, 📧 contact@netzinformatique.fr, 🌐 www.netzinformatique.fr. Horaires: Lun-Ven 9h-19h, Sam 10h-17h."
        elif "lent" in user_message.lower():
            response = "PC lent? Causes possibles: programmes au démarrage, malware, disque plein. Solutions: nettoyage système (35€), ajout RAM, remplacement par SSD. Diagnostic gratuit!"
        else:
            response = f"Merci pour votre message: '{user_message}'. NETZ Informatique vous aide avec tous vos besoins informatiques. Contactez-nous au 07 67 74 49 03!"
        
        return {
            "response": response,
            "language": "fr",
            "timestamp": datetime.utcnow().isoformat(),
            "model": "netz_test_model"
        }
        
    except Exception as e:
        return {"error": f"Erreur de traitement: {str(e)}"}

if __name__ == "__main__":
    print("🚀 Starting NETZ AI Test Server...")
    print("📱 Browser test: Open browser-test.html")
    print("🌐 API docs: http://localhost:8000/docs")
    print("❤️  Health: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)