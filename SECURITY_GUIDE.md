# 🔐 NETZ AI Security Guide

## Overview

This guide covers the security features implemented in the NETZ AI system and best practices for deployment.

## 🛡️ Security Features

### 1. Authentication & Authorization

#### JWT Authentication
- Token-based authentication for admin users
- 24-hour token expiration
- Secure token generation with HS256 algorithm

#### API Key Authentication
- API keys for programmatic access
- Permission-based access control
- Key prefix display for security

### 2. Rate Limiting

- **Default Limits**:
  - Chat endpoint: 30 requests/minute
  - Login endpoint: 5 requests/minute
  - General API: 60 requests/minute, 1000 requests/hour

- **Configuration**:
  ```python
  @limiter.limit("30/minute")
  async def chat(request: ChatRequest, ...):
  ```

### 3. Input Validation & Sanitization

#### XSS Prevention
- HTML sanitization using bleach
- Allowed tags: `<p>`, `<br>`, `<strong>`, `<em>`, `<u>`, `<a>`
- All user inputs sanitized before processing

#### SQL Injection Prevention
- Parameterized queries
- Input sanitization for SQL-like patterns
- Pattern detection and blocking

#### Path Traversal Prevention
- File path validation
- Directory traversal pattern blocking

### 4. Security Headers

All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy`

### 5. Request Size Limiting

- Maximum request body: 10MB
- File upload restrictions:
  - Allowed extensions: .txt, .pdf, .doc, .docx, .png, .jpg, .jpeg
  - Content type validation

### 6. IP Blocking

- Automatic blocking after 6 failed attempts
- Manual IP management via admin API
- Blocked IP list persistence

### 7. Audit Logging

All security events logged:
- Login attempts (success/failure)
- API key creation/revocation
- Permission changes
- Suspicious activity

## 🚀 Deployment Security Checklist

### Environment Variables

```bash
# Required for production
JWT_SECRET=<32+ character secret>
ADMIN_PASSWORD=<strong password>

# Optional but recommended
ALLOWED_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=30
```

### Pre-deployment Steps

1. **Change Default Credentials**
   ```python
   # In security_api.py, update:
   ADMIN_USERS = {
       "admin@yourdomain.com": {
           "password_hash": hash_password("your-secure-password")
       }
   }
   ```

2. **Generate Strong JWT Secret**
   ```python
   import secrets
   jwt_secret = secrets.token_hex(32)
   # Set as JWT_SECRET environment variable
   ```

3. **Configure CORS**
   ```python
   # Update allowed origins in security_middleware.py
   "allowed_origins": ["https://yourdomain.com"]
   ```

4. **Enable HTTPS**
   - Use reverse proxy (Nginx/Apache) with SSL
   - Redirect HTTP to HTTPS
   - Enable HSTS header

5. **Database Security**
   - Use environment variables for connection strings
   - Enable SSL for database connections
   - Regular backups

### API Security Usage

#### Obtaining Admin Token
```bash
curl -X POST https://api.yourdomain.com/api/security/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourdomain.com",
    "password": "your-password"
  }'
```

#### Creating API Keys
```bash
curl -X POST https://api.yourdomain.com/api/security/api-keys \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production App",
    "permissions": ["read", "write"]
  }'
```

#### Using API Keys
```bash
curl -X POST https://api.yourdomain.com/api/chat \
  -H "X-API-Key: netz-xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## 🔍 Security Monitoring

### 1. Audit Log Review
```bash
# View recent security events
curl -X GET https://api.yourdomain.com/api/security/audit-logs \
  -H "Authorization: Bearer <admin-token>"
```

### 2. Security Statistics
```bash
# Get security metrics
curl -X GET https://api.yourdomain.com/api/security/security-stats \
  -H "Authorization: Bearer <admin-token>"
```

### 3. Blocked IPs Management
```bash
# List blocked IPs
curl -X GET https://api.yourdomain.com/api/security/blocked-ips \
  -H "Authorization: Bearer <admin-token>"

# Unblock an IP
curl -X POST https://api.yourdomain.com/api/security/blocked-ips/1.2.3.4/unblock \
  -H "Authorization: Bearer <admin-token>"
```

## 🚨 Security Best Practices

### 1. Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Apply patches promptly

### 2. Access Control
- Use least privilege principle
- Regular API key rotation
- Remove unused keys

### 3. Monitoring
- Set up alerts for failed logins
- Monitor rate limit violations
- Review audit logs daily

### 4. Backup & Recovery
- Regular database backups
- Test recovery procedures
- Keep offline backups

### 5. Network Security
- Use firewall rules
- Restrict database access
- VPN for admin access

## 📊 Security Metrics

Monitor these key metrics:
- Failed login attempts per hour
- API requests per user
- Response times (detect DoS)
- Error rates
- Blocked IP count

## 🆘 Incident Response

### If Compromised:
1. Rotate all secrets immediately
2. Review audit logs
3. Block suspicious IPs
4. Reset all API keys
5. Notify affected users

### Prevention:
1. Regular security audits
2. Penetration testing
3. Code security reviews
4. Dependency scanning

## 🔧 Advanced Configuration

### Custom Rate Limits
```python
# Per-user rate limiting
@limiter.limit("100/hour", key_func=lambda: current_user.id)
```

### IP Whitelist
```python
# Add to security_middleware.py
WHITELISTED_IPS = {"10.0.0.1", "192.168.1.1"}
```

### Custom Permissions
```python
# Add new permissions
@require_permission("financial_data_access")
async def get_financial_data():
    pass
```

---

## Summary

The NETZ AI security implementation provides:
- ✅ Multi-layer authentication (JWT + API Keys)
- ✅ Comprehensive input validation
- ✅ Rate limiting and DoS protection
- ✅ Security headers and CORS
- ✅ Audit logging and monitoring
- ✅ IP blocking and threat detection

Always prioritize security in production deployments!