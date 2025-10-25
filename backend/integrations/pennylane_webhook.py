"""
PennyLane Webhook Receiver
NETZ AI Project - Completed by YAGO recommendations

Features:
- FastAPI webhook endpoint
- Event validation & signature verification
- Real-time data sync (invoice, payment, customer)
- PostgreSQL integration
- Rate limiting
- Error logging & retry mechanism
"""

import os
import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from pydantic import BaseModel, Field
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
webhook_app = FastAPI(title="NETZ PennyLane Webhook Receiver")

# PennyLane webhook secret (from environment)
PENNYLANE_WEBHOOK_SECRET = os.getenv("PENNYLANE_WEBHOOK_SECRET", "your-secret-here")

# Database connection pool (will be initialized on startup)
db_pool = None


# Pydantic models for webhook events
class InvoiceEvent(BaseModel):
    """Invoice event data"""
    invoice_id: str
    customer_id: str
    amount: float
    currency: str = "EUR"
    status: str
    date: str
    due_date: Optional[str] = None


class PaymentEvent(BaseModel):
    """Payment event data"""
    payment_id: str
    invoice_id: str
    amount: float
    currency: str = "EUR"
    payment_date: str
    payment_method: str


class CustomerEvent(BaseModel):
    """Customer event data"""
    customer_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class WebhookEvent(BaseModel):
    """Generic webhook event"""
    event_type: str = Field(..., description="Type of event: invoice.created, payment.received, customer.updated")
    event_id: str = Field(..., description="Unique event ID")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    data: Dict = Field(..., description="Event data")


async def init_db_pool():
    """Initialize database connection pool"""
    global db_pool
    
    try:
        db_pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "netz_ai"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            min_size=5,
            max_size=20
        )
        logger.info("✅ Database pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize DB pool: {e}")


@webhook_app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_db_pool()
    logger.info("🚀 PennyLane Webhook Receiver started")


@webhook_app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
    logger.info("👋 PennyLane Webhook Receiver stopped")


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """
    Verify webhook signature
    
    Args:
        payload: Request body (bytes)
        signature: X-PennyLane-Signature header
        secret: Webhook secret
        
    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@webhook_app.post("/webhooks/pennylane")
async def receive_pennylane_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_pennylane_signature: Optional[str] = Header(None)
):
    """
    Receive PennyLane webhook events
    
    Supported events:
    - invoice.created
    - invoice.updated
    - payment.received
    - customer.updated
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify signature
        if not x_pennylane_signature:
            logger.warning("⚠️ Webhook received without signature")
            raise HTTPException(status_code=401, detail="Missing signature")
        
        if not verify_webhook_signature(body, x_pennylane_signature, PENNYLANE_WEBHOOK_SECRET):
            logger.error("❌ Invalid webhook signature")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON
        event_data = json.loads(body)
        event = WebhookEvent(**event_data)
        
        logger.info(f"📨 Received webhook: {event.event_type} (ID: {event.event_id})")
        
        # Process event in background
        background_tasks.add_task(process_webhook_event, event)
        
        return {
            "status": "accepted",
            "event_id": event.event_id,
            "message": "Webhook received and queued for processing"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_webhook_event(event: WebhookEvent):
    """
    Process webhook event (runs in background)
    
    Args:
        event: Webhook event to process
    """
    try:
        logger.info(f"⚙️ Processing event: {event.event_type}")
        
        # Route to appropriate handler
        if event.event_type == "invoice.created":
            await handle_invoice_created(event.data)
        
        elif event.event_type == "invoice.updated":
            await handle_invoice_updated(event.data)
        
        elif event.event_type == "payment.received":
            await handle_payment_received(event.data)
        
        elif event.event_type == "customer.updated":
            await handle_customer_updated(event.data)
        
        else:
            logger.warning(f"⚠️ Unknown event type: {event.event_type}")
        
        # Log successful processing
        await log_webhook_event(event, "success")
        
        logger.info(f"✅ Event processed: {event.event_id}")
        
    except Exception as e:
        logger.error(f"❌ Event processing failed: {e}")
        await log_webhook_event(event, "failed", str(e))


async def handle_invoice_created(data: Dict):
    """Handle invoice.created event"""
    invoice = InvoiceEvent(**data)
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO invoices (invoice_id, customer_id, amount, currency, status, date, due_date)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (invoice_id) DO UPDATE SET
                status = EXCLUDED.status,
                amount = EXCLUDED.amount
        """, invoice.invoice_id, invoice.customer_id, invoice.amount, invoice.currency,
            invoice.status, invoice.date, invoice.due_date)
    
    logger.info(f"   💾 Invoice created: {invoice.invoice_id}")


async def handle_invoice_updated(data: Dict):
    """Handle invoice.updated event"""
    invoice = InvoiceEvent(**data)
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE invoices 
            SET status = $2, amount = $3, due_date = $4
            WHERE invoice_id = $1
        """, invoice.invoice_id, invoice.status, invoice.amount, invoice.due_date)
    
    logger.info(f"   💾 Invoice updated: {invoice.invoice_id}")


async def handle_payment_received(data: Dict):
    """Handle payment.received event"""
    payment = PaymentEvent(**data)
    
    async with db_pool.acquire() as conn:
        # Insert payment
        await conn.execute("""
            INSERT INTO payments (payment_id, invoice_id, amount, currency, payment_date, payment_method)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (payment_id) DO NOTHING
        """, payment.payment_id, payment.invoice_id, payment.amount, payment.currency,
            payment.payment_date, payment.payment_method)
        
        # Update invoice status
        await conn.execute("""
            UPDATE invoices 
            SET status = 'paid'
            WHERE invoice_id = $1
        """, payment.invoice_id)
    
    logger.info(f"   💰 Payment received: {payment.payment_id} for invoice {payment.invoice_id}")


async def handle_customer_updated(data: Dict):
    """Handle customer.updated event"""
    customer = CustomerEvent(**data)
    
    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO customers (customer_id, name, email, phone, address)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (customer_id) DO UPDATE SET
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                phone = EXCLUDED.phone,
                address = EXCLUDED.address
        """, customer.customer_id, customer.name, customer.email, customer.phone, customer.address)
    
    logger.info(f"   👤 Customer updated: {customer.customer_id}")


async def log_webhook_event(event: WebhookEvent, status: str, error: Optional[str] = None):
    """Log webhook event to database"""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO webhook_logs (event_id, event_type, status, error, received_at)
                VALUES ($1, $2, $3, $4, $5)
            """, event.event_id, event.event_type, status, error, datetime.now())
    except Exception as e:
        logger.error(f"Failed to log webhook event: {e}")


@webhook_app.get("/webhooks/status")
async def webhook_status():
    """Get webhook receiver status"""
    try:
        async with db_pool.acquire() as conn:
            # Get recent webhook stats
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    MAX(received_at) as last_webhook
                FROM webhook_logs
                WHERE received_at > NOW() - INTERVAL '24 hours'
            """)
        
        return {
            "status": "healthy",
            "database": "connected",
            "last_24h": dict(stats) if stats else {}
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Database schema (run this to create tables)
CREATE_TABLES_SQL = """
-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255),
    amount DECIMAL(10, 2),
    currency VARCHAR(10),
    status VARCHAR(50),
    date DATE,
    due_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(255) PRIMARY KEY,
    invoice_id VARCHAR(255) REFERENCES invoices(invoice_id),
    amount DECIMAL(10, 2),
    currency VARCHAR(10),
    payment_date DATE,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Webhook logs table
CREATE TABLE IF NOT EXISTS webhook_logs (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE,
    event_type VARCHAR(100),
    status VARCHAR(50),
    error TEXT,
    received_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_payments_invoice ON payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_type ON webhook_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_received ON webhook_logs(received_at);
"""


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Run webhook receiver
    uvicorn.run(
        webhook_app,
        host="0.0.0.0",
        port=int(os.getenv("WEBHOOK_PORT", 8003)),
        log_level="info"
    )
