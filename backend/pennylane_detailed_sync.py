"""
Enhanced PennyLane Integration for Detailed Accounting Data
"""

import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PennyLaneDetailedAPI:
    """Enhanced PennyLane API client with comprehensive data retrieval"""
    
    def __init__(self):
        self.api_key = os.getenv('PENNYLANE_API_KEY', '')
        self.company_id = os.getenv('PENNYLANE_COMPANY_ID', '22052053')
        self.base_url = "https://app.pennylane.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/companies/{self.company_id}",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_detailed_invoices(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get detailed invoice data with line items"""
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # Get all invoices
            response = requests.get(
                f"{self.base_url}/companies/{self.company_id}/customer_invoices",
                headers=self.headers,
                params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "include": "line_items,customer,payments"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                invoices = response.json().get('data', [])
                
                # Process and analyze invoices
                analysis = self._analyze_invoices(invoices)
                
                return {
                    "status": "success",
                    "period": {"start": start_date, "end": end_date},
                    "summary": analysis["summary"],
                    "monthly_breakdown": analysis["monthly"],
                    "customer_analysis": analysis["customers"],
                    "service_analysis": analysis["services"],
                    "payment_analysis": analysis["payments"],
                    "trends": analysis["trends"],
                    "raw_count": len(invoices)
                }
            else:
                return {"status": "error", "message": f"API Error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Failed to fetch detailed invoices: {e}")
            return {"status": "error", "message": str(e)}
    
    def _analyze_invoices(self, invoices: List[Dict]) -> Dict:
        """Analyze invoice data in detail"""
        analysis = {
            "summary": {
                "total_revenue": 0,
                "total_tax": 0,
                "invoice_count": len(invoices),
                "paid_count": 0,
                "pending_count": 0,
                "average_invoice": 0
            },
            "monthly": {},
            "customers": {},
            "services": {},
            "payments": {
                "on_time": 0,
                "late": 0,
                "average_days": 0,
                "payment_methods": {}
            },
            "trends": {}
        }
        
        payment_days = []
        
        for invoice in invoices:
            # Extract key data
            amount = invoice.get('amount_cents', 0) / 100
            tax = invoice.get('tax_amount_cents', 0) / 100
            date = invoice.get('date', '')
            month = date[:7] if date else 'unknown'
            customer_name = invoice.get('customer', {}).get('name', 'Unknown')
            status = invoice.get('status', '')
            
            # Update summary
            analysis["summary"]["total_revenue"] += amount
            analysis["summary"]["total_tax"] += tax
            
            if status == 'paid':
                analysis["summary"]["paid_count"] += 1
            else:
                analysis["summary"]["pending_count"] += 1
            
            # Monthly breakdown
            if month not in analysis["monthly"]:
                analysis["monthly"][month] = {
                    "revenue": 0,
                    "tax": 0,
                    "count": 0,
                    "services": {}
                }
            
            analysis["monthly"][month]["revenue"] += amount
            analysis["monthly"][month]["tax"] += tax
            analysis["monthly"][month]["count"] += 1
            
            # Customer analysis
            if customer_name not in analysis["customers"]:
                analysis["customers"][customer_name] = {
                    "total_revenue": 0,
                    "invoice_count": 0,
                    "services_purchased": set(),
                    "average_invoice": 0,
                    "payment_behavior": "on_time"
                }
            
            analysis["customers"][customer_name]["total_revenue"] += amount
            analysis["customers"][customer_name]["invoice_count"] += 1
            
            # Service/Product analysis from line items
            line_items = invoice.get('line_items', [])
            for item in line_items:
                service = item.get('label', 'Unknown Service')
                service_amount = item.get('amount_cents', 0) / 100
                quantity = item.get('quantity', 1)
                
                if service not in analysis["services"]:
                    analysis["services"][service] = {
                        "total_revenue": 0,
                        "total_quantity": 0,
                        "invoice_count": 0,
                        "average_price": 0,
                        "customers": set()
                    }
                
                analysis["services"][service]["total_revenue"] += service_amount
                analysis["services"][service]["total_quantity"] += quantity
                analysis["services"][service]["invoice_count"] += 1
                analysis["services"][service]["customers"].add(customer_name)
                
                # Add to customer's purchased services
                analysis["customers"][customer_name]["services_purchased"].add(service)
                
                # Add to monthly service breakdown
                if service not in analysis["monthly"][month]["services"]:
                    analysis["monthly"][month]["services"][service] = 0
                analysis["monthly"][month]["services"][service] += service_amount
            
            # Payment analysis
            if status == 'paid' and invoice.get('paid_at'):
                invoice_date = datetime.fromisoformat(invoice['date'])
                paid_date = datetime.fromisoformat(invoice['paid_at'])
                days_to_payment = (paid_date - invoice_date).days
                payment_days.append(days_to_payment)
                
                if days_to_payment <= 30:
                    analysis["payments"]["on_time"] += 1
                else:
                    analysis["payments"]["late"] += 1
            
            # Payment method tracking
            payment_method = invoice.get('payment_method', 'unknown')
            if payment_method not in analysis["payments"]["payment_methods"]:
                analysis["payments"]["payment_methods"][payment_method] = 0
            analysis["payments"]["payment_methods"][payment_method] += 1
        
        # Calculate averages and trends
        if analysis["summary"]["invoice_count"] > 0:
            analysis["summary"]["average_invoice"] = round(
                analysis["summary"]["total_revenue"] / analysis["summary"]["invoice_count"], 2
            )
        
        if payment_days:
            analysis["payments"]["average_days"] = round(sum(payment_days) / len(payment_days), 1)
        
        # Calculate customer averages
        for customer, data in analysis["customers"].items():
            if data["invoice_count"] > 0:
                data["average_invoice"] = round(data["total_revenue"] / data["invoice_count"], 2)
            # Convert set to list for JSON serialization
            data["services_purchased"] = list(data["services_purchased"])
        
        # Calculate service averages
        for service, data in analysis["services"].items():
            if data["total_quantity"] > 0:
                data["average_price"] = round(data["total_revenue"] / data["total_quantity"], 2)
            # Convert set to list for JSON serialization
            data["customers"] = list(data["customers"])
        
        # Trend analysis
        months = sorted(analysis["monthly"].keys())
        if len(months) >= 2:
            analysis["trends"]["monthly_growth"] = []
            for i in range(1, len(months)):
                prev_revenue = analysis["monthly"][months[i-1]]["revenue"]
                curr_revenue = analysis["monthly"][months[i]]["revenue"]
                growth = ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
                analysis["trends"]["monthly_growth"].append({
                    "month": months[i],
                    "growth_percentage": round(growth, 2)
                })
        
        return analysis
    
    def get_expense_analysis(self) -> Dict:
        """Get detailed expense analysis"""
        try:
            response = requests.get(
                f"{self.base_url}/companies/{self.company_id}/supplier_invoices",
                headers=self.headers,
                params={"include": "line_items,supplier"},
                timeout=30
            )
            
            if response.status_code == 200:
                expenses = response.json().get('data', [])
                
                analysis = {
                    "total_expenses": 0,
                    "by_category": {},
                    "by_supplier": {},
                    "monthly_expenses": {},
                    "cost_centers": {}
                }
                
                for expense in expenses:
                    amount = expense.get('amount_cents', 0) / 100
                    supplier = expense.get('supplier', {}).get('name', 'Unknown')
                    date = expense.get('date', '')
                    month = date[:7] if date else 'unknown'
                    
                    analysis["total_expenses"] += amount
                    
                    # By supplier
                    if supplier not in analysis["by_supplier"]:
                        analysis["by_supplier"][supplier] = 0
                    analysis["by_supplier"][supplier] += amount
                    
                    # Monthly
                    if month not in analysis["monthly_expenses"]:
                        analysis["monthly_expenses"][month] = 0
                    analysis["monthly_expenses"][month] += amount
                    
                    # Categories from line items
                    for item in expense.get('line_items', []):
                        category = item.get('category', 'Other')
                        item_amount = item.get('amount_cents', 0) / 100
                        
                        if category not in analysis["by_category"]:
                            analysis["by_category"][category] = 0
                        analysis["by_category"][category] += item_amount
                
                return {"status": "success", "analysis": analysis}
            
            return {"status": "error", "message": f"API Error: {response.status_code}"}
            
        except Exception as e:
            logger.error(f"Failed to fetch expenses: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_financial_ratios(self) -> Dict:
        """Calculate key financial ratios and KPIs"""
        invoices = self.get_detailed_invoices()
        expenses = self.get_expense_analysis()
        
        if invoices["status"] == "success" and expenses["status"] == "success":
            revenue = invoices["summary"]["total_revenue"]
            costs = expenses["analysis"]["total_expenses"]
            
            ratios = {
                "profitability": {
                    "gross_margin": round((revenue - costs) / revenue * 100, 2) if revenue > 0 else 0,
                    "net_profit": revenue - costs,
                    "profit_margin": round((revenue - costs) / revenue * 100, 2) if revenue > 0 else 0
                },
                "efficiency": {
                    "revenue_per_invoice": invoices["summary"]["average_invoice"],
                    "collection_days": invoices["payment_analysis"]["average_days"],
                    "payment_on_time_rate": round(
                        invoices["payment_analysis"]["on_time"] / 
                        (invoices["payment_analysis"]["on_time"] + invoices["payment_analysis"]["late"]) * 100, 2
                    ) if (invoices["payment_analysis"]["on_time"] + invoices["payment_analysis"]["late"]) > 0 else 0
                },
                "growth": {
                    "yoy_revenue_growth": self._calculate_yoy_growth(invoices["monthly_breakdown"]),
                    "customer_concentration": self._calculate_customer_concentration(invoices["customer_analysis"]),
                    "service_diversity": len(invoices["service_analysis"])
                }
            }
            
            return {"status": "success", "ratios": ratios}
        
        return {"status": "error", "message": "Could not calculate ratios"}
    
    def _calculate_yoy_growth(self, monthly_data: Dict) -> float:
        """Calculate year-over-year growth"""
        current_year = datetime.now().year
        last_year = current_year - 1
        
        current_year_revenue = sum(
            data["revenue"] for month, data in monthly_data.items() 
            if month.startswith(str(current_year))
        )
        
        last_year_revenue = sum(
            data["revenue"] for month, data in monthly_data.items() 
            if month.startswith(str(last_year))
        )
        
        if last_year_revenue > 0:
            return round((current_year_revenue - last_year_revenue) / last_year_revenue * 100, 2)
        return 0
    
    def _calculate_customer_concentration(self, customer_data: Dict) -> Dict:
        """Calculate customer concentration risk"""
        total_revenue = sum(c["total_revenue"] for c in customer_data.values())
        
        if total_revenue == 0:
            return {"top_10_percentage": 0, "largest_customer_percentage": 0}
        
        sorted_customers = sorted(
            customer_data.items(), 
            key=lambda x: x[1]["total_revenue"], 
            reverse=True
        )
        
        top_10_revenue = sum(c[1]["total_revenue"] for c in sorted_customers[:10])
        largest_customer_revenue = sorted_customers[0][1]["total_revenue"] if sorted_customers else 0
        
        return {
            "top_10_percentage": round(top_10_revenue / total_revenue * 100, 2),
            "largest_customer_percentage": round(largest_customer_revenue / total_revenue * 100, 2)
        }
    
    def save_detailed_data(self):
        """Save all detailed financial data for AI training"""
        logger.info("Fetching comprehensive financial data from PennyLane...")
        
        # Get all data
        invoices = self.get_detailed_invoices()
        expenses = self.get_expense_analysis()
        ratios = self.get_financial_ratios()
        
        # Combine all data
        comprehensive_data = {
            "last_updated": datetime.now().isoformat(),
            "company_id": self.company_id,
            "financial_overview": {
                "revenue_analysis": invoices,
                "expense_analysis": expenses,
                "financial_ratios": ratios
            },
            "insights": self._generate_insights(invoices, expenses, ratios)
        }
        
        # Save to file
        output_file = Path("pennylane_detailed_financial_data.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed financial data saved to {output_file}")
        
        return comprehensive_data
    
    def _generate_insights(self, invoices: Dict, expenses: Dict, ratios: Dict) -> Dict:
        """Generate AI-friendly insights from financial data"""
        insights = {
            "revenue_insights": [],
            "expense_insights": [],
            "customer_insights": [],
            "service_insights": [],
            "financial_health": []
        }
        
        # Revenue insights
        if invoices["status"] == "success":
            total_revenue = invoices["summary"]["total_revenue"]
            insights["revenue_insights"].append(
                f"Total revenue: {total_revenue:,.2f}€ from {invoices['summary']['invoice_count']} invoices"
            )
            insights["revenue_insights"].append(
                f"Average invoice value: {invoices['summary']['average_invoice']:,.2f}€"
            )
            
            # Top services
            top_services = sorted(
                invoices["service_analysis"].items(),
                key=lambda x: x[1]["total_revenue"],
                reverse=True
            )[:5]
            
            for service, data in top_services:
                insights["service_insights"].append(
                    f"{service}: {data['total_revenue']:,.2f}€ revenue, "
                    f"{data['invoice_count']} invoices, "
                    f"{len(data['customers'])} unique customers"
                )
            
            # Top customers
            top_customers = sorted(
                invoices["customer_analysis"].items(),
                key=lambda x: x[1]["total_revenue"],
                reverse=True
            )[:5]
            
            for customer, data in top_customers:
                insights["customer_insights"].append(
                    f"{customer}: {data['total_revenue']:,.2f}€ lifetime value, "
                    f"{data['invoice_count']} purchases, "
                    f"Average: {data['average_invoice']:,.2f}€"
                )
        
        # Expense insights
        if expenses["status"] == "success":
            total_expenses = expenses["analysis"]["total_expenses"]
            insights["expense_insights"].append(f"Total expenses: {total_expenses:,.2f}€")
            
            # Top expense categories
            top_categories = sorted(
                expenses["analysis"]["by_category"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            for category, amount in top_categories:
                percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                insights["expense_insights"].append(
                    f"{category}: {amount:,.2f}€ ({percentage:.1f}% of total expenses)"
                )
        
        # Financial health
        if ratios["status"] == "success":
            r = ratios["ratios"]
            insights["financial_health"] = [
                f"Gross margin: {r['profitability']['gross_margin']}%",
                f"Net profit: {r['profitability']['net_profit']:,.2f}€",
                f"Average collection time: {r['efficiency']['collection_days']} days",
                f"On-time payment rate: {r['efficiency']['payment_on_time_rate']}%",
                f"Customer concentration risk: Top 10 customers = {r['growth']['customer_concentration']['top_10_percentage']}% of revenue"
            ]
        
        return insights

# CLI usage
if __name__ == "__main__":
    api = PennyLaneDetailedAPI()
    
    if api.test_connection():
        print("✅ PennyLane connection successful!")
        
        # Save comprehensive data
        data = api.save_detailed_data()
        
        # Print summary
        if data["financial_overview"]["revenue_analysis"]["status"] == "success":
            print(f"\n📊 Financial Summary:")
            print(f"Total Revenue: {data['financial_overview']['revenue_analysis']['summary']['total_revenue']:,.2f}€")
            print(f"Total Invoices: {data['financial_overview']['revenue_analysis']['summary']['invoice_count']}")
            print(f"\n💡 Key Insights:")
            for insight in data["insights"]["financial_health"]:
                print(f"  - {insight}")
    else:
        print("❌ Failed to connect to PennyLane API")