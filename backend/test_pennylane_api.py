#!/usr/bin/env python3
"""
Test PennyLane API connection and retrieve real data
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("PENNYLANE_API_KEY", "rBJRccXSMapi7yv6nypkInzxU51G-hxSFEacOCTgFZ4")

print("🔍 Testing PennyLane API Connection")
print("="*50)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")

# Different API endpoints to test
api_endpoints = [
    {
        "name": "PennyLane API v1",
        "base_url": "https://app.pennylane.com/api/external/v1",
        "headers": {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }
    },
    {
        "name": "PennyLane API v1 (with X-Api-Key)",
        "base_url": "https://app.pennylane.com/api/external/v1", 
        "headers": {
            "X-Api-Key": API_KEY,
            "Accept": "application/json"
        }
    },
    {
        "name": "PennyLane Public API",
        "base_url": "https://api.pennylane.com/v1",
        "headers": {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }
    }
]

# Test endpoints
test_endpoints = [
    "/me",
    "/company",
    "/customers",
    "/invoices",
    "/customer_invoices",
    "/categories"
]

successful_config = None

# Test each API configuration
for config in api_endpoints:
    print(f"\n\nTesting: {config['name']}")
    print("-" * 40)
    
    for endpoint in test_endpoints:
        url = f"{config['base_url']}{endpoint}"
        
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(
                url, 
                headers=config['headers'],
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Success!")
                data = response.json()
                
                # Show sample data
                if isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())[:5]}")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"Found {len(data)} items")
                    
                successful_config = config
                break
                
            elif response.status_code == 401:
                print("❌ Unauthorized - API key might be invalid")
            elif response.status_code == 404:
                print("❌ Endpoint not found")
            else:
                print(f"❌ Error: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ Timeout")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    if successful_config:
        break

# If we found a working configuration, get more data
if successful_config:
    print("\n\n" + "="*50)
    print("✅ Found working API configuration!")
    print("="*50)
    
    headers = successful_config['headers']
    base_url = successful_config['base_url']
    
    # Get current month data
    current_date = datetime.now()
    start_date = current_date.replace(day=1).strftime("%Y-%m-%d")
    end_date = current_date.strftime("%Y-%m-%d")
    
    print(f"\nRetrieving data for period: {start_date} to {end_date}")
    
    # Try to get invoices
    try:
        print("\n1. Getting invoices...")
        url = f"{base_url}/invoices"
        params = {
            "filter[date_gte]": start_date,
            "filter[date_lte]": end_date,
            "limit": 100
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            invoices = response.json()
            
            # Calculate totals
            if isinstance(invoices, list):
                total_amount = sum(inv.get('amount', 0) for inv in invoices if inv.get('amount'))
                print(f"✅ Found {len(invoices)} invoices")
                print(f"   Total amount: {total_amount:,.2f} EUR")
            else:
                print(f"Response type: {type(invoices)}")
                
    except Exception as e:
        print(f"❌ Error getting invoices: {e}")
    
    # Try to get customers
    try:
        print("\n2. Getting customers...")
        url = f"{base_url}/customers"
        params = {"limit": 100}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            customers = response.json()
            
            if isinstance(customers, list):
                print(f"✅ Found {len(customers)} customers")
                
                # Show first 5 customers
                for i, customer in enumerate(customers[:5]):
                    name = customer.get('name', customer.get('label', 'N/A'))
                    print(f"   {i+1}. {name}")
            else:
                print(f"Response type: {type(customers)}")
                
    except Exception as e:
        print(f"❌ Error getting customers: {e}")
        
else:
    print("\n\n" + "="*50)
    print("❌ Could not connect to PennyLane API")
    print("="*50)
    print("\nPossible issues:")
    print("1. API key might be invalid or expired")
    print("2. API endpoint might have changed")
    print("3. Account might not have API access enabled")
    print("\nPlease check:")
    print("1. Your PennyLane account settings for API access")
    print("2. Generate a new API key if needed")
    print("3. Check PennyLane documentation for current API endpoints")