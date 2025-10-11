"""
Web Search Integration for Real-Time Information
Supports multiple search providers with fallback options
"""

import os
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchEngine:
    """Multi-provider web search integration"""
    
    def __init__(self):
        # Search provider APIs (in order of preference)
        self.providers = {
            "serper": {
                "api_key": os.getenv("SERPER_API_KEY", ""),
                "base_url": "https://google.serper.dev/search",
                "enabled": bool(os.getenv("SERPER_API_KEY"))
            },
            "brave": {
                "api_key": os.getenv("BRAVE_SEARCH_API_KEY", ""),
                "base_url": "https://api.search.brave.com/res/v1/web/search",
                "enabled": bool(os.getenv("BRAVE_SEARCH_API_KEY"))
            },
            "duckduckgo": {
                "api_key": None,  # No API key required
                "base_url": "https://api.duckduckgo.com",
                "enabled": True  # Always available
            }
        }
        
    def search(self, query: str, num_results: int = 5, search_type: str = "general") -> Dict:
        """
        Perform web search with fallback providers
        
        Args:
            query: Search query
            num_results: Number of results to return
            search_type: Type of search (general, news, academic, local)
            
        Returns:
            Search results with sources and summaries
        """
        
        # Try each provider in order
        for provider_name, provider_config in self.providers.items():
            if provider_config["enabled"]:
                try:
                    if provider_name == "serper":
                        return self._search_serper(query, num_results, search_type)
                    elif provider_name == "brave":
                        return self._search_brave(query, num_results, search_type)
                    elif provider_name == "duckduckgo":
                        return self._search_duckduckgo(query, num_results)
                except Exception as e:
                    logger.error(f"Search failed with {provider_name}: {e}")
                    continue
        
        # If all providers fail, return empty results
        return {
            "status": "error",
            "message": "All search providers failed",
            "query": query,
            "results": []
        }
    
    def _search_serper(self, query: str, num_results: int, search_type: str) -> Dict:
        """Search using Serper API (Google results)"""
        headers = {
            "X-API-KEY": self.providers["serper"]["api_key"],
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results,
            "hl": "fr"  # Default to French for NETZ
        }
        
        # Adjust for search type
        if search_type == "news":
            payload["type"] = "news"
        elif search_type == "academic":
            payload["type"] = "scholar"
        
        response = requests.post(
            self.providers["serper"]["base_url"],
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "date": item.get("date"),
                    "source": "Serper (Google)"
                })
            
            return {
                "status": "success",
                "query": query,
                "search_type": search_type,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        
        raise Exception(f"Serper API error: {response.status_code}")
    
    def _search_brave(self, query: str, num_results: int, search_type: str) -> Dict:
        """Search using Brave Search API"""
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.providers["brave"]["api_key"]
        }
        
        params = {
            "q": query,
            "count": num_results,
            "text_decorations": False
        }
        
        if search_type == "news":
            params["news"] = True
        
        response = requests.get(
            self.providers["brave"]["base_url"],
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "date": item.get("age"),
                    "source": "Brave Search"
                })
            
            return {
                "status": "success",
                "query": query,
                "search_type": search_type,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        
        raise Exception(f"Brave API error: {response.status_code}")
    
    def _search_duckduckgo(self, query: str, num_results: int) -> Dict:
        """Search using DuckDuckGo (no API key required)"""
        # Using DuckDuckGo Instant Answer API
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        
        response = requests.get(
            f"{self.providers['duckduckgo']['base_url']}",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            
            # Try to get results from different sections
            if data.get("AbstractURL"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", ""),
                    "source": "DuckDuckGo"
                })
            
            # Add related topics
            for topic in data.get("RelatedTopics", [])[:num_results-1]:
                if isinstance(topic, dict) and topic.get("FirstURL"):
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", ""),
                        "source": "DuckDuckGo"
                    })
            
            # Fallback: search using HTML scraping (less reliable)
            if not results:
                results = self._duckduckgo_html_search(query, num_results)
            
            return {
                "status": "success",
                "query": query,
                "search_type": "general",
                "results": results[:num_results],
                "timestamp": datetime.now().isoformat()
            }
        
        raise Exception(f"DuckDuckGo API error: {response.status_code}")
    
    def _duckduckgo_html_search(self, query: str, num_results: int) -> List[Dict]:
        """Fallback HTML search for DuckDuckGo"""
        # This is a simplified version - in production, use a proper HTML parser
        results = []
        
        # Add a mock result to indicate search was attempted
        results.append({
            "title": f"Search results for: {query}",
            "url": f"https://duckduckgo.com/?q={quote(query)}",
            "snippet": "Please visit DuckDuckGo to see full results. API limitations prevent detailed results.",
            "source": "DuckDuckGo (Limited)"
        })
        
        return results
    
    def search_with_context(self, query: str, context: str = "", search_type: str = "general") -> Dict:
        """
        Search with additional context for better results
        
        Args:
            query: Main search query
            context: Additional context (e.g., "NETZ Informatique Haguenau")
            search_type: Type of search
            
        Returns:
            Contextualized search results
        """
        
        # Enhance query with context
        if context:
            enhanced_query = f"{query} {context}"
        else:
            enhanced_query = query
        
        # Perform search
        results = self.search(enhanced_query, num_results=5, search_type=search_type)
        
        # Add relevance scoring based on context
        if results["status"] == "success" and context:
            for result in results["results"]:
                # Simple relevance scoring
                relevance_score = 0
                text = (result["title"] + " " + result["snippet"]).lower()
                
                for term in context.lower().split():
                    if term in text:
                        relevance_score += 1
                
                result["relevance_score"] = relevance_score
            
            # Sort by relevance
            results["results"].sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return results
    
    def search_financial_news(self, company: str = "NETZ Informatique") -> Dict:
        """Search for financial news about a company"""
        query = f"{company} financial results news"
        return self.search(query, num_results=5, search_type="news")
    
    def search_industry_trends(self, industry: str = "IT training France") -> Dict:
        """Search for industry trends and analysis"""
        query = f"{industry} trends analysis 2025"
        return self.search(query, num_results=5, search_type="general")
    
    def search_competitor_info(self, market: str = "formation informatique Alsace") -> Dict:
        """Search for competitor information"""
        query = f"{market} competitors market share"
        return self.search(query, num_results=5, search_type="general")
    
    def format_results_for_ai(self, search_results: Dict) -> str:
        """Format search results for AI consumption"""
        if search_results["status"] != "success":
            return f"Search failed: {search_results.get('message', 'Unknown error')}"
        
        formatted = f"Search Results for: {search_results['query']}\n"
        formatted += f"Search Type: {search_results.get('search_type', 'general')}\n"
        formatted += f"Timestamp: {search_results['timestamp']}\n\n"
        
        for i, result in enumerate(search_results["results"], 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   Summary: {result['snippet']}\n"
            if result.get('date'):
                formatted += f"   Date: {result['date']}\n"
            formatted += f"   Source: {result['source']}\n\n"
        
        return formatted


class AIWebSearchIntegration:
    """Integration layer between AI and web search"""
    
    def __init__(self):
        self.search_engine = WebSearchEngine()
        self.search_history = []
    
    def should_search_web(self, query: str) -> bool:
        """Determine if web search would be helpful for the query"""
        
        # Keywords that indicate web search would be useful
        search_indicators = [
            "actualité", "news", "récent", "recent", "aujourd'hui", "today",
            "2025", "2024", "dernière", "latest", "current", "actuel",
            "marché", "market", "concurrent", "competitor", "tendance", "trend",
            "prix actuel", "current price", "mise à jour", "update",
            "qui est", "who is", "qu'est-ce que", "what is"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in search_indicators)
    
    def enhance_response_with_search(self, query: str, base_response: str) -> Dict:
        """Enhance AI response with web search results"""
        
        # Check if search would be beneficial
        if not self.should_search_web(query):
            return {
                "enhanced_response": base_response,
                "search_performed": False
            }
        
        # Perform contextual search
        search_results = self.search_engine.search_with_context(
            query=query,
            context="NETZ Informatique Haguenau formation IT",
            search_type="general"
        )
        
        # Format results
        if search_results["status"] == "success" and search_results["results"]:
            search_summary = self.search_engine.format_results_for_ai(search_results)
            
            enhanced_response = f"{base_response}\n\n"
            enhanced_response += "📌 Informations complémentaires trouvées sur internet:\n\n"
            enhanced_response += search_summary
            
            # Save search history
            self.search_history.append({
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "results_count": len(search_results["results"])
            })
            
            return {
                "enhanced_response": enhanced_response,
                "search_performed": True,
                "search_results": search_results
            }
        
        return {
            "enhanced_response": base_response,
            "search_performed": False
        }


# Example usage
if __name__ == "__main__":
    # Test search functionality
    search = WebSearchEngine()
    
    # Test general search
    results = search.search("NETZ Informatique Haguenau")
    print("General Search Results:")
    print(search.format_results_for_ai(results))
    
    # Test financial news
    news = search.search_financial_news()
    print("\nFinancial News:")
    print(search.format_results_for_ai(news))
    
    # Test with AI integration
    ai_search = AIWebSearchIntegration()
    test_query = "Quelles sont les dernières actualités sur la formation IT en France?"
    
    if ai_search.should_search_web(test_query):
        print(f"\n✅ Web search recommended for: {test_query}")
    else:
        print(f"\n❌ Web search not needed for: {test_query}")