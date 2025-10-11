#!/usr/bin/env python3
"""
Test script to verify language detection and response fix
"""

import requests
import json
import time
from typing import Dict, List

# Test configuration
API_URL = "http://localhost:8001"
CHAT_ENDPOINT = f"{API_URL}/api/chat"
TEST_ENDPOINT = f"{API_URL}/api/test-language"

# Test queries in different languages
TEST_QUERIES = {
    "tr": [
        "Merhaba, nasılsın?",
        "NETZ hangi hizmetleri sunuyor?",
        "Python programlama eğitimi var mı?",
        "Excel kursu ne kadar sürüyor?",
        "Müşteri yorumları nasıl?",
    ],
    "fr": [
        "Bonjour, comment allez-vous?",
        "Quels services propose NETZ?",
        "Avez-vous une formation Python?",
        "Combien coûte la formation Excel?",
        "Quels sont vos horaires d'ouverture?",
    ],
    "en": [
        "Hello, how are you?",
        "What services does NETZ offer?",
        "Do you have Python training?",
        "How long is the Excel course?",
        "What are your customer reviews like?",
    ]
}

def test_language_detection(text: str) -> Dict:
    """Test language detection endpoint"""
    try:
        response = requests.post(TEST_ENDPOINT, json={"text": text})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def test_chat_response(text: str) -> Dict:
    """Test chat endpoint with language detection"""
    try:
        response = requests.post(CHAT_ENDPOINT, json={
            "messages": [{"role": "user", "content": text}]
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def detect_response_language(response_text: str) -> str:
    """Simple language detection for response validation"""
    # Common words to detect language
    turkish_indicators = ['ve', 'bir', 'bu', 'için', 'ile', 'olan', 'olarak']
    french_indicators = ['le', 'la', 'les', 'de', 'et', 'est', 'pour', 'avec']
    english_indicators = ['the', 'and', 'is', 'are', 'for', 'with', 'that']
    
    text_lower = response_text.lower()
    
    tr_count = sum(1 for word in turkish_indicators if f' {word} ' in text_lower)
    fr_count = sum(1 for word in french_indicators if f' {word} ' in text_lower)
    en_count = sum(1 for word in english_indicators if f' {word} ' in text_lower)
    
    if tr_count > fr_count and tr_count > en_count:
        return "tr"
    elif fr_count > en_count:
        return "fr"
    else:
        return "en"

def main():
    print("🧪 NETZ AI Language Detection Test")
    print("=" * 50)
    
    # Test 1: Language Detection Accuracy
    print("\n📍 Test 1: Language Detection Accuracy")
    print("-" * 40)
    
    detection_results = []
    for lang, queries in TEST_QUERIES.items():
        for query in queries:
            result = test_language_detection(query)
            is_correct = result.get("detected_language") == lang
            detection_results.append({
                "query": query,
                "expected": lang,
                "detected": result.get("detected_language"),
                "confidence": result.get("confidence", 0),
                "correct": is_correct
            })
            
            status = "✅" if is_correct else "❌"
            print(f"{status} [{lang}] {query[:30]}... -> {result.get('detected_language')} ({result.get('confidence', 0):.2f})")
    
    # Calculate accuracy
    correct_detections = sum(1 for r in detection_results if r["correct"])
    accuracy = (correct_detections / len(detection_results)) * 100
    print(f"\nDetection Accuracy: {accuracy:.1f}% ({correct_detections}/{len(detection_results)})")
    
    # Test 2: Chat Response Language Match
    print("\n📍 Test 2: Chat Response Language Match")
    print("-" * 40)
    
    response_results = []
    for lang, queries in TEST_QUERIES.items():
        for query in queries[:2]:  # Test first 2 queries to save time
            print(f"\nTesting: [{lang}] {query}")
            
            start_time = time.time()
            result = test_chat_response(query)
            response_time = time.time() - start_time
            
            if "response" in result:
                response_text = result["response"]
                response_lang = detect_response_language(response_text)
                model_info = result.get("model_info", {})
                
                is_match = response_lang == lang
                status = "✅" if is_match else "❌"
                
                print(f"  Detected Query Lang: {model_info.get('detected_language', 'unknown')} "
                      f"(confidence: {model_info.get('language_confidence', 0):.2f})")
                print(f"  Response Lang: {response_lang} {status}")
                print(f"  Response Time: {response_time:.1f}s")
                print(f"  Response Preview: {response_text[:100]}...")
                
                response_results.append({
                    "query": query,
                    "expected_lang": lang,
                    "detected_query_lang": model_info.get("detected_language"),
                    "response_lang": response_lang,
                    "match": is_match,
                    "time": response_time
                })
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
    
    # Calculate match rate
    if response_results:
        match_count = sum(1 for r in response_results if r["match"])
        match_rate = (match_count / len(response_results)) * 100
        avg_time = sum(r["time"] for r in response_results) / len(response_results)
        
        print(f"\n📊 Summary:")
        print(f"Language Match Rate: {match_rate:.1f}% ({match_count}/{len(response_results)})")
        print(f"Average Response Time: {avg_time:.1f}s")
    
    # Test 3: Edge Cases
    print("\n📍 Test 3: Edge Cases")
    print("-" * 40)
    
    edge_cases = [
        ("Python nedir?", "tr"),  # Technical term with Turkish
        ("Qu'est-ce que Python?", "fr"),  # Technical term with French
        ("Excel eğitimi kaç saat?", "tr"),  # Mixed technical/Turkish
        ("Formation Excel prix?", "fr"),  # Mixed technical/French
        ("ş ğ ı test", "tr"),  # Turkish characters only
        ("é è ç test", "fr"),  # French characters only
    ]
    
    for text, expected in edge_cases:
        result = test_language_detection(text)
        is_correct = result.get("detected_language") == expected
        status = "✅" if is_correct else "❌"
        print(f"{status} {text} -> Expected: {expected}, Got: {result.get('detected_language')} "
              f"(confidence: {result.get('confidence', 0):.2f})")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
            main()
        else:
            print("❌ API returned status code:", response.status_code)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API at", API_URL)
        print("Please make sure the backend is running: cd backend && python simple_api.py")