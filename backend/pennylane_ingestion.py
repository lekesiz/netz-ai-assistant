import logging
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import hashlib
from pennylane_service import get_pennylane_service

logger = logging.getLogger(__name__)

class PennyLaneIngestion:
    """Ingestion pipeline for PennyLane accounting data"""
    
    def __init__(self, qdrant_url: str = "localhost:6333"):
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.collection_name = "pennylane_data"
        self.vector_size = 384
        self.pennylane_service = get_pennylane_service()
        
        # Create collection if it doesn't exist
        self._create_collection()
    
    def _create_collection(self):
        """Create Qdrant collection for PennyLane data"""
        collections = self.qdrant_client.get_collections()
        if not any(col.name == self.collection_name for col in collections.collections):
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    def prepare_documents_from_pennylane(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert PennyLane data into documents for vector storage"""
        documents = []
        
        # Company information
        if data.get("company"):
            company = data["company"]
            doc_id = hashlib.md5("company_info".encode()).hexdigest()
            documents.append({
                "id": doc_id,
                "text": f"NETZ Informatique - Informations société: "
                        f"SIREN: {company.get('siren', 'N/A')}, "
                        f"TVA: {company.get('vat_number', 'N/A')}, "
                        f"Adresse: {company.get('address', 'N/A')}, "
                        f"Email: {company.get('email', 'N/A')}, "
                        f"Téléphone: {company.get('phone', 'N/A')}",
                "metadata": {
                    "type": "company_info",
                    "source": "pennylane",
                    "data": company
                }
            })
        
        # Customer documents
        for customer in data.get("customers", []):
            doc_id = hashlib.md5(f"customer_{customer.get('id')}".encode()).hexdigest()
            customer_text = (
                f"Client: {customer.get('name', 'N/A')}, "
                f"Email: {customer.get('email', 'N/A')}, "
                f"Téléphone: {customer.get('phone', 'N/A')}, "
                f"SIREN: {customer.get('siren', 'N/A')}, "
                f"Adresse: {customer.get('address', 'N/A')}"
            )
            documents.append({
                "id": doc_id,
                "text": customer_text,
                "metadata": {
                    "type": "customer",
                    "source": "pennylane",
                    "customer_id": customer.get('id'),
                    "customer_name": customer.get('name')
                }
            })
        
        # Supplier documents
        for supplier in data.get("suppliers", []):
            doc_id = hashlib.md5(f"supplier_{supplier.get('id')}".encode()).hexdigest()
            supplier_text = (
                f"Fournisseur: {supplier.get('name', 'N/A')}, "
                f"Email: {supplier.get('email', 'N/A')}, "
                f"SIREN: {supplier.get('siren', 'N/A')}, "
                f"Conditions de paiement: {supplier.get('payment_terms', 'N/A')}"
            )
            documents.append({
                "id": doc_id,
                "text": supplier_text,
                "metadata": {
                    "type": "supplier",
                    "source": "pennylane",
                    "supplier_id": supplier.get('id'),
                    "supplier_name": supplier.get('name')
                }
            })
        
        # Product/Service documents
        for product in data.get("products", []):
            doc_id = hashlib.md5(f"product_{product.get('id')}".encode()).hexdigest()
            product_text = (
                f"Produit/Service: {product.get('label', 'N/A')}, "
                f"Prix unitaire: {product.get('unit_price', 0)}€, "
                f"TVA: {product.get('vat_rate', 0)}%, "
                f"Catégorie: {product.get('category', 'N/A')}, "
                f"Description: {product.get('description', 'N/A')}"
            )
            documents.append({
                "id": doc_id,
                "text": product_text,
                "metadata": {
                    "type": "product",
                    "source": "pennylane",
                    "product_id": product.get('id'),
                    "product_name": product.get('label')
                }
            })
        
        # Invoice summaries
        invoice_summary = data.get("financial_summary", {}).get("invoice_stats", {})
        if invoice_summary:
            doc_id = hashlib.md5("invoice_summary".encode()).hexdigest()
            summary_text = (
                f"Résumé des factures: "
                f"Total factures: {invoice_summary.get('total_invoices', 0)}, "
                f"Montant total: {invoice_summary.get('total_amount', 0):.2f}€, "
                f"Montant payé: {invoice_summary.get('paid_amount', 0):.2f}€, "
                f"Montant en attente: {invoice_summary.get('pending_amount', 0):.2f}€, "
                f"Facture moyenne: {invoice_summary.get('average_invoice', 0):.2f}€"
            )
            documents.append({
                "id": doc_id,
                "text": summary_text,
                "metadata": {
                    "type": "financial_summary",
                    "source": "pennylane",
                    "summary_type": "invoices"
                }
            })
        
        # Top customers
        for i, customer in enumerate(data.get("financial_summary", {}).get("top_customers", [])):
            doc_id = hashlib.md5(f"top_customer_{i}".encode()).hexdigest()
            customer_text = (
                f"Top client #{i+1}: {customer.get('name', 'N/A')}, "
                f"Chiffre d'affaires total: {customer.get('total_revenue', 0):.2f}€, "
                f"Nombre de factures: {customer.get('invoice_count', 0)}"
            )
            documents.append({
                "id": doc_id,
                "text": customer_text,
                "metadata": {
                    "type": "top_customer",
                    "source": "pennylane",
                    "rank": i + 1,
                    "customer_id": customer.get('id')
                }
            })
        
        # Revenue by month
        revenue_data = data.get("financial_summary", {}).get("revenue_by_month", {})
        if revenue_data:
            revenue_text = "Chiffre d'affaires mensuel: "
            for month, amount in revenue_data.items():
                revenue_text += f"{month}: {amount:.2f}€, "
            
            doc_id = hashlib.md5("revenue_by_month".encode()).hexdigest()
            documents.append({
                "id": doc_id,
                "text": revenue_text.rstrip(", "),
                "metadata": {
                    "type": "revenue_analysis",
                    "source": "pennylane",
                    "data": revenue_data
                }
            })
        
        return documents
    
    def ingest_pennylane_data(self):
        """Fetch and ingest all PennyLane data"""
        try:
            logger.info("Fetching data from PennyLane...")
            pennylane_data = self.pennylane_service.get_all_data_for_training()
            
            # Save raw data for backup
            backup_path = Path("data/pennylane_backup")
            backup_path.mkdir(parents=True, exist_ok=True)
            backup_file = backup_path / f"pennylane_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(pennylane_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Backed up PennyLane data to {backup_file}")
            
            # Prepare documents
            documents = self.prepare_documents_from_pennylane(pennylane_data)
            logger.info(f"Prepared {len(documents)} documents from PennyLane data")
            
            if not documents:
                logger.warning("No documents to ingest")
                return
            
            # Generate embeddings
            texts = [doc["text"] for doc in documents]
            logger.info("Generating embeddings...")
            embeddings = self.encoder.encode(texts, show_progress_bar=True)
            
            # Prepare points for Qdrant
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                points.append(
                    PointStruct(
                        id=i,
                        vector=embedding.tolist(),
                        payload={
                            "text": doc["text"],
                            "metadata": doc["metadata"]
                        }
                    )
                )
            
            # Clear existing data and upload new
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector={"filter": {"must": [{"key": "metadata.source", "match": {"value": "pennylane"}}]}}
            )
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Successfully ingested {len(points)} PennyLane documents")
            
            # Update ingestion timestamp
            self._update_ingestion_status(len(points))
            
        except Exception as e:
            logger.error(f"Error ingesting PennyLane data: {e}")
            raise
    
    def _update_ingestion_status(self, document_count: int):
        """Update ingestion status in metadata"""
        status_doc = {
            "last_ingestion": datetime.now().isoformat(),
            "document_count": document_count,
            "source": "pennylane",
            "status": "success"
        }
        
        status_path = Path("data/ingestion_status.json")
        status_path.parent.mkdir(exist_ok=True)
        
        # Load existing status
        existing_status = {}
        if status_path.exists():
            with open(status_path, 'r') as f:
                existing_status = json.load(f)
        
        # Update PennyLane status
        existing_status["pennylane"] = status_doc
        
        # Save updated status
        with open(status_path, 'w') as f:
            json.dump(existing_status, f, indent=2)
    
    def search_financial_data(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for financial information"""
        query_vector = self.encoder.encode(query).tolist()
        
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        results = []
        for hit in search_result:
            results.append({
                "text": hit.payload["text"],
                "metadata": hit.payload["metadata"],
                "score": hit.score
            })
        
        return results

if __name__ == "__main__":
    # Test the PennyLane ingestion
    ingestion = PennyLaneIngestion()
    
    try:
        # Ingest data
        ingestion.ingest_pennylane_data()
        
        # Test search
        test_queries = [
            "Quel est le chiffre d'affaires total?",
            "Qui sont nos meilleurs clients?",
            "Informations sur les fournisseurs"
        ]
        
        for query in test_queries:
            print(f"\nRecherche: {query}")
            results = ingestion.search_financial_data(query, limit=3)
            for i, result in enumerate(results):
                print(f"{i+1}. Score: {result['score']:.3f}")
                print(f"   {result['text'][:150]}...")
                
    except Exception as e:
        logger.error(f"Test failed: {e}")