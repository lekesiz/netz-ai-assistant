"""
Unit tests for Security Middleware
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta
from security_middleware import (
    SecurityManager, hash_password, verify_password,
    validate_email, validate_url, sanitize_sql_param,
    validate_file_upload, sanitize_html
)


class TestSecurityManager:
    """Test security manager functionality"""
    
    @pytest.fixture
    def security_manager(self):
        """Create test security manager"""
        return SecurityManager()
    
    @pytest.mark.unit
    def test_generate_api_key(self, security_manager):
        """Test API key generation"""
        api_key = security_manager.generate_api_key("test_user", ["read", "write"])
        
        assert api_key.startswith("netz-")
        assert len(api_key) == 37  # netz- + 32 hex chars
        assert api_key in security_manager.api_keys
        
        key_data = security_manager.api_keys[api_key]
        assert key_data["name"] == "test_user"
        assert key_data["permissions"] == ["read", "write"]
    
    @pytest.mark.unit
    def test_validate_api_key(self, security_manager):
        """Test API key validation"""
        api_key = security_manager.generate_api_key("test", ["read"])
        
        # Valid key
        data = security_manager.validate_api_key(api_key)
        assert data is not None
        assert data["name"] == "test"
        
        # Invalid key
        assert security_manager.validate_api_key("invalid-key") is None
    
    @pytest.mark.unit
    def test_jwt_token_generation(self, security_manager):
        """Test JWT token generation and validation"""
        user_id = "test@example.com"
        permissions = ["read", "write"]
        
        token = security_manager.generate_jwt_token(user_id, permissions)
        assert isinstance(token, str)
        
        # Validate token
        payload = security_manager.validate_jwt_token(token)
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["permissions"] == permissions
    
    @pytest.mark.unit
    def test_jwt_token_expiration(self, security_manager):
        """Test JWT token expiration"""
        # Create token with short expiration
        payload = {
            "user_id": "test",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, security_manager.jwt_secret, algorithm="HS256")
        
        # Should return None for expired token
        assert security_manager.validate_jwt_token(token) is None
    
    @pytest.mark.unit
    def test_failed_attempts_tracking(self, security_manager):
        """Test tracking of failed authentication attempts"""
        ip = "192.168.1.1"
        
        # Track multiple attempts
        for _ in range(3):
            security_manager.track_failed_attempt(ip)
        
        assert len(security_manager.failed_attempts[ip]) == 3
        
        # Should not block after 3 attempts
        assert not security_manager.is_ip_blocked(ip)
        
        # Track more attempts to trigger blocking
        for _ in range(3):
            security_manager.track_failed_attempt(ip)
        
        # Should be blocked after 6 attempts
        assert security_manager.is_ip_blocked(ip)
    
    @pytest.mark.unit
    def test_input_validation(self, security_manager):
        """Test input validation for security threats"""
        # SQL injection attempts
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "javascript:alert(1)",
            "../../../etc/passwd",
            "union select * from users"
        ]
        
        for dangerous_input in dangerous_inputs:
            is_valid, error = security_manager.validate_input(dangerous_input)
            assert not is_valid, f"Should reject: {dangerous_input}"
            assert error is not None
        
        # Safe inputs
        safe_inputs = [
            "What is NETZ?",
            "Bonjour, comment allez-vous?",
            "Please help me with Python training"
        ]
        
        for safe_input in safe_inputs:
            is_valid, error = security_manager.validate_input(safe_input)
            assert is_valid, f"Should accept: {safe_input}"
            assert error is None


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    @pytest.mark.unit
    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert ":" in hashed  # Should contain salt:hash
        salt, hash_part = hashed.split(":")
        assert len(salt) == 32  # 16 bytes hex
        assert len(hash_part) == 64  # 32 bytes hex
    
    @pytest.mark.unit
    def test_verify_password(self):
        """Test password verification"""
        password = "secure_password_456"
        hashed = hash_password(password)
        
        # Correct password
        assert verify_password(password, hashed)
        
        # Wrong password
        assert not verify_password("wrong_password", hashed)
        
        # Invalid hash format
        assert not verify_password(password, "invalid_hash")
    
    @pytest.mark.unit
    def test_unique_hashes(self):
        """Test that same password produces different hashes"""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different salts


class TestInputValidation:
    """Test input validation utilities"""
    
    @pytest.mark.unit
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@company.fr",
            "admin+tag@netzinformatique.fr"
        ]
        
        for email in valid_emails:
            assert validate_email(email), f"Should accept: {email}"
        
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com"
        ]
        
        for email in invalid_emails:
            assert not validate_email(email), f"Should reject: {email}"
    
    @pytest.mark.unit
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://example.com",
            "http://www.example.com/path",
            "https://sub.domain.com:8080/path?query=1"
        ]
        
        for url in valid_urls:
            assert validate_url(url), f"Should accept: {url}"
        
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Only http/https
            "javascript:alert(1)",
            "//example.com"  # No protocol
        ]
        
        for url in invalid_urls:
            assert not validate_url(url), f"Should reject: {url}"
    
    @pytest.mark.unit
    def test_sql_sanitization(self):
        """Test SQL parameter sanitization"""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM users"
        ]
        
        for input_str in dangerous_inputs:
            sanitized = sanitize_sql_param(input_str)
            assert "'" not in sanitized
            assert ";" not in sanitized
            assert "--" not in sanitized
    
    @pytest.mark.unit
    def test_html_sanitization(self):
        """Test HTML sanitization"""
        # Dangerous HTML
        dangerous = '<script>alert("xss")</script><p>Hello</p>'
        sanitized = sanitize_html(dangerous)
        assert "<script>" not in sanitized
        assert "<p>Hello</p>" in sanitized
        
        # Allowed tags
        safe = '<p>Hello <strong>world</strong> <a href="http://example.com">link</a></p>'
        sanitized = sanitize_html(safe)
        assert "<strong>world</strong>" in sanitized
        assert '<a href="http://example.com"' in sanitized


class TestFileUploadValidation:
    """Test file upload validation"""
    
    @pytest.mark.unit
    def test_allowed_files(self):
        """Test allowed file types"""
        allowed_files = [
            ("document.txt", "text/plain"),
            ("report.pdf", "application/pdf"),
            ("image.png", "image/png"),
            ("photo.jpg", "image/jpeg")
        ]
        
        for filename, content_type in allowed_files:
            is_valid, error = validate_file_upload(filename, content_type)
            assert is_valid, f"Should allow: {filename}"
            assert error is None
    
    @pytest.mark.unit
    def test_blocked_files(self):
        """Test blocked file types"""
        blocked_files = [
            ("script.exe", "application/octet-stream"),
            ("virus.bat", "text/plain"),
            ("hack.php", "text/php"),
            ("shell.sh", "text/plain")
        ]
        
        for filename, content_type in blocked_files:
            is_valid, error = validate_file_upload(filename, content_type)
            assert not is_valid, f"Should block: {filename}"
            assert error is not None
    
    @pytest.mark.unit
    def test_path_traversal(self):
        """Test path traversal prevention"""
        dangerous_names = [
            "../../../etc/passwd",
            "..\\windows\\system32\\config",
            "uploads/../../../secret.txt"
        ]
        
        for filename in dangerous_names:
            is_valid, error = validate_file_upload(filename, "text/plain")
            assert not is_valid, f"Should block path traversal: {filename}"