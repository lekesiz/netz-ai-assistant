"""
PennyLane API Integration Module
Syncs financial data from PennyLane accounting software
"""

import os
import json
import requests
import schedule
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Invoice:
    """Invoice data structure"""
    invoice_id: str
    invoice_number: str
    customer_name: str
    amount: float
    currency: str
    date: str
    status: str
    line_items: List[Dict]
    metadata: Dict[str, Any]

@dataclass
class Customer:
    """Customer data structure"""
    customer_id: str
    name: str
    email: str
    phone: str
    address: str
    total_revenue: float
    invoice_count: int

class PennyLaneAPI:
    """PennyLane API client"""
    
    def __init__(self, api_key: str, company_id: str):
        self.api_key = api_key
        self.company_id = company_id
        # PennyLane API URL - check documentation for correct endpoint
        self.base_url = "https://app.pennylane.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-KEY": api_key  # Some APIs use this format
        }
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}
    
    def get_invoices(self, start_date: str = None, end_date: str = None) -> List[Invoice]:
        """Get invoices from PennyLane"""
        params = {
            "company_id": self.company_id,
            "limit": 100
        }
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        data = self._make_request("invoices", data=params)
        invoices = []
        
        for inv in data.get("data", []):
            invoice = Invoice(
                invoice_id=inv.get("id"),
                invoice_number=inv.get("number"),
                customer_name=inv.get("customer", {}).get("name", "Unknown"),
                amount=float(inv.get("amount", 0)),
                currency=inv.get("currency", "EUR"),
                date=inv.get("date"),
                status=inv.get("status"),
                line_items=inv.get("line_items", []),
                metadata={
                    "payment_method": inv.get("payment_method"),
                    "due_date": inv.get("due_date"),
                    "notes": inv.get("notes")
                }
            )
            invoices.append(invoice)
        
        return invoices
    
    def get_customers(self) -> List[Customer]:
        """Get customers from PennyLane"""
        data = self._make_request("customers", data={"company_id": self.company_id})
        customers = []
        
        for cust in data.get("data", []):
            customer = Customer(
                customer_id=cust.get("id"),
                name=cust.get("name"),
                email=cust.get("email", ""),
                phone=cust.get("phone", ""),
                address=cust.get("address", ""),
                total_revenue=float(cust.get("total_revenue", 0)),
                invoice_count=int(cust.get("invoice_count", 0))
            )
            customers.append(customer)
        
        return customers
    
    def get_financial_summary(self) -> Dict:
        """Get financial summary"""
        # Get current year data
        current_year = datetime.now().year
        start_date = f"{current_year}-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        invoices = self.get_invoices(start_date, end_date)
        
        # Calculate summary
        total_revenue = sum(inv.amount for inv in invoices if inv.status == "paid")
        pending_revenue = sum(inv.amount for inv in invoices if inv.status == "pending")
        
        # Monthly breakdown
        monthly_revenue = {}
        for inv in invoices:
            if inv.status == "paid":
                month = inv.date[:7]  # YYYY-MM
                if month not in monthly_revenue:
                    monthly_revenue[month] = 0
                monthly_revenue[month] += inv.amount
        
        return {
            "year": current_year,
            "total_revenue": total_revenue,
            "pending_revenue": pending_revenue,
            "invoice_count": len(invoices),
            "monthly_revenue": monthly_revenue,
            "top_customers": self._get_top_customers(invoices),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_top_customers(self, invoices: List[Invoice], limit: int = 5) -> List[Dict]:
        """Get top customers by revenue"""
        customer_revenue = {}
        
        for inv in invoices:
            if inv.status == "paid":
                if inv.customer_name not in customer_revenue:
                    customer_revenue[inv.customer_name] = 0
                customer_revenue[inv.customer_name] += inv.amount
        
        # Sort by revenue
        sorted_customers = sorted(
            customer_revenue.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        return [
            {"name": name, "revenue": revenue}
            for name, revenue in sorted_customers
        ]

class PennyLaneSync:
    """Sync PennyLane data with AI training system"""
    
    def __init__(self, api_key: str, company_id: str, kb_file: str = "simple_api_kb.json"):
        self.api = PennyLaneAPI(api_key, company_id)
        self.kb_file = Path(kb_file)
        self.sync_history_file = Path("pennylane_sync_history.json")
        self.cache_dir = Path("pennylane_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Load sync history
        self.sync_history = self._load_sync_history()
    
    def _load_sync_history(self) -> Dict:
        """Load sync history"""
        if self.sync_history_file.exists():
            with open(self.sync_history_file, 'r') as f:
                return json.load(f)
        return {"last_sync": None, "synced_data": {}}
    
    def _save_sync_history(self):
        """Save sync history"""
        with open(self.sync_history_file, 'w') as f:
            json.dump(self.sync_history, f, indent=2)
    
    def _generate_hash(self, data: Any) -> str:
        """Generate hash for data"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def sync_financial_data(self):
        """Sync financial data from PennyLane"""
        logger.info("Starting PennyLane sync...")
        
        try:
            # Get financial summary
            summary = self.api.get_financial_summary()
            
            # Get detailed data
            customers = self.api.get_customers()
            current_month_invoices = self.api.get_invoices(
                start_date=datetime.now().strftime("%Y-%m-01"),
                end_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            # Prepare document content
            content = self._prepare_content(summary, customers, current_month_invoices)
            
            # Check if data has changed
            content_hash = self._generate_hash(content)
            if content_hash == self.sync_history.get("last_content_hash"):
                logger.info("No changes in PennyLane data")
                return
            
            # Update knowledge base
            self._update_knowledge_base(content)
            
            # Update sync history
            self.sync_history["last_sync"] = datetime.now().isoformat()
            self.sync_history["last_content_hash"] = content_hash
            self._save_sync_history()
            
            # Save to cache
            cache_file = self.cache_dir / f"pennylane_data_{datetime.now().strftime('%Y%m%d')}.json"
            with open(cache_file, 'w') as f:
                json.dump(content, f, indent=2)
            
            logger.info("PennyLane sync completed successfully")
            
        except Exception as e:
            logger.error(f"PennyLane sync failed: {e}")
    
    def _prepare_content(self, summary: Dict, customers: List[Customer], invoices: List[Invoice]) -> Dict:
        """Prepare content for knowledge base"""
        return {
            "company": "NETZ INFORMATIQUE",
            "financial_summary": summary,
            "customers": {
                "total_count": len(customers),
                "top_customers": [
                    {
                        "name": c.name,
                        "email": c.email,
                        "total_revenue": c.total_revenue,
                        "invoice_count": c.invoice_count
                    }
                    for c in sorted(customers, key=lambda x: x.total_revenue, reverse=True)[:10]
                ]
            },
            "recent_invoices": [
                {
                    "number": inv.invoice_number,
                    "customer": inv.customer_name,
                    "amount": inv.amount,
                    "currency": inv.currency,
                    "date": inv.date,
                    "status": inv.status
                }
                for inv in invoices
            ],
            "sync_time": datetime.now().isoformat()
        }
    
    def _update_knowledge_base(self, content: Dict):
        """Update AI knowledge base with PennyLane data"""
        try:
            # Load existing KB
            if self.kb_file.exists():
                with open(self.kb_file, 'r', encoding='utf-8') as f:
                    kb = json.load(f)
            else:
                kb = {"documents": [], "last_updated": None}
            
            # Remove old PennyLane data
            kb["documents"] = [
                doc for doc in kb["documents"] 
                if doc.get("metadata", {}).get("source") != "pennylane"
            ]
            
            # Add new document
            doc = {
                "content": json.dumps(content, indent=2),
                "metadata": {
                    "filename": "pennylane_financial_data.json",
                    "source": "pennylane",
                    "type": "financial_data",
                    "upload_time": datetime.now().isoformat()
                },
                "hash": self._generate_hash(content),
                "timestamp": datetime.now().isoformat()
            }
            
            kb["documents"].append(doc)
            kb["last_updated"] = datetime.now().isoformat()
            
            # Save KB
            with open(self.kb_file, 'w', encoding='utf-8') as f:
                json.dump(kb, f, ensure_ascii=False, indent=2)
            
            # Restart simple_api
            os.system("pkill -f simple_api.py")
            os.system("python simple_api.py > simple_api.log 2>&1 &")
            
            logger.info("Knowledge base updated with PennyLane data")
            
        except Exception as e:
            logger.error(f"Error updating KB: {e}")
    
    def start_auto_sync(self, interval_hours: int = 24):
        """Start automatic sync"""
        logger.info(f"Starting PennyLane auto-sync every {interval_hours} hours")
        
        # Run initial sync
        self.sync_financial_data()
        
        # Schedule periodic sync
        schedule.every(interval_hours).hours.do(self.sync_financial_data)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run PennyLane sync"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get credentials from environment or config
    API_KEY = os.getenv("PENNYLANE_API_KEY", "")
    COMPANY_ID = os.getenv("PENNYLANE_COMPANY_ID", "")
    
    if not API_KEY or not COMPANY_ID:
        logger.error("PennyLane credentials not found. Set PENNYLANE_API_KEY and PENNYLANE_COMPANY_ID environment variables.")
        return
    
    logger.info(f"Starting PennyLane sync for company {COMPANY_ID}")
    
    # Create sync manager
    sync_manager = PennyLaneSync(API_KEY, COMPANY_ID)
    
    # Option 1: One-time sync (default)
    sync_manager.sync_financial_data()
    
    # Option 2: Scheduled sync (daily)
    # sync_manager.start_auto_sync(interval_hours=24)

if __name__ == "__main__":
    main()