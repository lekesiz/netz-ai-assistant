import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PennyLaneConfig:
    api_key: str
    base_url: str = "https://app.pennylane.com/api/external/v1"
    timeout: int = 30

class PennyLaneService:
    """Service for integrating with PennyLane accounting API"""
    
    def __init__(self, config: Optional[PennyLaneConfig] = None):
        if config is None:
            config = PennyLaneConfig(
                api_key=os.getenv("PENNYLANE_API_KEY"),
                base_url=os.getenv("PENNYLANE_BASE_URL", "https://app.pennylane.com/api/external/v1")
            )
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request to PennyLane"""
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.config.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"PennyLane API error: {e}")
            raise
    
    # Company Information
    def get_company_info(self) -> Dict[str, Any]:
        """Get company information from PennyLane"""
        return self._make_request("GET", "/company")
    
    # Customer Management
    def get_customers(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Get list of customers"""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", "/customers", params=params)
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get specific customer details"""
        return self._make_request("GET", f"/customers/{customer_id}")
    
    # Supplier Management
    def get_suppliers(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Get list of suppliers"""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", "/suppliers", params=params)
    
    # Invoice Management
    def get_invoices(self, page: int = 1, per_page: int = 100, 
                     status: Optional[str] = None,
                     date_from: Optional[str] = None,
                     date_to: Optional[str] = None) -> Dict[str, Any]:
        """Get list of invoices with optional filters"""
        params = {
            "page": page,
            "per_page": per_page
        }
        if status:
            params["status"] = status
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
            
        return self._make_request("GET", "/invoices", params=params)
    
    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get specific invoice details"""
        return self._make_request("GET", f"/invoices/{invoice_id}")
    
    # Bill Management
    def get_bills(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Get list of bills (supplier invoices)"""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", "/bills", params=params)
    
    # Products and Services
    def get_products(self, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """Get list of products/services"""
        params = {"page": page, "per_page": per_page}
        return self._make_request("GET", "/products", params=params)
    
    # Financial Reports
    def get_balance_sheet(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get balance sheet"""
        params = {}
        if date:
            params["date"] = date
        return self._make_request("GET", "/reports/balance_sheet", params=params)
    
    def get_income_statement(self, date_from: str, date_to: str) -> Dict[str, Any]:
        """Get income statement (P&L)"""
        params = {
            "date_from": date_from,
            "date_to": date_to
        }
        return self._make_request("GET", "/reports/income_statement", params=params)
    
    # Data Aggregation for AI Training
    def get_all_data_for_training(self) -> Dict[str, Any]:
        """Aggregate all relevant data for AI training"""
        training_data = {
            "company": None,
            "customers": [],
            "suppliers": [],
            "invoices": [],
            "bills": [],
            "products": [],
            "financial_summary": {},
            "extracted_at": datetime.now().isoformat()
        }
        
        try:
            # Get company info
            logger.info("Fetching company information...")
            training_data["company"] = self.get_company_info()
            
            # Get customers (paginated)
            logger.info("Fetching customers...")
            page = 1
            while True:
                customers_page = self.get_customers(page=page)
                if not customers_page.get("data"):
                    break
                training_data["customers"].extend(customers_page["data"])
                if page >= customers_page.get("meta", {}).get("last_page", 1):
                    break
                page += 1
            
            # Get suppliers (paginated)
            logger.info("Fetching suppliers...")
            page = 1
            while True:
                suppliers_page = self.get_suppliers(page=page)
                if not suppliers_page.get("data"):
                    break
                training_data["suppliers"].extend(suppliers_page["data"])
                if page >= suppliers_page.get("meta", {}).get("last_page", 1):
                    break
                page += 1
            
            # Get recent invoices (last 6 months)
            logger.info("Fetching invoices...")
            date_from = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            date_to = datetime.now().strftime("%Y-%m-%d")
            page = 1
            while True:
                invoices_page = self.get_invoices(
                    page=page,
                    date_from=date_from,
                    date_to=date_to
                )
                if not invoices_page.get("data"):
                    break
                training_data["invoices"].extend(invoices_page["data"])
                if page >= invoices_page.get("meta", {}).get("last_page", 1):
                    break
                page += 1
            
            # Get products/services
            logger.info("Fetching products...")
            page = 1
            while True:
                products_page = self.get_products(page=page)
                if not products_page.get("data"):
                    break
                training_data["products"].extend(products_page["data"])
                if page >= products_page.get("meta", {}).get("last_page", 1):
                    break
                page += 1
            
            # Calculate financial summaries
            logger.info("Calculating financial summaries...")
            training_data["financial_summary"] = self._calculate_summaries(training_data)
            
            logger.info(f"Data extraction complete. Found: "
                       f"{len(training_data['customers'])} customers, "
                       f"{len(training_data['suppliers'])} suppliers, "
                       f"{len(training_data['invoices'])} invoices, "
                       f"{len(training_data['products'])} products")
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error fetching PennyLane data: {e}")
            raise
    
    def _calculate_summaries(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial summaries from raw data"""
        summary = {
            "total_customers": len(data.get("customers", [])),
            "total_suppliers": len(data.get("suppliers", [])),
            "total_products": len(data.get("products", [])),
            "invoice_stats": self._calculate_invoice_stats(data.get("invoices", [])),
            "top_customers": self._get_top_customers(data.get("invoices", [])),
            "revenue_by_month": self._calculate_revenue_by_month(data.get("invoices", []))
        }
        return summary
    
    def _calculate_invoice_stats(self, invoices: List[Dict]) -> Dict[str, Any]:
        """Calculate invoice statistics"""
        if not invoices:
            return {}
        
        total_amount = sum(float(inv.get("amount", 0)) for inv in invoices)
        paid_amount = sum(float(inv.get("amount", 0)) for inv in invoices 
                         if inv.get("status") == "paid")
        
        return {
            "total_invoices": len(invoices),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "pending_amount": total_amount - paid_amount,
            "average_invoice": total_amount / len(invoices) if invoices else 0
        }
    
    def _get_top_customers(self, invoices: List[Dict], limit: int = 10) -> List[Dict]:
        """Get top customers by revenue"""
        customer_revenue = {}
        
        for invoice in invoices:
            customer_id = invoice.get("customer_id")
            customer_name = invoice.get("customer", {}).get("name", "Unknown")
            amount = float(invoice.get("amount", 0))
            
            if customer_id:
                if customer_id not in customer_revenue:
                    customer_revenue[customer_id] = {
                        "id": customer_id,
                        "name": customer_name,
                        "total_revenue": 0,
                        "invoice_count": 0
                    }
                customer_revenue[customer_id]["total_revenue"] += amount
                customer_revenue[customer_id]["invoice_count"] += 1
        
        # Sort by revenue
        sorted_customers = sorted(
            customer_revenue.values(),
            key=lambda x: x["total_revenue"],
            reverse=True
        )
        
        return sorted_customers[:limit]
    
    def _calculate_revenue_by_month(self, invoices: List[Dict]) -> Dict[str, float]:
        """Calculate revenue by month"""
        revenue_by_month = {}
        
        for invoice in invoices:
            date_str = invoice.get("date")
            if date_str:
                month_key = date_str[:7]  # YYYY-MM
                amount = float(invoice.get("amount", 0))
                revenue_by_month[month_key] = revenue_by_month.get(month_key, 0) + amount
        
        return dict(sorted(revenue_by_month.items()))

# Singleton instance
_pennylane_service = None

def get_pennylane_service() -> PennyLaneService:
    """Get singleton PennyLane service instance"""
    global _pennylane_service
    if _pennylane_service is None:
        _pennylane_service = PennyLaneService()
    return _pennylane_service