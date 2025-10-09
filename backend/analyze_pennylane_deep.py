#!/usr/bin/env python3
"""
Deep analysis of PennyLane data to get accurate financial information
"""

import os
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
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

print("🔍 Deep Analysis of PennyLane Financial Data")
print("="*50)

# Get ALL invoices (not just first 100)
all_invoices = []
print("\n1. Fetching ALL invoices...")

page = 1
while True:
    try:
        params = {
            "page": page,
            "per_page": 100,
            "filter[status]": "finalized"  # Only finalized invoices
        }
        
        response = requests.get(
            f"{BASE_URL}/customer_invoices",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, dict):
                invoices = data.get('invoices', data.get('customer_invoices', []))
            else:
                invoices = data
                
            if invoices:
                all_invoices.extend(invoices)
                print(f"   Page {page}: Found {len(invoices)} invoices")
                
                if len(invoices) < 100:
                    break
                page += 1
            else:
                break
        else:
            print(f"   Error: {response.status_code}")
            break
            
    except Exception as e:
        print(f"   Error: {e}")
        break

print(f"\nTotal invoices fetched: {len(all_invoices)}")

# Analyze by month and year
monthly_data = defaultdict(lambda: {"revenue": 0, "count": 0, "invoices": []})
yearly_data = defaultdict(lambda: {"revenue": 0, "count": 0})

for invoice in all_invoices:
    try:
        # Get date
        date_str = invoice.get('date', invoice.get('issue_date', ''))
        if not date_str:
            continue
            
        invoice_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
        month_key = invoice_date.strftime('%Y-%m')
        year_key = str(invoice_date.year)
        
        # Get amount (handle different field names)
        amount = 0
        for field in ['amount', 'total_amount', 'amount_with_tax', 'amount_without_tax']:
            if field in invoice:
                try:
                    amount = float(invoice[field])
                    break
                except:
                    continue
        
        if amount > 0:
            monthly_data[month_key]["revenue"] += amount
            monthly_data[month_key]["count"] += 1
            monthly_data[month_key]["invoices"].append({
                "number": invoice.get('invoice_number', invoice.get('number', 'N/A')),
                "amount": amount,
                "date": date_str[:10],
                "customer": invoice.get('customer_name', invoice.get('customer', {}).get('name', 'N/A'))
            })
            
            yearly_data[year_key]["revenue"] += amount
            yearly_data[year_key]["count"] += 1
            
    except Exception as e:
        continue

# Print detailed analysis
print("\n2. Financial Analysis by Year:")
print("-" * 40)
for year in sorted(yearly_data.keys()):
    data = yearly_data[year]
    print(f"\nYear {year}:")
    print(f"   Total Revenue: €{data['revenue']:,.2f}")
    print(f"   Total Invoices: {data['count']}")
    print(f"   Average Invoice: €{data['revenue']/max(data['count'], 1):,.2f}")

# Current year monthly breakdown
current_year = str(datetime.now().year)
print(f"\n3. Monthly Breakdown for {current_year}:")
print("-" * 40)

year_months = [k for k in monthly_data.keys() if k.startswith(current_year)]
total_2025 = 0

for month in sorted(year_months):
    data = monthly_data[month]
    total_2025 += data["revenue"]
    month_name = datetime.strptime(month, '%Y-%m').strftime('%B %Y')
    print(f"\n{month_name}:")
    print(f"   Revenue: €{data['revenue']:,.2f}")
    print(f"   Invoices: {data['count']}")
    print(f"   Average: €{data['revenue']/max(data['count'], 1):,.2f}")

print(f"\n{current_year} TOTAL: €{total_2025:,.2f}")

# Current month details
current_month = datetime.now().strftime('%Y-%m')
if current_month in monthly_data:
    print(f"\n4. Current Month ({datetime.now().strftime('%B %Y')}) Details:")
    print("-" * 40)
    
    current_data = monthly_data[current_month]
    print(f"Revenue: €{current_data['revenue']:,.2f}")
    print(f"Invoices: {current_data['count']}")
    
    print("\nLast 10 invoices:")
    for i, inv in enumerate(sorted(current_data['invoices'], 
                                 key=lambda x: x['date'], 
                                 reverse=True)[:10], 1):
        print(f"{i}. {inv['number']} - {inv['customer']}")
        print(f"   €{inv['amount']:,.2f} - {inv['date']}")

# Year-end projection
months_passed = datetime.now().month
if months_passed > 0 and total_2025 > 0:
    monthly_average = total_2025 / months_passed
    projection = monthly_average * 12
    
    print(f"\n5. {current_year} Projections:")
    print("-" * 40)
    print(f"Months completed: {months_passed}")
    print(f"Average monthly revenue: €{monthly_average:,.2f}")
    print(f"Year-end projection: €{projection:,.2f}")

# Save detailed data
output_data = {
    "analysis_date": datetime.now().isoformat(),
    "total_invoices": len(all_invoices),
    "yearly_data": dict(yearly_data),
    "monthly_data": {k: {"revenue": v["revenue"], "count": v["count"]} 
                     for k, v in monthly_data.items()},
    "current_year_total": total_2025,
    "current_month": {
        "month": current_month,
        "revenue": monthly_data[current_month]["revenue"] if current_month in monthly_data else 0,
        "count": monthly_data[current_month]["count"] if current_month in monthly_data else 0
    }
}

with open('pennylane_detailed_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print("\n✅ Analysis saved to: pennylane_detailed_analysis.json")