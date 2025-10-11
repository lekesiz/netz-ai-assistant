"""
Integration tests for Security API endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime


class TestSecurityEndpoints:
    """Test security-related API endpoints"""
    
    @pytest.mark.integration
    def test_login_success(self, test_client: TestClient):
        """Test successful login"""
        response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@netzinformatique.fr"
        assert "admin" in data["user"]["permissions"]
    
    @pytest.mark.integration
    def test_login_failure(self, test_client: TestClient):
        """Test failed login"""
        response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    @pytest.mark.integration
    def test_rate_limiting(self, test_client: TestClient):
        """Test rate limiting on login"""
        # Make multiple login attempts
        for i in range(6):  # One more than limit
            response = test_client.post(
                "/api/security/login",
                json={
                    "email": f"test{i}@example.com",
                    "password": "password"
                }
            )
            
            if i < 5:
                # Should work for first 5 attempts
                assert response.status_code in [401, 422]  # Wrong creds or validation error
            else:
                # 6th attempt should be rate limited
                assert response.status_code == 429
    
    @pytest.mark.integration
    def test_api_key_creation(self, test_client: TestClient):
        """Test API key creation"""
        # First login to get token
        login_response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Create API key
        response = test_client.post(
            "/api/security/api-keys",
            json={
                "name": "Test API Key",
                "permissions": ["read", "write"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["api_key"].startswith("netz-")
        assert data["name"] == "Test API Key"
        assert data["permissions"] == ["read", "write"]
    
    @pytest.mark.integration
    def test_api_key_list(self, test_client: TestClient):
        """Test listing API keys"""
        # Login
        login_response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        token = login_response.json()["access_token"]
        
        # List API keys
        response = test_client.get(
            "/api/security/api-keys",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "api_keys" in data
        assert isinstance(data["api_keys"], list)
    
    @pytest.mark.integration
    def test_unauthorized_access(self, test_client: TestClient):
        """Test unauthorized access to admin endpoints"""
        # Try to access without token
        response = test_client.get("/api/security/api-keys")
        assert response.status_code == 403
        
        # Try with invalid token
        response = test_client.get(
            "/api/security/api-keys",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 403
    
    @pytest.mark.integration
    def test_security_headers(self, test_client: TestClient):
        """Test security headers are present"""
        response = test_client.get("/health")
        
        # Check security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Strict-Transport-Security")
        assert response.headers.get("Content-Security-Policy")
    
    @pytest.mark.integration
    def test_input_sanitization(self, test_client: TestClient):
        """Test input sanitization on chat endpoint"""
        # Try XSS attack
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{
                    "role": "user",
                    "content": "<script>alert('xss')</script>What is NETZ?"
                }]
            }
        )
        
        # Should reject due to security validation
        assert response.status_code == 422
        assert "Security validation failed" in str(response.json())
    
    @pytest.mark.integration
    def test_sql_injection_prevention(self, test_client: TestClient):
        """Test SQL injection prevention"""
        response = test_client.post(
            "/api/chat",
            json={
                "messages": [{
                    "role": "user",
                    "content": "'; DROP TABLE users; --"
                }]
            }
        )
        
        assert response.status_code == 422
        assert "Security validation failed" in str(response.json())
    
    @pytest.mark.integration
    def test_api_key_authentication(self, test_client: TestClient):
        """Test API key authentication"""
        # Create an API key first
        login_response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        token = login_response.json()["access_token"]
        
        key_response = test_client.post(
            "/api/security/api-keys",
            json={"name": "Test Key", "permissions": ["read"]},
            headers={"Authorization": f"Bearer {token}"}
        )
        api_key = key_response.json()["api_key"]
        
        # Use API key for chat
        with patch("ollama.chat") as mock_chat:
            mock_chat.return_value = {"message": {"content": "Test response"}}
            
            response = test_client.post(
                "/api/chat",
                json={
                    "messages": [{"role": "user", "content": "Hello"}]
                },
                headers={"X-API-Key": api_key}
            )
            
            assert response.status_code == 200
    
    @pytest.mark.integration
    def test_audit_logging(self, test_client: TestClient):
        """Test audit logging functionality"""
        # Login (should create audit log)
        login_response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get audit logs
        response = test_client.get(
            "/api/security/audit-logs?event_type=successful_login",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        logs = response.json()["logs"]
        assert any(log["event_type"] == "successful_login" for log in logs)
    
    @pytest.mark.integration
    def test_blocked_ip_management(self, test_client: TestClient):
        """Test blocked IP management"""
        # Login
        login_response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get blocked IPs
        response = test_client.get(
            "/api/security/blocked-ips",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "blocked_ips" in response.json()
    
    @pytest.mark.integration
    def test_security_stats(self, test_client: TestClient):
        """Test security statistics endpoint"""
        # Login
        login_response = test_client.post(
            "/api/security/login",
            json={
                "email": "admin@netzinformatique.fr",
                "password": "changeme123"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get stats
        response = test_client.get(
            "/api/security/security-stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        stats = response.json()["stats"]
        assert "blocked_ips" in stats
        assert "api_keys_active" in stats
        assert "events_24h" in stats