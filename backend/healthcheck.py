#!/usr/bin/env python3
"""
Health check script for NETZ AI API
"""
import sys
import requests
import time

def health_check():
    try:
        # Check API health endpoint
        response = requests.get('http://localhost:8001/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify essential features
            features = data.get('features', {})
            required_features = ['ollama', 'knowledge_base']
            
            for feature in required_features:
                if not features.get(feature):
                    print(f"❌ Feature {feature} not available")
                    return False
            
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = health_check()
    sys.exit(0 if success else 1)