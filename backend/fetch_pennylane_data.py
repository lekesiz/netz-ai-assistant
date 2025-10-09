#!/usr/bin/env python3
"""
Fetch real financial data from PennyLane API
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("PENNYLANE_API_KEY", "rBJRccXSMapi7yv6nypkInzxU51G-hxSFEacOCTgFZ4")
BASE_URL = "https://app.pennylane.com/api/external/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

print("📊 Fetching Real Financial Data from PennyLane")
print("="*50)

# Get company info
try:
    print("\n1. Company Information:")
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        company_data = data.get('company', {})
        user_data = data.get('user', {})
        
        print(f"✅ Company: {company_data.get('name', 'N/A')}")
        print(f"   User: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        
        # Store company info
        company_info = {
            "name": company_data.get('name'),
            "user": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}",
            "email": user_data.get('email')
        }
except Exception as e:
    print(f"❌ Error: {e}")
    company_info = {}

# Get all customer invoices
all_invoices = []
try:
    print("\n2. Fetching Customer Invoices...")
    
    # Try different endpoints
    endpoints_to_try = [
        "/customer_invoices",
        "/invoices", 
        "/documents?filter[type]=customer_invoice"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"   Trying {endpoint}...")
        
        page = 1
        while True:
            params = {
                "page": page,
                "per_page": 100
            }
            
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict):
                    invoices = data.get('invoices', data.get('customer_invoices', data.get('data', [])))
                    if not invoices and 'values' in data:
                        invoices = data['values']
                else:
                    invoices = data
                
                if invoices:
                    all_invoices.extend(invoices)
                    print(f"   ✅ Page {page}: Found {len(invoices)} invoices")
                    
                    # Check if there are more pages
                    if len(invoices) < 100:
                        break
                    page += 1
                else:
                    break
                    
                if all_invoices:
                    break  # Found invoices, stop trying other endpoints
            else:
                print(f"   ❌ Status: {response.status_code}")
                break
                
        if all_invoices:
            break
            
    print(f"\n   Total invoices found: {len(all_invoices)}")
    
except Exception as e:
    print(f"❌ Error fetching invoices: {e}")

# Get customers
all_customers = []
try:
    print("\n3. Fetching Customers...")
    
    page = 1
    while True:
        params = {
            "page": page,
            "per_page": 100
        }
        
        response = requests.get(
            f"{BASE_URL}/customers",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                customers = data.get('customers', data.get('data', []))
            else:
                customers = data
                
            if customers:
                all_customers.extend(customers)
                print(f"   ✅ Page {page}: Found {len(customers)} customers")
                
                if len(customers) < 100:
                    break
                page += 1
            else:
                break
        else:
            print(f"   ❌ Status: {response.status_code}")
            break
            
    print(f"\n   Total customers found: {len(all_customers)}")
    
except Exception as e:
    print(f"❌ Error fetching customers: {e}")

# Calculate financial statistics
print("\n4. Financial Analysis:")

# Current month statistics
current_date = datetime.now()
current_month_start = current_date.replace(day=1)

monthly_revenue = 0
monthly_invoices = 0
current_year_revenue = 0

for invoice in all_invoices:
    try:
        # Get invoice date
        invoice_date_str = invoice.get('date', invoice.get('issue_date', ''))
        if invoice_date_str:
            invoice_date = datetime.strptime(invoice_date_str[:10], '%Y-%m-%d')
            
            # Get amount
            amount = float(invoice.get('amount', invoice.get('total_amount', invoice.get('amount_with_tax', 0))))
            
            # Current month
            if invoice_date >= current_month_start:
                monthly_revenue += amount
                monthly_invoices += 1
            
            # Current year
            if invoice_date.year == current_date.year:
                current_year_revenue += amount
                
    except Exception as e:
        continue

print(f"\nCurrent Month ({current_date.strftime('%B %Y')}):")
print(f"   Revenue: €{monthly_revenue:,.2f}")
print(f"   Invoices: {monthly_invoices}")
print(f"\nYear {current_date.year} Total:")
print(f"   Revenue: €{current_year_revenue:,.2f}")

# Customer analysis
active_customers = len(all_customers)
print(f"\nCustomer Statistics:")
print(f"   Total active customers: {active_customers}")

# Save data for import
financial_data = {
    "company": company_info,
    "summary": {
        "monthly_revenue": monthly_revenue,
        "monthly_invoices": monthly_invoices,
        "yearly_revenue": current_year_revenue,
        "active_customers": active_customers,
        "total_invoices": len(all_invoices)
    },
    "invoices": all_invoices[:10],  # First 10 for reference
    "customers": all_customers[:10],  # First 10 for reference
    "last_updated": datetime.now().isoformat()
}

# Save to file
output_file = "pennylane_data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(financial_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Data saved to: {output_file}")
print("\nNow run: python load_pennylane_to_rag.py")