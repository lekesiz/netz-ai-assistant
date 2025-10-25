"""
Unit Tests for NETZ AI Integrations
Tests for Google Drive, Gmail, PennyLane, and Wedof integrations

Run with: pytest test_integrations.py -v
"""

import pytest
import hmac
import hashlib
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


# ==================== GMAIL INTEGRATION TESTS ====================

class TestGmailIntegration:
    """Test suite for Gmail sync integration"""

    def test_categorize_email_support(self):
        """Test email categorization - support category"""
        from integrations.gmail_sync import GmailSync

        sync = GmailSync.__new__(GmailSync)  # Create instance without init
        sync.category_keywords = {
            "support": ["help", "issue", "problem", "bug", "error"],
            "sales": ["devis", "quote", "price"],
            "administrative": ["facture", "invoice"]
        }

        # Test support email
        subject = "Urgent: Computer problem"
        body = "I need help fixing this error"
        category = sync._categorize_email(subject, body)

        assert category == "support", f"Expected 'support', got '{category}'"

    def test_categorize_email_sales(self):
        """Test email categorization - sales category"""
        from integrations.gmail_sync import GmailSync

        sync = GmailSync.__new__(GmailSync)
        sync.category_keywords = {
            "support": ["help", "issue", "problem"],
            "sales": ["devis", "quote", "price", "tarif"],
            "administrative": ["facture", "invoice"]
        }

        subject = "Demande de devis"
        body = "Je voudrais un devis pour une formation Excel"
        category = sync._categorize_email(subject, body)

        assert category == "sales", f"Expected 'sales', got '{category}'"

    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis - positive"""
        from integrations.gmail_sync import GmailSync

        sync = GmailSync.__new__(GmailSync)
        sync.positive_keywords = ["merci", "thank", "great", "excellent", "parfait"]
        sync.negative_keywords = ["problem", "issue", "error"]

        subject = "Thank you for the excellent service"
        body = "Everything was great, merci beaucoup!"
        sentiment = sync._analyze_sentiment(subject, body)

        assert sentiment == "positive", f"Expected 'positive', got '{sentiment}'"

    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis - negative"""
        from integrations.gmail_sync import GmailSync

        sync = GmailSync.__new__(GmailSync)
        sync.positive_keywords = ["merci", "thank"]
        sync.negative_keywords = ["problem", "issue", "error", "bug", "fail"]

        subject = "Problem with your service"
        body = "I encountered multiple errors and bugs"
        sentiment = sync._analyze_sentiment(subject, body)

        assert sentiment == "negative", f"Expected 'negative', got '{sentiment}'"

    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis - neutral"""
        from integrations.gmail_sync import GmailSync

        sync = GmailSync.__new__(GmailSync)
        sync.positive_keywords = ["merci", "thank"]
        sync.negative_keywords = ["problem", "issue"]

        subject = "Question about your hours"
        body = "What are your opening times?"
        sentiment = sync._analyze_sentiment(subject, body)

        assert sentiment == "neutral", f"Expected 'neutral', got '{sentiment}'"


# ==================== PENNYLANE WEBHOOK TESTS ====================

class TestPennyLaneWebhook:
    """Test suite for PennyLane webhook integration"""

    def test_verify_webhook_signature_valid(self):
        """Test HMAC signature verification - valid signature"""
        from integrations.pennylane_webhook import verify_webhook_signature

        payload = b'{"event": "invoice.created", "data": {"id": "123"}}'
        secret = "test_secret_key"

        # Generate valid signature
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        result = verify_webhook_signature(payload, expected_signature, secret)

        assert result is True, "Valid signature should be accepted"

    def test_verify_webhook_signature_invalid(self):
        """Test HMAC signature verification - invalid signature"""
        from integrations.pennylane_webhook import verify_webhook_signature

        payload = b'{"event": "invoice.created"}'
        secret = "test_secret_key"
        invalid_signature = "invalid_signature_12345"

        result = verify_webhook_signature(payload, invalid_signature, secret)

        assert result is False, "Invalid signature should be rejected"

    def test_verify_webhook_signature_tampered_payload(self):
        """Test HMAC signature verification - tampered payload"""
        from integrations.pennylane_webhook import verify_webhook_signature

        original_payload = b'{"event": "invoice.created", "amount": 100}'
        secret = "test_secret_key"

        # Generate signature for original payload
        signature = hmac.new(secret.encode(), original_payload, hashlib.sha256).hexdigest()

        # Tamper with payload
        tampered_payload = b'{"event": "invoice.created", "amount": 999}'

        result = verify_webhook_signature(tampered_payload, signature, secret)

        assert result is False, "Tampered payload should fail verification"


# ==================== WEDOF INTEGRATION TESTS ====================

class TestWedofIntegration:
    """Test suite for Wedof sync integration"""

    def test_process_stagiaire_data(self):
        """Test stagiaire data processing"""
        from integrations.wedof_sync import WedofSync

        sync = WedofSync.__new__(WedofSync)

        raw_data = {
            "id": "stag123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "0612345678",
            "status": "active",
            "start_date": "2025-01-15",
            "end_date": "2025-06-15",
            "formation_id": "form456",
            "company": {"name": "ABC Corp"},
            "created_at": "2025-01-10T10:00:00Z",
            "updated_at": "2025-01-20T15:30:00Z",
            "address": "123 Rue Test",
            "city": "Paris",
            "postal_code": "75001"
        }

        processed = sync._process_stagiaire(raw_data)

        assert processed["stagiaire_id"] == "stag123"
        assert processed["full_name"] == "Jean Dupont"
        assert processed["email"] == "jean.dupont@example.com"
        assert processed["status"] == "active"
        assert processed["company"] == "ABC Corp"
        assert processed["metadata"]["city"] == "Paris"

    def test_process_formation_data(self):
        """Test formation data processing"""
        from integrations.wedof_sync import WedofSync

        sync = WedofSync.__new__(WedofSync)

        raw_data = {
            "id": "form789",
            "title": "Python Programming",
            "description": "Learn Python basics",
            "category": "programming",
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
            "duration_hours": 40,
            "location": "Paris Office",
            "instructor": {"name": "Marie Martin"},
            "max_participants": 10,
            "current_participants": 7,
            "status": "scheduled",
            "created_at": "2025-01-15T09:00:00Z",
            "updated_at": "2025-01-25T14:00:00Z",
            "certification": "QUALIOPI",
            "level": "beginner"
        }

        processed = sync._process_formation(raw_data)

        assert processed["formation_id"] == "form789"
        assert processed["title"] == "Python Programming"
        assert processed["duration_hours"] == 40
        assert processed["instructor"] == "Marie Martin"
        assert processed["max_participants"] == 10
        assert processed["current_participants"] == 7
        assert processed["metadata"]["certification"] == "QUALIOPI"


# ==================== INTEGRATIONS API TESTS ====================

class TestIntegrationsAPI:
    """Test suite for Integrations REST API"""

    @pytest.fixture
    def mock_background_tasks(self):
        """Mock FastAPI BackgroundTasks"""
        return Mock()

    def test_integration_status_format(self):
        """Test integration status response format"""
        from integrations_api import IntegrationStatus

        status = IntegrationStatus(
            enabled=True,
            last_sync="2025-01-25T10:00:00",
            records_count=150,
            error=None
        )

        assert status.enabled is True
        assert status.last_sync == "2025-01-25T10:00:00"
        assert status.records_count == 150
        assert status.error is None

    def test_sync_response_success(self):
        """Test successful sync response format"""
        from integrations_api import SyncResponse

        response = SyncResponse(
            success=True,
            message="Gmail sync started",
            task_id="gmail-1234567890",
            records_synced=100,
            error=None
        )

        assert response.success is True
        assert "Gmail" in response.message
        assert response.task_id.startswith("gmail-")
        assert response.records_synced == 100

    def test_sync_response_error(self):
        """Test error sync response format"""
        from integrations_api import SyncResponse

        response = SyncResponse(
            success=False,
            message="Sync failed",
            task_id=None,
            records_synced=0,
            error="Connection timeout"
        )

        assert response.success is False
        assert response.error == "Connection timeout"


# ==================== UTILITY TESTS ====================

class TestIntegrationUtilities:
    """Test suite for integration utility functions"""

    def test_should_sync_new_entity(self):
        """Test sync decision for new entity"""
        from integrations.wedof_sync import WedofSync

        sync = WedofSync.__new__(WedofSync)
        sync.sync_history_file = Mock()
        sync._load_sync_history = Mock(return_value={})

        # New entity should always sync
        should_sync = sync._should_sync("stagiaire", "new123", "2025-01-25T10:00:00")

        assert should_sync is True, "New entities should always be synced"

    def test_should_sync_modified_entity(self):
        """Test sync decision for modified entity"""
        from integrations.wedof_sync import WedofSync

        sync = WedofSync.__new__(WedofSync)
        sync._load_sync_history = Mock(return_value={
            "stagiaire:existing123": "2025-01-20T10:00:00"
        })

        # Modified entity (newer timestamp) should sync
        should_sync = sync._should_sync("stagiaire", "existing123", "2025-01-25T15:00:00")

        assert should_sync is True, "Modified entities should be synced"

    def test_should_not_sync_unchanged_entity(self):
        """Test sync decision for unchanged entity"""
        from integrations.wedof_sync import WedofSync

        sync = WedofSync.__new__(WedofSync)
        sync._load_sync_history = Mock(return_value={
            "stagiaire:unchanged123": "2025-01-25T10:00:00"
        })

        # Unchanged entity (same or older timestamp) should not sync
        should_sync = sync._should_sync("stagiaire", "unchanged123", "2025-01-24T10:00:00")

        assert should_sync is False, "Unchanged entities should not be synced"


# ==================== INTEGRATION TESTS ====================

class TestEndToEndIntegration:
    """End-to-end integration tests"""

    def test_gmail_categorization_real_examples(self):
        """Test real-world email categorization examples"""
        from integrations.gmail_sync import GmailSync

        sync = GmailSync.__new__(GmailSync)
        sync.category_keywords = {
            "support": ["help", "issue", "problem", "bug", "error", "panne", "dépannage"],
            "sales": ["devis", "quote", "price", "tarif", "commande"],
            "administrative": ["facture", "invoice", "payment", "contract"]
        }

        # Real examples
        examples = [
            ("Mon ordinateur est en panne", "support"),
            ("Demande de devis pour formation Excel", "sales"),
            ("Facture du mois de janvier", "administrative"),
            ("Problème de connexion internet", "support"),
            ("Quel est le tarif pour une maintenance?", "sales")
        ]

        for text, expected_category in examples:
            category = sync._categorize_email(text, "")
            assert category == expected_category, \
                f"Text '{text}' should be categorized as '{expected_category}', got '{category}'"


# ==================== PYTEST CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
