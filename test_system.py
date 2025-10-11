#!/usr/bin/env python3
"""
NETZ AI Assistant - System Integration Test
Tests all components are working together
"""

import asyncio
import requests
import json
from datetime import datetime
from colorama import init, Fore, Style
import sys

init(autoreset=True)

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def print_test(name, status, details=""):
    """Print test result with color"""
    if status:
        print(f"{Fore.GREEN}✅ {name}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ {name}{Style.RESET_ALL}")
    if details:
        print(f"   {Fore.YELLOW}{details}{Style.RESET_ALL}")

async def test_frontend():
    """Test frontend availability"""
    try:
        resp = requests.get(FRONTEND_URL, timeout=5)
        print_test("Frontend", resp.status_code == 200, f"Status: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print_test("Frontend", False, str(e))
        return False

async def test_backend_health():
    """Test backend health endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        data = resp.json()
        healthy = data.get('status') == 'healthy'
        print_test("Backend Health", healthy, f"Services: {data.get('services', {})}")
        return healthy
    except Exception as e:
        print_test("Backend Health", False, str(e))
        return False

async def test_chat_api():
    """Test chat functionality"""
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "Bonjour, quelle est la date aujourd'hui?"}
            ],
            "model": "mistral",
            "temperature": 0.7
        }
        
        resp = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        success = resp.status_code == 200
        if success:
            data = resp.json()
            print_test("Chat API", True, f"Response length: {len(data.get('response', ''))}")
        else:
            print_test("Chat API", False, f"Status: {resp.status_code}")
        return success
    except Exception as e:
        print_test("Chat API", False, str(e))
        return False

async def test_data_status():
    """Test data ingestion status"""
    try:
        resp = requests.get(f"{BASE_URL}/api/data/status", timeout=5)
        data = resp.json()
        print_test("Data Status", resp.status_code == 200, f"Sources: {list(data.keys())}")
        return resp.status_code == 200
    except Exception as e:
        print_test("Data Status", False, str(e))
        return False

async def test_vector_search():
    """Test vector search capability"""
    try:
        payload = {
            "query": "informatique",
            "limit": 5
        }
        
        resp = requests.post(
            f"{BASE_URL}/api/search",
            json=payload,
            timeout=10
        )
        
        success = resp.status_code == 200
        if success:
            data = resp.json()
            print_test("Vector Search", True, f"Results: {len(data.get('results', []))}")
        else:
            print_test("Vector Search", False, f"Status: {resp.status_code}")
        return success
    except Exception as e:
        print_test("Vector Search", False, str(e))
        return False

async def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"NETZ AI Assistant - System Integration Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}{Style.RESET_ALL}\n")
    
    tests = [
        test_frontend(),
        test_backend_health(),
        test_chat_api(),
        test_data_status(),
        test_vector_search()
    ]
    
    results = await asyncio.gather(*tests)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print(f"{Fore.GREEN}✨ All systems operational! ✨{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Some tests failed. Check logs for details.{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)