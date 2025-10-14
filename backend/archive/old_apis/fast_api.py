"""
Optimized FastAPI backend for NETZ AI Assistant
Fast response times with demo data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import ollama
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="NETZ AI Assistant API - Fast Version")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
qdrant_client = QdrantClient(url="http://localhost:6333")

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "mistral"
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: datetime
    sources: Optional[List[Dict[str, Any]]] = None

# Cache for embeddings
query_cache = {}

def get_cached_embedding(text: str):
    """Get embedding with caching"""
    if text not in query_cache:
        query_cache[text] = encoder.encode(text)
    return query_cache[text]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "api": "running",
            "llm": "running",
            "vector_db": "running"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Fast chat endpoint with vector search"""
    try:
        # Get the last user message
        user_query = request.messages[-1].content
        logger.info(f"Processing query: {user_query[:50]}...")
        
        # Quick vector search
        sources = []
        try:
            # Get query embedding
            query_vector = get_cached_embedding(user_query)
            
            # Search in vector database
            search_result = qdrant_client.search(
                collection_name="netz_documents",
                query_vector=query_vector.tolist(),
                limit=3
            )
            
            # Extract context from search results
            context_texts = []
            for hit in search_result:
                text = hit.payload.get("text", "")
                if text:
                    context_texts.append(text)
                    sources.append({
                        "text": text[:200] + "...",
                        "metadata": hit.payload.get("metadata", {}),
                        "score": hit.score
                    })
            
            # Build context
            context = "\n\n".join(context_texts[:2])  # Use top 2 results
            
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            context = ""
        
        # Build prompt
        if context:
            system_prompt = f"""Tu es l'assistant AI de NETZ Informatique. Voici des informations pertinentes:

{context}

Utilise ces informations pour répondre de manière précise et professionnelle."""
        else:
            system_prompt = "Tu es l'assistant AI de NETZ Informatique. Réponds de manière professionnelle en français."
        
        # Generate response with Ollama
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        response = ollama.chat(
            model=request.model,
            messages=messages,
            options={
                "temperature": request.temperature,
                "num_predict": 200  # Limit response length for speed
            }
        )
        
        return ChatResponse(
            response=response['message']['content'],
            model=request.model,
            timestamp=datetime.utcnow(),
            sources=sources if sources else None
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        
        # Fallback response
        return ChatResponse(
            response="Désolé, je rencontre un problème technique. Veuillez réessayer.",
            model=request.model,
            timestamp=datetime.utcnow()
        )

@app.get("/api/data/status")
async def data_status():
    """Get data status"""
    try:
        collection = qdrant_client.get_collection("netz_documents")
        return {
            "status": "ready",
            "document_count": collection.points_count,
            "last_update": datetime.utcnow()
        }
    except:
        return {
            "status": "no_data",
            "document_count": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)