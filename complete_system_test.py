#!/usr/bin/env python3
"""
Complete NETZ AI System Test
Tests full integration: Frontend + API + AI + Knowledge Base
"""

import asyncio
import httpx
import json
from datetime import datetime

class NETZSystemTester:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.api_url = "http://localhost:8001"
        self.test_results = []
        
    async def test_component(self, name: str, test_func):
        """Run a test component"""
        print(f"🧪 Testing {name}...")
        try:
            result = await test_func()
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status}: {result['message']}")
            self.test_results.append({
                "component": name,
                "success": result["success"],
                "message": result["message"],
                "details": result.get("details", {})
            })
            return result["success"]
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.test_results.append({
                "component": name,
                "success": False,
                "message": f"Error: {str(e)}",
                "details": {}
            })
            return False
    
    async def test_frontend_health(self):
        """Test frontend accessibility"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.frontend_url, timeout=5)
                if response.status_code == 200 and "NETZ AI" in response.text:
                    return {
                        "success": True,
                        "message": "Frontend accessible and contains NETZ branding",
                        "details": {"status_code": response.status_code}
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Frontend returned {response.status_code}",
                        "details": {"status_code": response.status_code}
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Frontend not accessible: {str(e)}"
                }
    
    async def test_api_health(self):
        """Test API health"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.api_url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    features = health_data.get("features", {})
                    if all([features.get("ollama"), features.get("rag"), features.get("knowledge_base")]):
                        return {
                            "success": True,
                            "message": "API healthy with all features enabled",
                            "details": health_data
                        }
                    else:
                        return {
                            "success": False,
                            "message": "API missing required features",
                            "details": health_data
                        }
                else:
                    return {
                        "success": False,
                        "message": f"API health check failed: {response.status_code}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"API not accessible: {str(e)}"
                }
    
    async def test_ai_chat_basic(self):
        """Test basic AI chat functionality"""
        async with httpx.AsyncClient() as client:
            try:
                chat_request = {
                    "messages": [{"role": "user", "content": "Bonjour"}],
                    "model": "mistral"
                }
                
                response = await client.post(
                    f"{self.api_url}/api/chat",
                    json=chat_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    chat_data = response.json()
                    ai_response = chat_data.get("response", "")
                    
                    # Check if response contains NETZ-specific content
                    netz_indicators = ["NETZ", "Informatique", "Haguenau", "07 67 74 49 03"]
                    found_indicators = [ind for ind in netz_indicators if ind in ai_response]
                    
                    if len(found_indicators) >= 2:
                        return {
                            "success": True,
                            "message": f"AI responds with NETZ context ({len(found_indicators)}/4 indicators)",
                            "details": {
                                "response_length": len(ai_response),
                                "netz_indicators": found_indicators,
                                "model": chat_data.get("model"),
                                "language": chat_data.get("language")
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"AI response lacks NETZ context (only {len(found_indicators)}/4 indicators)",
                            "details": {
                                "response": ai_response[:200] + "...",
                                "found_indicators": found_indicators
                            }
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Chat API failed: {response.status_code}",
                        "details": {"response_text": response.text}
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Chat test failed: {str(e)}"
                }
    
    async def test_ai_chat_netz_knowledge(self):
        """Test AI knowledge about NETZ services"""
        test_questions = [
            {
                "question": "Quels sont vos tarifs?",
                "expected_keywords": ["55€", "75€", "45€", "39€", "gratuit"]
            },
            {
                "question": "Proposez-vous des formations?",
                "expected_keywords": ["QUALIOPI", "formation", "CPF", "Excel", "Python"]
            },
            {
                "question": "Comment vous contacter?",
                "expected_keywords": ["07 67 74 49 03", "contact@netzinformatique.fr", "Haguenau"]
            }
        ]
        
        successful_tests = 0
        total_tests = len(test_questions)
        details = []
        
        async with httpx.AsyncClient() as client:
            for test in test_questions:
                try:
                    chat_request = {
                        "messages": [{"role": "user", "content": test["question"]}]
                    }
                    
                    response = await client.post(
                        f"{self.api_url}/api/chat",
                        json=chat_request,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        chat_data = response.json()
                        ai_response = chat_data.get("response", "").lower()
                        
                        found_keywords = [kw for kw in test["expected_keywords"] if kw.lower() in ai_response]
                        coverage = len(found_keywords) / len(test["expected_keywords"])
                        
                        if coverage >= 0.6:  # 60% keyword coverage
                            successful_tests += 1
                        
                        details.append({
                            "question": test["question"],
                            "coverage": coverage,
                            "found_keywords": found_keywords,
                            "success": coverage >= 0.6
                        })
                    else:
                        details.append({
                            "question": test["question"],
                            "error": f"HTTP {response.status_code}",
                            "success": False
                        })
                        
                except Exception as e:
                    details.append({
                        "question": test["question"],
                        "error": str(e),
                        "success": False
                    })
        
        success_rate = successful_tests / total_tests
        return {
            "success": success_rate >= 0.8,  # 80% success rate required
            "message": f"NETZ Knowledge Test: {successful_tests}/{total_tests} questions answered correctly ({success_rate*100:.0f}%)",
            "details": {
                "success_rate": success_rate,
                "test_details": details
            }
        }
    
    async def test_frontend_api_integration(self):
        """Test if frontend can communicate with API"""
        # This would require browser automation, for now we'll test the API endpoints the frontend uses
        async with httpx.AsyncClient() as client:
            try:
                # Test the exact same call the frontend makes
                frontend_request = {
                    "messages": [{"role": "user", "content": "Test integration"}],
                    "model": "mistral",
                    "temperature": 0.7
                }
                
                response = await client.post(
                    f"{self.api_url}/api/chat",
                    json=frontend_request,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["response", "language", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        return {
                            "success": True,
                            "message": "Frontend-API integration working (all required fields present)",
                            "details": {
                                "response_fields": list(data.keys()),
                                "has_cors": "access-control-allow-origin" in str(response.headers).lower()
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": f"Missing fields for frontend integration: {missing_fields}",
                            "details": {"available_fields": list(data.keys())}
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Integration test failed: HTTP {response.status_code}"
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Integration test error: {str(e)}"
                }
    
    async def run_complete_test(self):
        """Run complete system test"""
        print("🚀 NETZ AI Complete System Test")
        print("="*50)
        
        test_components = [
            ("Frontend Accessibility", self.test_frontend_health),
            ("API Health & Features", self.test_api_health),
            ("AI Chat Basic", self.test_ai_chat_basic),
            ("NETZ Knowledge Base", self.test_ai_chat_netz_knowledge),
            ("Frontend-API Integration", self.test_frontend_api_integration),
        ]
        
        passed_tests = 0
        total_tests = len(test_components)
        
        for component, test_func in test_components:
            success = await self.test_component(component, test_func)
            if success:
                passed_tests += 1
            print()  # Empty line for readability
        
        # Generate summary
        print("="*50)
        print("📊 SYSTEM TEST SUMMARY")
        print("="*50)
        
        success_rate = (passed_tests / total_tests) * 100
        
        if success_rate >= 90:
            status = "🟢 EXCELLENT"
        elif success_rate >= 80:
            status = "🟡 GOOD"  
        elif success_rate >= 60:
            status = "🟠 NEEDS WORK"
        else:
            status = "🔴 CRITICAL ISSUES"
        
        print(f"Overall Status: {status}")
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.0f}%)")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['component']}: {result['message']}")
        
        # System readiness
        print("\n🎯 System Readiness:")
        if success_rate >= 80:
            print("✅ SYSTEM READY FOR PRODUCTION USE")
            print("🌐 Frontend: http://localhost:3000")
            print("🔗 API: http://localhost:8001")
            print("📚 API Docs: http://localhost:8001/docs")
        else:
            print("⚠️  SYSTEM NEEDS FIXES BEFORE PRODUCTION")
        
        return {
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "status": status,
            "details": self.test_results
        }

async def main():
    tester = NETZSystemTester()
    await tester.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())