# NETZ AI - PennyLane Integration

## 🏦 Overview

The NETZ AI Assistant now integrates with PennyLane accounting software to provide intelligent financial insights and automated accounting data access.

## 🔑 API Configuration

**API Key**: Configured in `.env` file
**Base URL**: https://app.pennylane.com/api/external/v1

## 📊 Available Data

### 1. Company Information
- SIREN/SIRET
- VAT Number
- Address and Contact Info
- Banking Details

### 2. Customer Data
- Customer Database
- Contact Information
- Purchase History
- Outstanding Invoices

### 3. Supplier Management
- Supplier List
- Payment Terms
- Purchase Orders
- Bills and Payments

### 4. Financial Documents
- **Invoices**: Sales invoices with status tracking
- **Bills**: Supplier invoices
- **Quotes**: Pending quotes
- **Credit Notes**: Refunds and corrections

### 5. Products & Services
- Service Catalog
- Pricing Information
- VAT Rates
- Product Categories

### 6. Financial Analytics
- Revenue by Month
- Top Customers by Revenue
- Invoice Statistics
- Payment Status Tracking

## 🔄 Automatic Data Synchronization

### Update Schedule
- **PennyLane Data**: Daily at 02:00
- **Google Drive**: Daily at 03:00
- **Manual Updates**: Available via API

### Data Retention
- Backups kept for 30 days
- Automatic cleanup of old data
- Versioned backups with timestamps

## 🤖 AI Capabilities

### 1. Financial Queries
The AI can answer questions like:
- "Quel est notre chiffre d'affaires ce mois?"
- "Qui sont nos meilleurs clients?"
- "Quelles factures sont en attente de paiement?"
- "Quel est le montant total des factures impayées?"

### 2. Customer Insights
- Customer purchase patterns
- Outstanding balances
- Communication history
- Payment behavior analysis

### 3. Supplier Analysis
- Spending by supplier
- Payment terms optimization
- Cost analysis
- Supplier performance

### 4. Business Intelligence
- Revenue trends
- Cash flow insights
- Customer segmentation
- Product performance

## 🔒 Security

### Data Protection
- API Key stored securely in environment variables
- Encrypted data transmission
- Local data backup with access control
- No sensitive data in logs

### Access Control
- Role-based permissions
- Audit trail for all queries
- Data anonymization options
- GDPR compliance

## 📡 API Endpoints

### Data Management
- `POST /api/data/update/pennylane` - Trigger manual update
- `GET /api/data/status` - Check data synchronization status

### Search & Query
- `POST /api/pennylane/search` - Search financial data
- `POST /api/chat` - Chat with financial context

### Examples:
```bash
# Search for customer information
curl -X POST http://localhost:8000/api/pennylane/search \
  -H "Content-Type: application/json" \
  -d '{"query": "clients avec factures impayées", "limit": 5}'

# Trigger manual data update
curl -X POST http://localhost:8000/api/data/update/pennylane

# Check data status
curl -X GET http://localhost:8000/api/data/status
```

## 📈 Data Schema

### Customer Document
```json
{
  "type": "customer",
  "text": "Client: ACME Corp, Email: contact@acme.fr, SIREN: 123456789",
  "metadata": {
    "customer_id": "cust_123",
    "customer_name": "ACME Corp",
    "source": "pennylane"
  }
}
```

### Financial Summary
```json
{
  "type": "financial_summary",
  "text": "Total factures: 150, Montant total: 125000€, Payé: 100000€",
  "metadata": {
    "summary_type": "invoices",
    "period": "2024",
    "source": "pennylane"
  }
}
```

## 🚀 Usage Examples

### 1. Financial Assistant
```python
# Query: "Quel est le statut de paiement de nos dernières factures?"
# Response: "Sur les 25 dernières factures émises ce mois:
# - 18 sont payées (72%)
# - 5 sont en attente de paiement (20%)
# - 2 sont en retard (8%)
# Montant total en attente: 15,450€"
```

### 2. Customer Analysis
```python
# Query: "Qui est notre meilleur client?"
# Response: "Votre meilleur client est TECH SOLUTIONS:
# - Chiffre d'affaires total: 45,000€
# - Nombre de factures: 12
# - Dernière commande: 15/01/2025
# - Statut: Tous les paiements à jour"
```

### 3. Cash Flow Insights
```python
# Query: "Analyse de trésorerie pour ce mois"
# Response: "Analyse de trésorerie - Janvier 2025:
# - Entrées prévues: 35,000€
# - Factures à encaisser: 15,450€
# - Dépenses prévues: 22,000€
# - Solde prévisionnel: +28,450€"
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check API key validity
   - Verify internet connection
   - Check PennyLane service status

2. **Data Not Updating**
   - Check scheduler logs
   - Verify cron expressions
   - Manual trigger via API

3. **Search Not Working**
   - Ensure Qdrant is running
   - Check collection exists
   - Verify embeddings generated

## 📋 Best Practices

1. **Regular Monitoring**
   - Check update logs weekly
   - Monitor data quality
   - Review search accuracy

2. **Data Hygiene**
   - Keep PennyLane data clean
   - Regular customer/supplier updates
   - Accurate product categorization

3. **Security**
   - Rotate API keys quarterly
   - Review access logs
   - Update dependencies

## 🔮 Future Enhancements

1. **Advanced Analytics**
   - Predictive cash flow
   - Customer churn analysis
   - Automated financial reports

2. **Integrations**
   - Bank reconciliation
   - Tax calculations
   - Export to accounting software

3. **AI Improvements**
   - Multi-language support
   - Voice queries
   - Automated insights

---
*Last updated: 2025-01-10*