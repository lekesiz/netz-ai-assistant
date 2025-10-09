#!/usr/bin/env python3
"""
Load real PennyLane financial data into RAG system
"""

import json
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
import uuid

# Initialize
client = QdrantClient(url="http://localhost:6333")
encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
collection_name = "netz_documents"

print("💰 Loading Real PennyLane Financial Data into RAG")
print("="*50)

# Load the fetched data
try:
    with open('pennylane_data.json', 'r', encoding='utf-8') as f:
        pennylane_data = json.load(f)
except FileNotFoundError:
    print("❌ Error: pennylane_data.json not found!")
    print("   Please run: python fetch_pennylane_data.py first")
    exit(1)

# Extract data
company = pennylane_data['company']
summary = pennylane_data['summary']
invoices = pennylane_data['invoices']
customers = pennylane_data['customers']

# Current date info
current_date = datetime.now()
current_month = current_date.strftime("%B %Y")

# Create financial report
financial_report = f"""
NETZ INFORMATIQUE - Rapport Financier Réel {current_month}
Source: PennyLane (Données officielles)

CHIFFRE D'AFFAIRES MENSUEL - {current_month.upper()}
================================================
Chiffre d'affaires total: {summary['monthly_revenue']:,.2f} € HT
Nombre de factures émises: {summary['monthly_invoices']}
Chiffre d'affaires moyen par facture: {summary['monthly_revenue'] / max(summary['monthly_invoices'], 1):,.2f} € HT

CHIFFRE D'AFFAIRES ANNUEL 2025
==============================
Chiffre d'affaires cumulé 2025: {summary['yearly_revenue']:,.2f} € HT
Moyenne mensuelle (sur {current_date.month} mois): {summary['yearly_revenue'] / current_date.month:,.2f} € HT
Projection annuelle: {(summary['yearly_revenue'] / current_date.month) * 12:,.2f} € HT

STATISTIQUES CLIENTS
====================
Nombre total de clients actifs: {summary['active_customers']:,}
Nombre total de factures dans le système: {summary['total_invoices']:,}

DERNIÈRES FACTURES ({current_month})
====================================
"""

# Add recent invoices
month_invoices = []
for inv in invoices:
    try:
        inv_date = datetime.strptime(inv.get('date', inv.get('issue_date', ''))[:10], '%Y-%m-%d')
        if inv_date.month == current_date.month and inv_date.year == current_date.year:
            month_invoices.append(inv)
    except:
        continue

for i, inv in enumerate(month_invoices[:10], 1):
    customer_name = inv.get('customer_name', inv.get('customer', {}).get('name', 'N/A'))
    amount = float(inv.get('amount', inv.get('total_amount', inv.get('amount_with_tax', 0))))
    invoice_number = inv.get('invoice_number', inv.get('number', 'N/A'))
    date = inv.get('date', inv.get('issue_date', 'N/A'))[:10]
    
    financial_report += f"\n{i}. Facture {invoice_number}"
    financial_report += f"\n   Client: {customer_name}"
    financial_report += f"\n   Montant: {amount:,.2f} € HT"
    financial_report += f"\n   Date: {date}\n"

financial_report += f"\nDernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
financial_report += f"\nSource: API PennyLane"

# Create customer report
customer_report = f"""
NETZ INFORMATIQUE - Rapport Clients (Données PennyLane)
Date: {current_month}

PORTEFEUILLE CLIENTS
====================
Nombre total de clients dans PennyLane: {summary['active_customers']:,}

TOP 10 CLIENTS RÉCENTS:
"""

# Add customer list
for i, customer in enumerate(customers[:10], 1):
    name = customer.get('name', customer.get('label', 'N/A'))
    phone = customer.get('phone', '')
    customer_type = customer.get('customer_type', 'company')
    notes = customer.get('notes', '')
    
    customer_report += f"\n{i}. {name}"
    if phone:
        customer_report += f"\n   Tél: {phone}"
    customer_report += f"\n   Type: {customer_type}"
    if notes:
        customer_report += f"\n   Notes: {notes[:50]}..."
    customer_report += "\n"

customer_report += f"\nTotal clients actifs: {summary['active_customers']:,}"
customer_report += f"\nDernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}"

# Create summary for quick answers
quick_summary = f"""
NETZ INFORMATIQUE - Données Financières Clés (PennyLane)

CHIFFRE D'AFFAIRES:
- Mois en cours ({current_month}): {summary['monthly_revenue']:,.2f} € HT
- Nombre de factures ce mois: {summary['monthly_invoices']}
- Total année 2025: {summary['yearly_revenue']:,.2f} € HT
- Projection fin d'année: {(summary['yearly_revenue'] / current_date.month) * 12:,.2f} € HT

CLIENTS:
- Nombre total de clients: {summary['active_customers']:,}

ENTREPRISE:
- Nom: {company.get('name', 'NETZ INFORMATIQUE')}
- Contact: {company.get('email', 'mikail@netzinformatique.fr')}

Source: Données réelles PennyLane
Dernière synchronisation: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""

# Load documents into RAG
def load_document(text, doc_type):
    """Load document into vector database"""
    try:
        vector = encoder.encode(text)
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector.tolist(),
                    payload={
                        "text": text,
                        "metadata": {
                            "source": "pennylane_api",
                            "type": doc_type,
                            "last_updated": datetime.now().isoformat(),
                            "month": current_month,
                            "data_type": "real_financial_data"
                        }
                    }
                )
            ]
        )
        print(f"✅ Loaded: {doc_type}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Load all documents
print("\nLoading PennyLane data into RAG system...")
load_document(financial_report, "pennylane_financial_report")
load_document(customer_report, "pennylane_customer_report")
load_document(quick_summary, "pennylane_quick_summary")

print("\n" + "="*50)
print("✅ Real PennyLane data successfully loaded!")
print("\nKey figures now available:")
print(f"- Monthly revenue ({current_month}): €{summary['monthly_revenue']:,.2f}")
print(f"- Monthly invoices: {summary['monthly_invoices']}")
print(f"- Yearly revenue (2025): €{summary['yearly_revenue']:,.2f}")
print(f"- Active customers: {summary['active_customers']:,}")
print("\nThe AI assistant now has access to REAL financial data from PennyLane!")