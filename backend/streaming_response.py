"""
Streaming Response Implementation for NETZ AI
Supports Server-Sent Events (SSE) for real-time AI responses
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
import json
import logging
from datetime import datetime
import ollama
from rag_service import get_rag_service

logger = logging.getLogger(__name__)

class StreamingChatService:
    def __init__(self):
        self.active_streams = {}
        
    async def generate_sse_response(
        self, 
        query: str,
        session_id: str,
        model: str = "mistral",
        use_rag: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for streaming responses"""
        
        try:
            # Start event
            yield self._format_sse({
                "type": "start",
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id
            })
            
            # RAG context retrieval
            context_docs = []
            if use_rag:
                try:
                    rag = get_rag_service()
                    context_docs = rag.search_documents(query)
                    
                    # Send context event
                    yield self._format_sse({
                        "type": "context",
                        "sources": [
                            {
                                "text": doc["text"][:200] + "...",
                                "score": doc["score"]
                            } for doc in context_docs[:3]
                        ]
                    })
                except Exception as e:
                    logger.error(f"RAG error: {e}")
                    yield self._format_sse({
                        "type": "warning",
                        "message": "Using direct model without context"
                    })
            
            # Build prompt with context
            prompt = self._build_prompt(query, context_docs)
            
            # Stream from Ollama
            stream = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            # Stream response chunks
            full_response = ""
            chunk_count = 0
            
            for chunk in stream:
                if chunk.get("done"):
                    break
                    
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_response += content
                    chunk_count += 1
                    
                    # Send content chunk
                    yield self._format_sse({
                        "type": "content",
                        "content": content,
                        "chunk_number": chunk_count
                    })
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)
            
            # Send completion event
            yield self._format_sse({
                "type": "complete",
                "total_chunks": chunk_count,
                "response_length": len(full_response),
                "model": model,
                "used_rag": use_rag
            })
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield self._format_sse({
                "type": "error",
                "message": str(e)
            })
    
    def _format_sse(self, data: Dict[str, Any]) -> str:
        """Format data as Server-Sent Event"""
        return f"data: {json.dumps(data)}\n\n"
    
    def _build_prompt(self, query: str, context_docs: list) -> str:
        """Build prompt with RAG context"""
        if not context_docs:
            return query
        
        context = "\n\n".join([
            f"Document {i+1}: {doc['text']}"
            for i, doc in enumerate(context_docs[:3])
        ])
        
        return f"""Contexte de l'entreprise NETZ Informatique:
{context}

Question: {query}

Réponds de manière professionnelle et précise en utilisant le contexte fourni."""

# Singleton instance
_streaming_service = None

def get_streaming_service() -> StreamingChatService:
    global _streaming_service
    if _streaming_service is None:
        _streaming_service = StreamingChatService()
    return _streaming_service

# Extension for existing APIs
def add_streaming_endpoints(app: FastAPI):
    """Add streaming endpoints to existing FastAPI app"""
    
    @app.get("/api/chat/stream")
    async def stream_chat(
        query: str,
        session_id: Optional[str] = None,
        model: str = "mistral",
        use_rag: bool = True
    ):
        """SSE endpoint for streaming chat responses"""
        service = get_streaming_service()
        
        if not session_id:
            session_id = f"stream_{datetime.utcnow().timestamp()}"
        
        return StreamingResponse(
            service.generate_sse_response(query, session_id, model, use_rag),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    @app.post("/api/chat/stream")
    async def stream_chat_post(request: Dict[str, Any]):
        """POST endpoint for streaming with request body"""
        query = request.get("query", "")
        session_id = request.get("session_id")
        model = request.get("model", "mistral")
        use_rag = request.get("use_rag", True)
        
        service = get_streaming_service()
        
        if not session_id:
            session_id = f"stream_{datetime.utcnow().timestamp()}"
        
        return StreamingResponse(
            service.generate_sse_response(query, session_id, model, use_rag),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

# Frontend JavaScript example for consuming SSE
FRONTEND_EXAMPLE = """
// Example: How to consume streaming responses in frontend

class StreamingChat {
    constructor() {
        this.eventSource = null;
    }
    
    async sendMessage(query, onChunk, onComplete) {
        // Close previous connection if exists
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        // Create new SSE connection
        const url = `/api/chat/stream?query=${encodeURIComponent(query)}`;
        this.eventSource = new EventSource(url);
        
        let fullResponse = '';
        
        this.eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'start':
                    console.log('Stream started:', data.session_id);
                    break;
                    
                case 'context':
                    console.log('RAG sources:', data.sources);
                    break;
                    
                case 'content':
                    fullResponse += data.content;
                    onChunk(data.content, fullResponse);
                    break;
                    
                case 'complete':
                    this.eventSource.close();
                    onComplete(fullResponse, data);
                    break;
                    
                case 'error':
                    console.error('Stream error:', data.message);
                    this.eventSource.close();
                    break;
            }
        };
        
        this.eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            this.eventSource.close();
        };
    }
    
    stop() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }
}

// Usage
const chat = new StreamingChat();

chat.sendMessage(
    "Quels sont vos services?",
    (chunk, fullText) => {
        // Update UI with new chunk
        document.getElementById('response').innerHTML = fullText;
    },
    (fullResponse, metadata) => {
        // Handle completion
        console.log('Response complete:', metadata);
    }
);
"""

if __name__ == "__main__":
    print("Streaming Response Module")
    print("=" * 50)
    print("This module provides SSE streaming for AI responses")
    print("\nFeatures:")
    print("- Real-time token streaming")
    print("- RAG context integration")
    print("- Progress indicators")
    print("- Error handling")
    print("\nFrontend Example:")
    print(FRONTEND_EXAMPLE)