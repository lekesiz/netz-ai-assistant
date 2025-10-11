#!/usr/bin/env python3
"""
Load detailed PennyLane financial data
"""

from pennylane_detailed_sync import PennyLaneDetailedAPI
import json
from pathlib import Path

def load_pennylane_data():
    """Load and save detailed PennyLane data"""
    print("🔄 Loading detailed financial data from PennyLane...")
    
    api = PennyLaneDetailedAPI()
    
    if api.test_connection():
        print("✅ Connected to PennyLane API")
        
        # Get comprehensive financial data
        data = api.save_detailed_data()
        
        # Print summary
        if data["financial_overview"]["revenue_analysis"]["status"] == "success":
            revenue = data["financial_overview"]["revenue_analysis"]["summary"]["total_revenue"]
            invoices = data["financial_overview"]["revenue_analysis"]["summary"]["invoice_count"]
            
            print(f"\n📊 Financial Summary:")
            print(f"Total Revenue: {revenue:,.2f}€")
            print(f"Total Invoices: {invoices}")
            
            # Show top customers
            customers = data["financial_overview"]["revenue_analysis"]["customer_analysis"]
            top_customers = sorted(customers.items(), key=lambda x: x[1]["total_revenue"], reverse=True)[:5]
            
            print(f"\n👥 Top 5 Customers:")
            for customer, info in top_customers:
                print(f"  - {customer}: {info['total_revenue']:,.2f}€ ({info['invoice_count']} invoices)")
            
            # Show top services
            services = data["financial_overview"]["revenue_analysis"]["service_analysis"]
            top_services = sorted(services.items(), key=lambda x: x[1]["total_revenue"], reverse=True)[:5]
            
            print(f"\n💼 Top 5 Services:")
            for service, info in top_services:
                print(f"  - {service}: {info['total_revenue']:,.2f}€ ({info['invoice_count']} invoices)")
            
            print("\n✅ Financial data successfully loaded and saved!")
            return True
    else:
        print("❌ Failed to connect to PennyLane API")
        print("Please check your PENNYLANE_API_KEY environment variable")
        return False

if __name__ == "__main__":
    load_pennylane_data()