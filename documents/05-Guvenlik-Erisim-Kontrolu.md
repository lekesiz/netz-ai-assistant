# NETZ Informatique - Güvenlik ve Erişim Kontrolü Dokümanı

## 🔐 Güvenlik Mimarisi Genel Bakış

### Temel Prensipler
1. **Zero Trust Architecture** - Hiçbir kullanıcı veya cihaza güvenme
2. **Defense in Depth** - Çok katmanlı güvenlik
3. **Least Privilege** - Minimum yetki prensibi
4. **Data Encryption** - Veri şifreleme (rest & transit)
5. **Audit Everything** - Her işlemi kaydet

## 🏗️ Güvenlik Katmanları

### 1. Network Güvenliği

#### A. Air-Gapped Deployment (Önerilen)
```yaml
Fiziksel İzolasyon:
  - İnternet bağlantısı YOK
  - Dedicated VLAN
  - Fiziksel güvenlik duvarı
  
Veri Transferi:
  - USB kontrolü (sadece onaylı cihazlar)
  - Data diode (tek yönlü veri akışı)
  - Offline update mekanizması
```

#### B. Network Segmentation
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  DMZ Network    │     │ Application Net │     │   Data Network  │
│                 │     │                 │     │                 │
│  - Web Gateway  │────▶│  - API Server   │────▶│  - LLM Server   │
│  - Reverse Proxy│     │  - Auth Server  │     │  - Vector DB    │
│                 │     │                 │     │  - PostgreSQL   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

#### C. Firewall Kuralları
```bash
# iptables rules
# Sadece gerekli portlar açık
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -p tcp --dport 22 -m iprange --src-range 192.168.1.100-192.168.1.110 -j ACCEPT  # SSH (limited)
iptables -A INPUT -j DROP  # Diğer tüm trafiği reddet
```

### 2. Kimlik Doğrulama ve Yetkilendirme

#### A. Keycloak Setup
```yaml
# docker-compose.yml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
      - KC_DB=postgres
      - KC_DB_URL_HOST=postgres
      - KC_DB_USERNAME=keycloak
      - KC_DB_PASSWORD=${KC_DB_PASSWORD}
    command:
      - start
      - --optimized
      - --https-certificate-file=/opt/keycloak/certs/tls.crt
      - --https-certificate-key-file=/opt/keycloak/certs/tls.key
```

#### B. Multi-Factor Authentication (MFA)
```python
# mfa_config.py
MFA_METHODS = {
    'totp': {
        'enabled': True,
        'issuer': 'NETZ AI System',
        'algorithm': 'SHA256',
        'digits': 6,
        'period': 30
    },
    'hardware_token': {
        'enabled': True,
        'supported': ['YubiKey', 'Nitrokey']
    },
    'biometric': {
        'enabled': True,
        'methods': ['fingerprint', 'face_id']
    }
}
```

#### C. Role-Based Access Control (RBAC)
```python
# rbac_config.py
ROLES = {
    'admin': {
        'permissions': ['*'],
        'data_access': ['all'],
        'api_rate_limit': None
    },
    'manager': {
        'permissions': [
            'read:all',
            'write:reports',
            'manage:users'
        ],
        'data_access': ['company', 'projects', 'clients'],
        'api_rate_limit': 1000  # per hour
    },
    'employee': {
        'permissions': [
            'read:public',
            'read:internal_docs',
            'chat:ai'
        ],
        'data_access': ['public', 'procedures'],
        'api_rate_limit': 100
    },
    'guest': {
        'permissions': ['read:public'],
        'data_access': ['public'],
        'api_rate_limit': 10
    }
}
```

### 3. Data Encryption

#### A. Encryption at Rest
```python
# encryption_config.py
ENCRYPTION_CONFIG = {
    'algorithm': 'AES-256-GCM',
    'key_derivation': 'PBKDF2',
    'key_rotation': '90_days',
    'hsm_integration': True
}

# Database encryption
DATABASE_ENCRYPTION = {
    'transparent_data_encryption': True,
    'column_encryption': ['emails', 'phone_numbers', 'addresses'],
    'backup_encryption': True
}
```

#### B. Encryption in Transit
```yaml
# TLS Configuration
tls:
  version: "1.3"  # Minimum TLS 1.3
  cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_CHACHA20_POLY1305_SHA256
  certificate:
    type: "ECC"  # Elliptic Curve
    key_size: 384
  hsts:
    enabled: true
    max_age: 31536000
    include_subdomains: true
```

### 4. API Security

#### A. API Gateway Configuration
```python
# kong_config.py
KONG_PLUGINS = {
    'rate-limiting': {
        'minute': 60,
        'hour': 1000,
        'policy': 'local'
    },
    'jwt': {
        'key_claim_name': 'kid',
        'secret_is_base64': True,
        'claims_to_verify': ['exp', 'nbf']
    },
    'cors': {
        'origins': ['https://netz-ai.local'],
        'credentials': True,
        'max_age': 3600
    },
    'ip-restriction': {
        'whitelist': ['192.168.1.0/24']
    }
}
```

#### B. Input Validation
```python
# input_validator.py
from pydantic import BaseModel, validator
import re

class ChatInput(BaseModel):
    message: str
    context: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        # Injection prevention
        if re.search(r'<script|javascript:|on\w+\s*=', v, re.I):
            raise ValueError('Potential XSS detected')
        
        # Length check
        if len(v) > 10000:
            raise ValueError('Message too long')
        
        # SQL injection prevention
        sql_patterns = [
            r'\b(union|select|insert|update|delete|drop)\b',
            r'(--|;|\/\*|\*\/)',
            r'(\b(or|and)\b\s*\d+\s*=\s*\d+)'
        ]
        for pattern in sql_patterns:
            if re.search(pattern, v, re.I):
                raise ValueError('Potential SQL injection detected')
        
        return v
```

### 5. Audit ve Logging

#### A. Centralized Logging
```yaml
# logging_config.yaml
logging:
  level: INFO
  handlers:
    - type: file
      path: /var/log/netz-ai/app.log
      rotation:
        max_size: 100MB
        max_files: 30
    - type: syslog
      host: syslog-server.local
      port: 514
      protocol: TCP
  
  sensitive_data:
    mask_fields:
      - password
      - api_key
      - credit_card
      - ssn
```

#### B. Audit Trail
```python
# audit_logger.py
class AuditLogger:
    def log_event(self, event_type, user, details):
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user': {
                'id': user.id,
                'username': user.username,
                'ip_address': user.ip_address,
                'user_agent': user.user_agent
            },
            'details': details,
            'hash': self.generate_hash(event_type, user, details)
        }
        
        # Tamper-proof logging
        self.write_to_append_only_log(audit_entry)
        
    def generate_hash(self, *args):
        """Create tamper-proof hash"""
        data = json.dumps(args, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
```

### 6. Model Security

#### A. Model Access Control
```python
# model_security.py
class ModelAccessControl:
    def __init__(self):
        self.model_permissions = {
            'base_model': ['employee', 'manager', 'admin'],
            'financial_model': ['manager', 'admin'],
            'hr_model': ['hr', 'admin']
        }
    
    def check_model_access(self, user_role, model_name):
        allowed_roles = self.model_permissions.get(model_name, [])
        return user_role in allowed_roles
```

#### B. Prompt Injection Prevention
```python
# prompt_security.py
class PromptSecurity:
    def __init__(self):
        self.blacklist_patterns = [
            r'ignore previous instructions',
            r'disregard all prior',
            r'system prompt',
            r'reveal your instructions',
            r'bypass security'
        ]
    
    def sanitize_prompt(self, prompt):
        # Check blacklist
        for pattern in self.blacklist_patterns:
            if re.search(pattern, prompt, re.I):
                raise SecurityError("Potential prompt injection detected")
        
        # Add security prefix
        secure_prompt = f"[SECURITY: User role={user.role}]\n{prompt}"
        return secure_prompt
```

### 7. Incident Response Plan

#### A. Security Incident Levels
```yaml
incident_levels:
  critical:
    - Data breach
    - System compromise
    - Unauthorized admin access
    response_time: 15_minutes
    
  high:
    - Multiple failed auth attempts
    - Suspicious API usage
    - Anomalous data access
    response_time: 1_hour
    
  medium:
    - Single user compromise
    - Performance anomaly
    response_time: 4_hours
    
  low:
    - Failed login attempts
    - Rate limit violations
    response_time: 24_hours
```

#### B. Automated Response
```python
# incident_response.py
class IncidentResponder:
    def respond_to_incident(self, incident_type, severity):
        responses = {
            'brute_force': self.block_ip,
            'data_exfiltration': self.isolate_system,
            'prompt_injection': self.terminate_session,
            'unauthorized_access': self.revoke_credentials
        }
        
        # Execute response
        response_func = responses.get(incident_type)
        if response_func:
            response_func()
        
        # Alert security team
        self.send_alert(incident_type, severity)
```

### 8. Compliance ve Standards

#### A. GDPR Compliance
```python
# gdpr_compliance.py
GDPR_FEATURES = {
    'right_to_access': True,
    'right_to_erasure': True,
    'data_portability': True,
    'consent_management': True,
    'breach_notification': '72_hours',
    'privacy_by_design': True,
    'data_minimization': True
}
```

#### B. Security Standards
- ISO 27001 compliance
- SOC 2 Type II
- OWASP Top 10 mitigation
- CIS Controls implementation

## 🔧 Security Hardening Checklist

### System Level
- [ ] Disable unnecessary services
- [ ] Regular security updates
- [ ] Kernel hardening (sysctl)
- [ ] SELinux/AppArmor enabled
- [ ] Secure boot enabled

### Application Level
- [ ] Dependencies scanning
- [ ] Static code analysis
- [ ] Dynamic security testing
- [ ] Penetration testing
- [ ] Security headers configured

### Operational Level
- [ ] Security training for staff
- [ ] Regular security audits
- [ ] Incident response drills
- [ ] Backup verification
- [ ] Access review (quarterly)

## 📊 Security Monitoring Dashboard

```python
# monitoring_metrics.py
SECURITY_METRICS = {
    'authentication': {
        'failed_login_attempts': 'prometheus_counter',
        'successful_logins': 'prometheus_counter',
        'mfa_usage': 'prometheus_gauge',
        'session_duration': 'prometheus_histogram'
    },
    'api_security': {
        'rate_limit_violations': 'prometheus_counter',
        'blocked_requests': 'prometheus_counter',
        'response_times': 'prometheus_histogram',
        'error_rates': 'prometheus_gauge'
    },
    'data_access': {
        'sensitive_data_access': 'prometheus_counter',
        'bulk_data_exports': 'prometheus_counter',
        'anomalous_queries': 'prometheus_counter'
    }
}
```

---
*Son güncelleme: 2025-01-09*