import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import ollama
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    qdrant_url: str = "localhost:6333"
    collection_name: str = "netz_documents"
    model_name: str = "mistral"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    top_k: int = 5
    temperature: float = 0.7

class RAGService:
    def __init__(self, config: RAGConfig = RAGConfig()):
        self.config = config
        self.qdrant_client = QdrantClient(url=config.qdrant_url)
        self.encoder = SentenceTransformer(config.embedding_model)
        
    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Search for relevant documents using vector similarity"""
        try:
            # Generate query embedding
            query_vector = self.encoder.encode(query).tolist()
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.config.collection_name,
                query_vector=query_vector,
                limit=self.config.top_k
            )
            
            # Format results
            documents = []
            for hit in search_results:
                documents.append({
                    "text": hit.payload.get("text", ""),
                    "metadata": hit.payload.get("metadata", {}),
                    "score": hit.score
                })
            
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate response using LLM with retrieved context"""
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}: {doc['text']}" 
            for i, doc in enumerate(context_docs)
        ])
        
        # Create prompt
        prompt = f"""Tu es l'assistant AI de NETZ Informatique. Utilise le contexte suivant pour répondre à la question de manière précise et professionnelle.

Contexte:
{context}

Question: {query}

Réponse:"""
        
        try:
            # Generate response using Ollama
            response = ollama.chat(
                model=self.config.model_name,
                messages=[
                    {"role": "system", "content": "Tu es un assistant professionnel pour NETZ Informatique. Réponds en français de manière claire et concise."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Désolé, je n'ai pas pu générer une réponse. Veuillez réessayer."
    
    def query(self, user_query: str) -> Dict[str, Any]:
        """Main RAG pipeline: search + generate"""
        # Search for relevant documents
        documents = self.search_documents(user_query)
        
        # Generate response
        response = self.generate_response(user_query, documents)
        
        return {
            "query": user_query,
            "response": response,
            "sources": documents,
            "model": self.config.model_name
        }

# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service