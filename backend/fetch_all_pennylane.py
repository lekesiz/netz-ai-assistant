#!/usr/bin/env python3
"""
Fetch all available data from PennyLane API
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("PENNYLANE_API_KEY", "rBJRccXSMapi7yv6nypkInzxU51G-hxSFEacOCTgFZ4")
BASE_URL = "https://app.pennylane.com/api/external/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

print("📊 Fetching All PennyLane Data")
print("="*50)

# Test different endpoints
endpoints = [
    {"name": "Invoices (v1)", "url": "/invoices"},
    {"name": "Customer Invoices", "url": "/customer_invoices"},
    {"name": "Documents", "url": "/documents"},
    {"name": "Sales", "url": "/sales"},
    {"name": "Revenues", "url": "/revenues"},
]

all_data = {}

for endpoint in endpoints:
    print(f"\nTrying {endpoint['name']} at {endpoint['url']}...")
    
    try:
        # Try without parameters first
        response = requests.get(
            f"{BASE_URL}{endpoint['url']}",
            headers=headers,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Print structure
            if isinstance(data, dict):
                print(f"Response type: dict with keys: {list(data.keys())[:10]}")
                
                # Check for data in different formats
                for key in ['invoices', 'customer_invoices', 'documents', 'data', 'items', 'results']:
                    if key in data and isinstance(data[key], list):
                        print(f"Found {len(data[key])} items in '{key}'")
                        all_data[endpoint['name']] = data[key][:5]  # Save first 5 for analysis
                        break
                        
            elif isinstance(data, list):
                print(f"Response type: list with {len(data)} items")
                all_data[endpoint['name']] = data[:5]
                
            # Try with date filter for 2025
            if response.status_code == 200:
                print("\nTrying with 2025 filter...")
                params = {
                    "filter[date_gte]": "2025-01-01",
                    "filter[date_lte]": "2025-12-31"
                }
                
                response2 = requests.get(
                    f"{BASE_URL}{endpoint['url']}",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                if response2.status_code == 200:
                    data2 = response2.json()
                    if isinstance(data2, list):
                        print(f"2025 filter: Found {len(data2)} items")
                    elif isinstance(data2, dict):
                        for key in ['invoices', 'customer_invoices', 'data']:
                            if key in data2:
                                print(f"2025 filter: Found {len(data2[key])} items in '{key}'")
                                
        elif response.status_code == 400:
            # Try different parameter names
            print("Trying alternative parameters...")
            
            params_list = [
                {"date_from": "2025-01-01", "date_to": "2025-12-31"},
                {"start_date": "2025-01-01", "end_date": "2025-12-31"},
                {"from": "2025-01-01", "to": "2025-12-31"}
            ]
            
            for params in params_list:
                response3 = requests.get(
                    f"{BASE_URL}{endpoint['url']}",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                if response3.status_code == 200:
                    print(f"✅ Success with params: {params}")
                    break
                    
    except Exception as e:
        print(f"Error: {str(e)}")

# Save findings
with open('pennylane_api_analysis.json', 'w') as f:
    json.dump(all_data, f, indent=2)

print("\n" + "="*50)
print("Analysis complete. Check pennylane_api_analysis.json for details.")