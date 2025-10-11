"""
Dynamic Model Selection System for NETZ AI
Automatically selects the best model based on query type and user preferences
"""

import re
import time
import psutil
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType(str, Enum):
    GENERAL = "general"
    CODING = "coding"
    FAST = "fast"
    ACCURATE = "accurate"
    VISION = "vision"

class QueryType(str, Enum):
    CODE = "code"
    TECHNICAL = "technical"
    BUSINESS = "business"
    CASUAL = "casual"
    ANALYSIS = "analysis"
    CREATIVE = "creative"

@dataclass
class ModelProfile:
    """Profile for each available model"""
    name: str
    model_id: str
    size_gb: float
    ram_usage_gb: float
    tokens_per_second: int
    accuracy_score: float  # 0-1
    turkish_support: float  # 0-1
    coding_ability: float  # 0-1
    context_window: int
    strengths: List[str]
    weaknesses: List[str]
    use_cases: List[str]

class DynamicModelSelector:
    """Intelligent model selection based on context and resources"""
    
    def __init__(self):
        # Model profiles based on benchmarks
        self.models = {
            ModelType.GENERAL: ModelProfile(
                name="Mistral 7B",
                model_id="mistral:latest",
                size_gb=4.4,
                ram_usage_gb=8,
                tokens_per_second=120,
                accuracy_score=0.85,
                turkish_support=0.90,
                coding_ability=0.65,
                context_window=32000,
                strengths=["Speed", "Multilingual", "Balanced"],
                weaknesses=["Limited coding", "Math reasoning"],
                use_cases=["General chat", "Customer support", "Translation"]
            ),
            
            ModelType.CODING: ModelProfile(
                name="Qwen 2.5 Coder 32B",
                model_id="qwen2.5-coder:32b",
                size_gb=19,
                ram_usage_gb=24,
                tokens_per_second=40,
                accuracy_score=0.95,
                turkish_support=0.85,
                coding_ability=0.98,
                context_window=128000,
                strengths=["Code generation", "Debugging", "100+ languages"],
                weaknesses=["Slower", "High RAM usage"],
                use_cases=["Programming", "Code review", "Technical documentation"]
            ),
            
            ModelType.FAST: ModelProfile(
                name="Llama 3.2",
                model_id="llama3.2:latest",
                size_gb=2.0,
                ram_usage_gb=4,
                tokens_per_second=150,
                accuracy_score=0.75,
                turkish_support=0.50,
                coding_ability=0.40,
                context_window=16000,
                strengths=["Very fast", "Low resource usage"],
                weaknesses=["Lower accuracy", "Limited Turkish"],
                use_cases=["Quick answers", "Prototyping", "Simple tasks"]
            ),
            
            ModelType.ACCURATE: ModelProfile(
                name="Qwen 2.5 72B",
                model_id="qwen2.5:72b",
                size_gb=47,
                ram_usage_gb=60,
                tokens_per_second=20,
                accuracy_score=0.98,
                turkish_support=0.95,
                coding_ability=0.85,
                context_window=128000,
                strengths=["Highest accuracy", "Complex reasoning", "Research"],
                weaknesses=["Very slow", "Huge RAM usage"],
                use_cases=["Research", "Complex analysis", "Academic work"]
            )
        }
        
        # Query patterns for automatic detection
        self.query_patterns = {
            QueryType.CODE: [
                r'\b(code|kod|python|javascript|sql|api|function|class|debug|error|bug)\b',
                r'\b(nasıl yazılır|how to code|comment coder)\b',
                r'```[a-zA-Z]*\n',  # Code blocks
                r'\b(def|import|return|if|for|while|try|catch)\b'
            ],
            QueryType.TECHNICAL: [
                r'\b(server|database|network|security|güvenlik|réseau|système)\b',
                r'\b(configure|install|setup|kurulum|configuration)\b',
                r'\b(technical|teknik|technique)\b'
            ],
            QueryType.BUSINESS: [
                r'\b(revenue|invoice|customer|müşteri|client|facture)\b',
                r'\b(business|finance|accounting|muhasebe|comptabilité)\b',
                r'\b(report|analysis|rapport|analiz)\b'
            ],
            QueryType.ANALYSIS: [
                r'\b(analyze|analyse|analiz|compare|karşılaştır|comparer)\b',
                r'\b(detailed|détaillé|detaylı|in-depth|derinlemesine)\b',
                r'\b(research|araştırma|recherche)\b'
            ]
        }
        
        # Model switching history for optimization
        self.model_history = []
        self.current_model = ModelType.GENERAL
        self.preloaded_models = set()
        
        # System resource monitoring
        self.max_ram_usage = 0.7  # Use max 70% of available RAM
        self.min_free_ram_gb = 20  # Keep at least 20GB free
        
    def analyze_query(self, query: str) -> Tuple[QueryType, float]:
        """Analyze query to determine its type and confidence"""
        query_lower = query.lower()
        
        scores = {}
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 1
            scores[query_type] = score
        
        # Get the highest scoring type
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = scores[best_type] / len(self.query_patterns[best_type])
            
            # Default to CASUAL if confidence is too low
            if confidence < 0.2:
                return QueryType.CASUAL, 0.5
            
            return best_type, confidence
        
        return QueryType.CASUAL, 0.5
    
    def check_system_resources(self) -> Dict[str, float]:
        """Check current system resource usage"""
        memory = psutil.virtual_memory()
        
        return {
            "total_ram_gb": memory.total / (1024**3),
            "available_ram_gb": memory.available / (1024**3),
            "ram_usage_percent": memory.percent,
            "cpu_percent": psutil.cpu_percent(interval=0.1)
        }
    
    def can_load_model(self, model: ModelProfile) -> bool:
        """Check if system can handle loading a model"""
        resources = self.check_system_resources()
        
        # Check if we have enough RAM
        if resources["available_ram_gb"] < max(model.ram_usage_gb, self.min_free_ram_gb):
            logger.warning(f"Insufficient RAM for {model.name}. Available: {resources['available_ram_gb']:.1f}GB")
            return False
        
        # Check if RAM usage would exceed threshold
        projected_usage = (resources["ram_usage_percent"] + 
                          (model.ram_usage_gb / resources["total_ram_gb"]) * 100)
        
        if projected_usage > self.max_ram_usage * 100:
            logger.warning(f"Loading {model.name} would exceed RAM threshold")
            return False
        
        return True
    
    def select_model(
        self,
        query: str,
        user_preference: Optional[str] = None,
        max_response_time: Optional[float] = None
    ) -> Tuple[str, Dict[str, any]]:
        """Select the best model for the query"""
        
        # 1. Check user preference first
        if user_preference:
            if user_preference in self.models:
                model = self.models[user_preference]
                if self.can_load_model(model):
                    return model.model_id, self._get_model_info(model)
        
        # 2. Analyze query type
        query_type, confidence = self.analyze_query(query)
        logger.info(f"Query type: {query_type} (confidence: {confidence:.2f})")
        
        # 3. Map query type to model type
        model_mapping = {
            QueryType.CODE: ModelType.CODING,
            QueryType.TECHNICAL: ModelType.CODING,
            QueryType.BUSINESS: ModelType.GENERAL,
            QueryType.ANALYSIS: ModelType.ACCURATE,
            QueryType.CREATIVE: ModelType.GENERAL,
            QueryType.CASUAL: ModelType.GENERAL
        }
        
        preferred_model_type = model_mapping.get(query_type, ModelType.GENERAL)
        
        # 4. Check if we need fast response
        if max_response_time and max_response_time < 1.0:
            preferred_model_type = ModelType.FAST
        
        # 5. Get the model and check resources
        model = self.models[preferred_model_type]
        
        # 6. Fallback logic if preferred model can't be loaded
        if not self.can_load_model(model):
            fallback_order = [ModelType.GENERAL, ModelType.FAST]
            for fallback_type in fallback_order:
                fallback_model = self.models[fallback_type]
                if self.can_load_model(fallback_model):
                    logger.info(f"Falling back to {fallback_model.name}")
                    model = fallback_model
                    break
        
        # 7. Update history
        self.model_history.append({
            "timestamp": time.time(),
            "query_type": query_type,
            "model": model.name,
            "query_preview": query[:50]
        })
        
        # Keep only last 100 entries
        if len(self.model_history) > 100:
            self.model_history = self.model_history[-100:]
        
        self.current_model = preferred_model_type
        
        return model.model_id, self._get_model_info(model)
    
    def _get_model_info(self, model: ModelProfile) -> Dict[str, any]:
        """Get detailed model information"""
        return {
            "name": model.name,
            "type": self.current_model,
            "size_gb": model.size_gb,
            "expected_tokens_per_second": model.tokens_per_second,
            "context_window": model.context_window,
            "strengths": model.strengths,
            "turkish_support": f"{model.turkish_support * 100:.0f}%",
            "coding_ability": f"{model.coding_ability * 100:.0f}%",
            "accuracy": f"{model.accuracy_score * 100:.0f}%"
        }
    
    def preload_models(self, model_types: List[ModelType]):
        """Preload models for faster switching"""
        for model_type in model_types:
            if model_type in self.models:
                model = self.models[model_type]
                if self.can_load_model(model):
                    try:
                        logger.info(f"Preloading {model.name}...")
                        ollama.generate(
                            model=model.model_id,
                            prompt="test",
                            keep_alive=300  # Keep in memory for 5 minutes
                        )
                        self.preloaded_models.add(model.model_id)
                    except Exception as e:
                        logger.error(f"Failed to preload {model.name}: {e}")
    
    def get_usage_statistics(self) -> Dict[str, any]:
        """Get model usage statistics"""
        if not self.model_history:
            return {"message": "No usage history yet"}
        
        # Calculate usage by model
        model_usage = {}
        query_types = {}
        
        for entry in self.model_history:
            model = entry["model"]
            query_type = entry["query_type"]
            
            model_usage[model] = model_usage.get(model, 0) + 1
            query_types[query_type] = query_types.get(query_type, 0) + 1
        
        # Get most used model
        most_used_model = max(model_usage, key=model_usage.get)
        most_common_query = max(query_types, key=query_types.get)
        
        return {
            "total_queries": len(self.model_history),
            "model_usage": model_usage,
            "query_types": query_types,
            "most_used_model": most_used_model,
            "most_common_query_type": most_common_query,
            "preloaded_models": list(self.preloaded_models),
            "current_resources": self.check_system_resources()
        }
    
    def recommend_optimal_setup(self) -> Dict[str, any]:
        """Recommend optimal model setup based on system and usage"""
        resources = self.check_system_resources()
        recommendations = []
        
        # Based on available RAM
        if resources["available_ram_gb"] > 80:
            recommendations.append({
                "setup": "High Performance",
                "models": ["mistral:latest", "qwen2.5-coder:32b", "qwen2.5:72b"],
                "description": "All models available for maximum flexibility"
            })
        elif resources["available_ram_gb"] > 40:
            recommendations.append({
                "setup": "Balanced",
                "models": ["mistral:latest", "qwen2.5-coder:32b"],
                "description": "General + Coding models for most use cases"
            })
        else:
            recommendations.append({
                "setup": "Efficient",
                "models": ["mistral:latest", "llama3.2:latest"],
                "description": "Lightweight models for resource conservation"
            })
        
        # Based on usage patterns
        if self.model_history:
            usage_stats = self.get_usage_statistics()
            if usage_stats["query_types"].get(QueryType.CODE, 0) > len(self.model_history) * 0.3:
                recommendations.append({
                    "setup": "Developer Focused",
                    "models": ["qwen2.5-coder:32b", "deepseek-coder-v2:latest"],
                    "description": "Optimized for coding tasks"
                })
        
        return {
            "recommendations": recommendations,
            "current_resources": resources,
            "optimal_preload": ["mistral:latest"]  # Always preload the general model
        }

# Singleton instance
_model_selector = None

def get_model_selector() -> DynamicModelSelector:
    """Get model selector instance"""
    global _model_selector
    if _model_selector is None:
        _model_selector = DynamicModelSelector()
    return _model_selector