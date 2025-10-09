from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from rag_service import get_rag_service
import ollama
from pennylane_ingestion import PennyLaneIngestion
from data_scheduler import get_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NETZ AI Assistant API",
    description="Offline AI Assistant for NETZ Informatique with PennyLane Integration",
    version="2.0.0"
)

# Initialize scheduler on startup
@app.on_event("startup")
async def startup_event():
    scheduler = get_scheduler()
    scheduler.start()
    logger.info("Data scheduler initialized")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "mistral"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

class ChatResponse(BaseModel):
    response: str
    model: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    sources: Optional[List[Dict[str, Any]]] = None

class RAGQueryRequest(BaseModel):
    query: str
    use_context: Optional[bool] = True
    model: Optional[str] = "mistral"

class RAGQueryResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict[str, Any]]
    model: str
    timestamp: datetime

@app.get("/")
async def root():
    return {
        "message": "NETZ AI Assistant API",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    # Check service statuses
    services_status = {
        "api": "running",
        "database": "pending",
        "llm": "pending",
        "vector_db": "pending"
    }
    
    # Check Ollama
    try:
        models = ollama.list()
        services_status["llm"] = "running"
    except:
        pass
    
    # Check Qdrant
    try:
        rag = get_rag_service()
        if rag.qdrant_client.get_collections():
            services_status["vector_db"] = "running"
    except:
        pass
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": services_status
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Chat request received with {len(request.messages)} messages")
        
        # Get the last user message
        last_message = request.messages[-1].content if request.messages else ""
        
        # Use RAG to generate response
        rag = get_rag_service()
        result = rag.query(last_message)
        
        return ChatResponse(
            response=result["response"],
            model=result["model"],
            timestamp=datetime.utcnow(),
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        # Fallback to direct Ollama if RAG fails
        try:
            response = ollama.chat(
                model=request.model,
                messages=[{"role": m.role, "content": m.content} for m in request.messages]
            )
            return ChatResponse(
                response=response['message']['content'],
                model=request.model,
                timestamp=datetime.utcnow()
            )
        except Exception as fallback_error:
            logger.error(f"Fallback error: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/query", response_model=RAGQueryResponse)
async def rag_query(request: RAGQueryRequest):
    """Direct RAG query endpoint"""
    try:
        rag = get_rag_service()
        
        if request.use_context:
            result = rag.query(request.query)
        else:
            # Direct LLM query without context
            response = ollama.chat(
                model=request.model,
                messages=[{"role": "user", "content": request.query}]
            )
            result = {
                "query": request.query,
                "response": response['message']['content'],
                "sources": [],
                "model": request.model
            }
        
        return RAGQueryResponse(
            query=result["query"],
            response=result["response"],
            sources=result["sources"],
            model=result["model"],
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_endpoint(query: dict):
    """Vector search endpoint"""
    try:
        rag = get_rag_service()
        if not rag:
            return {"results": [], "error": "RAG service not initialized"}
        
        search_query = query.get("query", "")
        limit = query.get("limit", 5)
        
        # Perform vector search using the RAG service's search method
        results = []
        search_results = rag.vector_store.search(
            collection_name=rag.collection_name,
            query_text=search_query,
            limit=limit
        )
        
        for hit in search_results:
            results.append({
                "text": hit.payload.get("text", ""),
                "metadata": hit.payload.get("metadata", {}),
                "score": hit.score
            })
        
        return {
            "results": results,
            "query": search_query,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return {"results": [], "error": str(e)}

@app.get("/api/models")
async def list_models():
    try:
        # Get models from Ollama
        ollama_models = ollama.list()
        models = []
        
        for model in ollama_models['models']:
            models.append({
                "id": model['name'],
                "name": model['name'],
                "size": f"{model['size'] / (1024**3):.1f}GB",
                "status": "available"
            })
        
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {
            "models": [
                {"id": "mistral", "name": "Mistral 7B", "status": "unknown"},
                {"id": "llama2", "name": "Llama 2 7B", "status": "unknown"},
                {"id": "qwen", "name": "Qwen 2.5", "status": "unknown"}
            ]
        }

@app.post("/api/data/update/{source}")
async def trigger_data_update(source: str):
    """Manually trigger data update for a specific source"""
    try:
        scheduler = get_scheduler()
        scheduler.trigger_update(source)
        return {
            "status": "success",
            "message": f"Update triggered for {source}",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error triggering update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/status")
async def get_data_status():
    """Get status of data sources"""
    try:
        status_file = Path("data/ingestion_status.json")
        update_log_file = Path("data/update_log.json")
        
        status = {}
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = json.load(f)
        
        recent_updates = []
        if update_log_file.exists():
            with open(update_log_file, 'r') as f:
                logs = json.load(f)
                recent_updates = logs[-10:]  # Last 10 updates
        
        return {
            "data_sources": status,
            "recent_updates": recent_updates,
            "scheduler_config": get_scheduler().config
        }
    except Exception as e:
        logger.error(f"Error getting data status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pennylane/search")
async def search_pennylane(query: str, limit: int = 5):
    """Search PennyLane financial data"""
    try:
        pennylane_ingestion = PennyLaneIngestion()
        results = pennylane_ingestion.search_financial_data(query, limit)
        
        return {
            "query": query,
            "results": results,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"PennyLane search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/update/google_drive")
async def update_google_drive():
    """Sync Google Drive documents to RAG"""
    try:
        from google_drive_sync import get_google_drive_sync
        sync = get_google_drive_sync()
        result = sync.sync_to_rag()
        return result
    except Exception as e:
        logger.error(f"Google Drive sync error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/api/data/update/pennylane")
async def update_pennylane():
    """Sync PennyLane financial data"""
    try:
        from pennylane_ingestion import PennyLaneIngestion
        ingestion = PennyLaneIngestion()
        result = await ingestion.ingest_all_data()
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"PennyLane sync error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)