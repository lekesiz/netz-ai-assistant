# NETZ Informatique Offline AI - Yazılım Stack ve Teknoloji Seçimi

## 🎯 Proje Gereksinimleri Özeti
- Tamamen offline çalışma
- Çoklu kullanıcı desteği
- Şirket verilerine özel eğitim
- Güvenli ve izole ortam
- Otomatik güncelleme yeteneği

## 🏗️ Teknoloji Stack'i

### 1. İşletim Sistemi
**Önerilen**: Ubuntu Server 22.04 LTS
- Uzun vadeli destek (2027'ye kadar)
- Geniş CUDA/GPU desteği
- Container teknolojileri için ideal
- Güvenlik güncellemeleri

**Alternatif**: Rocky Linux 9 (RedHat uyumlu)

### 2. Container ve Orchestration
```yaml
Container Runtime: Docker 24.0+
Orchestration: 
  - Development: Docker Compose
  - Production: Kubernetes (K3s - lightweight)
Registry: Harbor (self-hosted)
```

### 3. LLM Inference Stack

#### A. Model Serving Framework
**Ana Seçim**: **vLLM**
```bash
# Özellikleri:
- Yüksek throughput
- PagedAttention ile verimli bellek kullanımı
- Multi-GPU desteği
- OpenAI API uyumlu
```

#### B. Alternatifler
- **Ollama**: Basit kurulum, lokal model yönetimi
- **LocalAI**: OpenAI API drop-in replacement
- **Text Generation Inference (HuggingFace)**: Production-ready

### 4. Vector Database
**Ana Seçim**: **Qdrant**
```python
# Avantajları:
- On-premise deployment
- Yüksek performans
- REST/gRPC API
- Filtreleme yetenekleri
```

**Yedek**: Weaviate, ChromaDB

### 5. Frontend Stack

#### Web Interface
```javascript
Framework: Next.js 14 (App Router)
UI Library: shadcn/ui + Tailwind CSS
State Management: Zustand
Real-time: Socket.io
Auth: NextAuth.js + Keycloak
```

#### Desktop Application (Opsiyonel)
```javascript
Framework: Electron + Next.js
Auto-updater: electron-updater
Local storage: SQLite
```

### 6. Backend Architecture

#### API Gateway
**Kong Gateway** (Self-hosted)
- Rate limiting
- Authentication
- Request routing
- Analytics

#### Microservices
```yaml
Language: Python 3.11+
Framework: FastAPI
Task Queue: Celery + Redis
Message Broker: RabbitMQ
Cache: Redis
Database: PostgreSQL 15
```

### 7. Monitoring ve Logging

#### Observability Stack
```yaml
Metrics: Prometheus + Grafana
Logs: Loki + Promtail
Traces: Jaeger
Alerting: Alertmanager
```

#### AI-Specific Monitoring
- Model latency tracking
- Token usage analytics
- User query patterns
- Resource utilization

## 🔧 Geliştirme Araçları

### Version Control
```bash
Git: Lokal GitLab instance
CI/CD: GitLab CI veya Jenkins
Code Quality: SonarQube
```

### Development Environment
```yaml
IDE: VS Code + Remote Development
Linting: Black, ESLint, Prettier
Testing: pytest, Jest
Documentation: Sphinx + MkDocs
```

## 📦 Paket Yönetimi

### System Packages
```bash
# APT repository mirror (offline)
apt-mirror veya Aptly
```

### Python Packages
```bash
# Private PyPI server
pip install devpi-server
# veya
docker run -d pypiserver/pypiserver
```

### Container Images
```bash
# Harbor registry için offline sync
harbor-replication
skopeo sync
```

## 🏛️ Sistem Mimarisi

```
┌─────────────────┐     ┌─────────────────┐
│   Web Client    │     │ Desktop Client  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────┴──────┐
              │ Kong Gateway│
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────┴────┐ ┌───┴────┐ ┌───┴────┐
    │Chat API │ │Admin API│ │Data API│
    └────┬────┘ └────────┘ └────┬────┘
         │                       │
    ┌────┴────┐             ┌───┴────┐
    │  vLLM   │             │ Qdrant │
    └─────────┘             └────────┘
```

## 🚀 Deployment Stratejisi

### Phase 1: Development
```yaml
deployment:
  type: docker-compose
  services:
    - llm-server
    - vector-db
    - web-app
    - postgres
    - redis
```

### Phase 2: Production
```yaml
deployment:
  type: kubernetes
  namespace: netz-ai
  components:
    - ingress-nginx
    - cert-manager
    - metallb (load balancer)
```

## 📋 Kurulum Öncelikleri

1. **Temel Altyapı** (Hafta 1)
   - Ubuntu Server kurulumu
   - Docker & Docker Compose
   - NVIDIA drivers & CUDA

2. **LLM Stack** (Hafta 2)
   - vLLM kurulumu
   - Model indirme ve test
   - API endpoint konfigürasyonu

3. **Data Layer** (Hafta 3)
   - PostgreSQL setup
   - Qdrant vector DB
   - Redis cache

4. **Application Layer** (Hafta 4-5)
   - Backend API development
   - Frontend development
   - Authentication setup

5. **Integration** (Hafta 6)
   - Google Drive connector
   - Gmail integration
   - Web scraping setup

## 🔐 Güvenlik Gereksinimleri

### Network Security
- Air-gapped deployment seçeneği
- VPN-only access
- SSL/TLS everywhere

### Application Security
- OAuth2/OIDC (Keycloak)
- API key management
- Rate limiting
- Audit logging

### Data Security
- Encryption at rest
- Encryption in transit
- Regular backups
- Access control (RBAC)

---
*Son güncelleme: 2025-01-09*