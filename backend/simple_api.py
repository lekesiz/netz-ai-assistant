"""
Simple API without sentence transformer issues
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import ollama
import json
from pathlib import Path
import logging
import time

logger = logging.getLogger(__name__)

from advanced_prompt_system import AdvancedPromptSystem
from learning_approval_system import get_learning_system
from dynamic_model_selector import get_model_selector, ModelType
from language_detection_system import get_language_detector
from enhanced_knowledge_base import get_enhanced_knowledge_base
from web_search_integration import AIWebSearchIntegration
from pennylane_detailed_sync import PennyLaneDetailedAPI
from performance_optimizer import get_optimization_orchestrator
from lightweight_rag import get_rag_system
import asyncio
from security_middleware import (
    security_headers_middleware, ip_blocking_middleware, 
    request_size_limit_middleware, limiter, RateLimitExceeded,
    _rate_limit_exceeded_handler, verify_api_key_optional,
    security_manager, audit_logger, SecureRequest, sanitize_html
)

app = FastAPI(title="NETZ AI Assistant - Simple API")

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middleware
app.middleware("http")(security_headers_middleware)
app.middleware("http")(ip_blocking_middleware)
app.middleware("http")(request_size_limit_middleware)

# Configure CORS with security
from security_middleware import get_cors_config
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)

class Message(SecureRequest):
    role: str
    content: str
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'Invalid role. Must be one of: {allowed_roles}')
        return v

class ChatRequest(SecureRequest):
    messages: List[Message]
    model: Optional[str] = None
    model_preference: Optional[str] = None  # "fast", "accurate", "coding", "general"
    max_response_time: Optional[float] = None
    enable_web_search: Optional[bool] = False  # Enable internet search
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('Messages cannot be empty')
        if len(v) > 50:
            raise ValueError('Too many messages in conversation')
        return v

class ChatResponse(BaseModel):
    response: str
    model: str
    model_info: Optional[Dict] = None
    timestamp: datetime

class FeedbackRequest(BaseModel):
    session_id: str
    original_query: str
    ai_response: str
    user_feedback: str
    user_id: Optional[str] = "anonymous"

class FeedbackResponse(BaseModel):
    status: str
    message: str
    contribution_id: Optional[str] = None

# Load knowledge base dynamically
def load_knowledge_base():
    """Load knowledge base from file and uploaded documents"""
    # Get enhanced knowledge base
    enhanced_kb = get_enhanced_knowledge_base()
    enhanced_knowledge = enhanced_kb.get_comprehensive_knowledge()
    
    base_knowledge = enhanced_knowledge + """
    
=== INFORMATIONS TEMPS RÉEL ===
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

# Global variables
KNOWLEDGE_BASE = load_knowledge_base()
PROMPT_SYSTEM = AdvancedPromptSystem()
MODEL_SELECTOR = get_model_selector()
LANGUAGE_DETECTOR = get_language_detector()
WEB_SEARCH = AIWebSearchIntegration()
PENNYLANE = PennyLaneDetailedAPI()
OPTIMIZER = get_optimization_orchestrator()
RAG = get_rag_system()

# Track conversation contexts
conversation_contexts = {}

# Preload frequently used models
try:
    MODEL_SELECTOR.preload_models([ModelType.GENERAL])
except Exception as e:
    print(f"Model preloading failed: {e}")

# Initialize RAG with knowledge base
def initialize_rag():
    """Initialize RAG system with existing knowledge"""
    try:
        # Get enhanced knowledge
        enhanced_kb = get_enhanced_knowledge_base()
        knowledge_dict = enhanced_kb.knowledge_categories
        
        # Add to RAG
        added = RAG.add_knowledge_base(knowledge_dict)
        logger.info(f"Added {added} knowledge items to RAG")
        
        # Add PennyLane data if available
        try:
            pennylane_file = Path("pennylane_detailed_data.json")
            if pennylane_file.exists():
                with open(pennylane_file, 'r', encoding='utf-8') as f:
                    pennylane_data = json.load(f)
                    
                # Add financial data to RAG
                if "financial_overview" in pennylane_data:
                    financial = pennylane_data["financial_overview"]["revenue_analysis"]
                    RAG.add_document(
                        content=json.dumps(financial, ensure_ascii=False),
                        title="Financial Overview",
                        source="pennylane",
                        doc_type="financial"
                    )
                    logger.info("Added PennyLane financial data to RAG")
        except Exception as e:
            logger.warning(f"Could not load PennyLane data: {e}")
            
    except Exception as e:
        logger.error(f"RAG initialization failed: {e}")

# Initialize on startup
initialize_rag()

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow(), "mode": "university_level"}

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(request: ChatRequest, req: Request, api_key_data: Optional[Dict] = Depends(verify_api_key_optional)):
    """Chat endpoint with advanced university-level knowledge"""
    try:
        start_time = time.time()
        user_query = request.messages[-1].content
        
        # Security audit logging
        client_ip = req.client.host if req.client else "unknown"
        audit_logger.log_event("chat_request", 
                              api_key_data.get("name", "anonymous") if api_key_data else "anonymous",
                              {"ip": client_ip, "query_length": len(user_query)})
        
        # Check optimization first
        opt_result = await OPTIMIZER.optimize_request(user_query, request.model)
        
        if opt_result.get("cache_hit"):
            # Return cached response
            response_time = time.time() - start_time
            OPTIMIZER.response_optimizer.track_response_time("cached", response_time)
            
            return ChatResponse(
                response=opt_result["response"],
                model="cached",
                model_info={
                    "optimization": "cached",
                    "response_time": response_time,
                    "cache_hit": True
                },
                timestamp=datetime.utcnow()
            )
        
        # Reload knowledge base to get latest updates
        global KNOWLEDGE_BASE
        KNOWLEDGE_BASE = load_knowledge_base()
        
        # Create session context
        session_id = request.messages[0].content[:10]  # Simple session ID
        if session_id not in conversation_contexts:
            conversation_contexts[session_id] = {
                "history": [],
                "user_level": "advanced",
                "language": "auto"
            }
        
        # Detect query type and enhance if needed
        enhanced_query = PROMPT_SYSTEM.enhance_user_query(user_query)
        
        # Get RAG context for the query
        rag_context = ""
        try:
            rag_results = RAG.search(user_query, k=3)
            if rag_results:
                rag_context = "\n\n=== RELEVANT CONTEXT FROM RAG ===\n"
                for result in rag_results:
                    rag_context += f"- {result['content']}\n"
        except Exception as e:
            logger.warning(f"RAG search failed: {e}")
        
        # Build advanced system prompt with RAG context
        base_system_prompt = PROMPT_SYSTEM.build_system_prompt(
            knowledge_base=KNOWLEDGE_BASE + rag_context,
            context={
                "session_id": session_id,
                "query_history": conversation_contexts[session_id]["history"][-5:],  # Last 5 queries
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Enhance with language detection
        system_prompt, detected_lang, lang_confidence = LANGUAGE_DETECTOR.enhance_prompt_with_language(
            base_system_prompt, user_query
        )
        
        # Select optimal model
        model_id, model_info = MODEL_SELECTOR.select_model(
            query=user_query,
            user_preference=request.model_preference,
            max_response_time=request.max_response_time
        )
        
        # Use manually specified model if provided
        if request.model:
            model_id = request.model
            model_info = {"name": request.model, "type": "manual"}
        
        # Generate response with enhanced parameters
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": enhanced_query}
        ]
        
        response = ollama.chat(
            model=model_id,
            messages=messages,
            options={
                "temperature": 0.7,  # Balanced creativity
                "top_p": 0.9,       # Nucleus sampling
                "num_predict": 2048, # Longer responses
                "stop": ["```\n\n", "---\n\n"]  # Natural stopping points
            }
        )
        
        # Enhance with web search if enabled
        final_response = response['message']['content']
        web_search_performed = False
        
        if request.enable_web_search or WEB_SEARCH.should_search_web(user_query):
            try:
                search_result = WEB_SEARCH.enhance_response_with_search(
                    query=user_query,
                    base_response=final_response
                )
                
                if search_result["search_performed"]:
                    final_response = search_result["enhanced_response"]
                    web_search_performed = True
            except Exception as e:
                logger.error(f"Web search failed: {e}")
        
        # Store in context with language info
        conversation_contexts[session_id]["history"].append({
            "query": user_query,
            "response": final_response,
            "detected_language": detected_lang,
            "language_confidence": lang_confidence
        })
        
        # Validate response language
        is_correct_lang, response_lang = LANGUAGE_DETECTOR.validate_response_language(
            response['message']['content'], detected_lang
        )
        
        if not is_correct_lang and lang_confidence > 0.7:
            # Log language mismatch for debugging
            print(f"Language mismatch: Query in {detected_lang}, Response in {response_lang}")
        
        # Cache response if appropriate
        if opt_result.get("should_cache") and opt_result.get("query_hash"):
            OPTIMIZER.cache_response(opt_result["query_hash"], final_response)
        
        # Track performance
        response_time = time.time() - start_time
        OPTIMIZER.response_optimizer.track_response_time(model_id, response_time)
        OPTIMIZER.performance_monitor.record_metric("response_time", response_time)
        
        return ChatResponse(
            response=final_response,
            model=model_id,
            model_info={
                **model_info,
                "detected_language": detected_lang,
                "language_confidence": lang_confidence,
                "web_search_performed": web_search_performed,
                "response_time": response_time,
                "cached": False
            },
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        return ChatResponse(
            response=f"An error occurred: {str(e)}. Please try again with a different query.",
            model=request.model or "mistral:latest",
            model_info={"error": str(e)},
            timestamp=datetime.utcnow()
        )

@app.post("/api/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for potential learning"""
    try:
        learning_system = get_learning_system()
        
        # Check if feedback contains potential new knowledge
        contribution = learning_system.extract_knowledge_from_conversation(
            user_query=request.original_query,
            ai_response=request.ai_response,
            user_feedback=request.user_feedback,
            session_id=request.session_id,
            user_id=request.user_id
        )
        
        if contribution:
            return FeedbackResponse(
                status="success",
                message="Thank you for your feedback! Your contribution has been submitted for review by our team.",
                contribution_id=contribution.id
            )
        else:
            return FeedbackResponse(
                status="noted",
                message="Thank you for your feedback. We've noted your comment.",
                contribution_id=None
            )
            
    except Exception as e:
        return FeedbackResponse(
            status="error",
            message=f"Error processing feedback: {str(e)}",
            contribution_id=None
        )

@app.get("/api/models/available")
async def get_available_models():
    """Get list of available models"""
    try:
        models = []
        for model_type, profile in MODEL_SELECTOR.models.items():
            models.append({
                "type": model_type.value,
                "name": profile.name,
                "model_id": profile.model_id,
                "size_gb": profile.size_gb,
                "turkish_support": f"{profile.turkish_support * 100:.0f}%",
                "coding_ability": f"{profile.coding_ability * 100:.0f}%",
                "speed": profile.tokens_per_second,
                "use_cases": profile.use_cases
            })
        
        return {
            "status": "success",
            "models": models,
            "current_model": MODEL_SELECTOR.current_model.value,
            "preloaded": list(MODEL_SELECTOR.preloaded_models)
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/models/statistics")
async def get_model_statistics():
    """Get model usage statistics"""
    try:
        stats = MODEL_SELECTOR.get_usage_statistics()
        recommendations = MODEL_SELECTOR.recommend_optimal_setup()
        
        return {
            "status": "success",
            "statistics": stats,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/models/preload")
async def preload_models(model_types: List[str]):
    """Preload specific models for faster response"""
    try:
        # Convert strings to ModelType enums
        types_to_load = []
        for model_str in model_types:
            try:
                model_type = ModelType(model_str)
                types_to_load.append(model_type)
            except ValueError:
                continue
        
        MODEL_SELECTOR.preload_models(types_to_load)
        
        return {
            "status": "success",
            "preloaded": list(MODEL_SELECTOR.preloaded_models),
            "message": f"Preloaded {len(types_to_load)} models"
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/financial-data/refresh")
async def refresh_financial_data():
    """Refresh financial data from PennyLane"""
    try:
        if PENNYLANE.test_connection():
            data = PENNYLANE.save_detailed_data()
            
            # Reload knowledge base to include new data
            global KNOWLEDGE_BASE
            KNOWLEDGE_BASE = load_knowledge_base()
            
            return {
                "status": "success",
                "message": "Financial data refreshed",
                "summary": {
                    "total_revenue": data["financial_overview"]["revenue_analysis"]["summary"]["total_revenue"],
                    "invoice_count": data["financial_overview"]["revenue_analysis"]["summary"]["invoice_count"],
                    "last_updated": data["last_updated"]
                }
            }
        else:
            return {"status": "error", "message": "PennyLane connection failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/learning-status")
async def get_learning_status():
    """Get current learning system status"""
    try:
        learning_system = get_learning_system()
        
        # Get counts without admin token (public stats)
        pending_count = len(learning_system.pending_contributions)
        approved_count = len(learning_system.approved_knowledge)
        
        return {
            "status": "active",
            "knowledge_base_size": len(KNOWLEDGE_BASE),
            "pending_contributions": pending_count,
            "approved_contributions": approved_count,
            "learning_enabled": True,
            "languages_supported": ["en", "fr", "tr"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "learning_enabled": False
        }

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint for real-time responses"""
    async def generate():
        try:
            user_query = request.messages[-1].content
            
            # Reload knowledge base
            global KNOWLEDGE_BASE
            KNOWLEDGE_BASE = load_knowledge_base()
            
            # Create session context
            session_id = request.messages[0].content[:10]
            if session_id not in conversation_contexts:
                conversation_contexts[session_id] = {
                    "history": [],
                    "user_level": "advanced",
                    "language": "auto"
                }
            
            # Detect language and enhance prompt
            enhanced_query = PROMPT_SYSTEM.enhance_user_query(user_query)
            base_system_prompt = PROMPT_SYSTEM.build_system_prompt(
                knowledge_base=KNOWLEDGE_BASE,
                context={
                    "session_id": session_id,
                    "query_history": conversation_contexts[session_id]["history"][-5:],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            system_prompt, detected_lang, lang_confidence = LANGUAGE_DETECTOR.enhance_prompt_with_language(
                base_system_prompt, user_query
            )
            
            # Select model
            model_id, model_info = MODEL_SELECTOR.select_model(
                query=user_query,
                user_preference=request.model_preference,
                max_response_time=request.max_response_time
            )
            
            if request.model:
                model_id = request.model
            
            # Stream response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_query}
            ]
            
            # Send initial metadata
            yield f"data: {json.dumps({'type': 'metadata', 'model': model_id, 'detected_language': detected_lang, 'confidence': lang_confidence})}\n\n"
            
            # Stream the response
            stream = ollama.chat(
                model=model_id,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            )
            
            full_response = ""
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_response += content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            # Store in context
            conversation_contexts[session_id]["history"].append({
                "query": user_query,
                "response": full_response,
                "detected_language": detected_lang,
                "language_confidence": lang_confidence
            })
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.post("/api/test-language")
async def test_language_detection(request: Dict[str, Any]):
    """Test language detection for debugging"""
    try:
        text = request.get("text", "")
        detected_lang, confidence = LANGUAGE_DETECTOR.detect_language(text)
        
        # Get test phrases for comparison
        test_phrases = LANGUAGE_DETECTOR.get_test_phrases()
        
        return {
            "input_text": text,
            "detected_language": detected_lang,
            "confidence": confidence,
            "language_name": LANGUAGE_DETECTOR._get_language_name(detected_lang),
            "test_phrases": test_phrases
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "detected_language": "unknown",
            "confidence": 0
        }

@app.get("/api/performance/stats")
async def get_performance_stats():
    """Get comprehensive performance statistics"""
    try:
        stats = OPTIMIZER.get_optimization_stats()
        
        # Add current system info
        stats["system"] = {
            "active_conversations": len(conversation_contexts),
            "knowledge_base_size": len(KNOWLEDGE_BASE),
            "models_available": len(MODEL_SELECTOR.models)
        }
        
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/performance/optimize")
async def optimize_system(settings: Dict[str, Any]):
    """Adjust performance optimization settings"""
    try:
        # Preload specific models
        if "preload_models" in settings:
            models = settings["preload_models"]
            results = await OPTIMIZER.model_preloader.preload_all_models(models)
            return {
                "status": "success",
                "preload_results": results,
                "message": f"Preloaded {sum(results.values())} models successfully"
            }
        
        # Adjust cache settings
        if "cache_ttl" in settings:
            OPTIMIZER.cache.default_ttl = settings["cache_ttl"]
        
        if "cache_max_size" in settings:
            OPTIMIZER.cache.max_size = settings["cache_max_size"]
        
        return {
            "status": "success",
            "message": "Optimization settings updated",
            "current_settings": {
                "cache_ttl": OPTIMIZER.cache.default_ttl,
                "cache_max_size": OPTIMIZER.cache.max_size,
                "preloaded_models": list(OPTIMIZER.model_preloader.preloaded_models)
            }
        }
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/rag/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        stats = RAG.get_stats()
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/rag/add-document")
async def add_document_to_rag(request: Dict[str, Any]):
    """Add a document to RAG"""
    try:
        doc_id = RAG.add_document(
            content=request["content"],
            title=request.get("title", ""),
            source=request.get("source", "user"),
            doc_type=request.get("doc_type", "text"),
            metadata=request.get("metadata", {})
        )
        
        return {
            "status": "success",
            "document_id": doc_id,
            "message": "Document added to RAG"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/rag/search")
async def search_rag(request: Dict[str, Any]):
    """Search RAG for relevant documents"""
    try:
        results = RAG.search(
            query=request["query"],
            k=request.get("k", 5),
            filter_type=request.get("filter_type")
        )
        
        return {
            "status": "success",
            "query": request["query"],
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/rag/rebuild")
async def rebuild_rag_index():
    """Rebuild RAG index with current knowledge"""
    try:
        # Re-initialize RAG
        initialize_rag()
        
        # Get updated stats
        stats = RAG.get_stats()
        
        return {
            "status": "success",
            "message": "RAG index rebuilt",
            "statistics": stats
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Include security routes
from security_api import include_security_routes
include_security_routes(app)

if __name__ == "__main__":
    import uvicorn
    
    # Generate initial API key for testing
    print("\n🔐 Security Configuration:")
    print("=" * 50)
    demo_key = security_manager.generate_api_key("Demo User", ["read"])
    print(f"Demo API Key: {demo_key}")
    print(f"Admin Login: admin@netzinformatique.fr / changeme123")
    print("=" * 50)
    print("\n⚠️  IMPORTANT: Change admin password in production!")
    print("\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port to avoid conflict