# 🚀 NETZ AI Production Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Deployment Methods](#deployment-methods)
4. [Security Configuration](#security-configuration)
5. [Monitoring Setup](#monitoring-setup)
6. [Backup & Recovery](#backup--recovery)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

## 🔧 Prerequisites

### System Requirements
- **CPU**: Minimum 4 cores, recommended 8 cores
- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: Minimum 50GB SSD
- **OS**: Ubuntu 20.04+ or similar Linux distribution

### Software Requirements
```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose

# Required tools
sudo apt-get update
sudo apt-get install -y git curl wget nginx certbot python3-certbot-nginx
```

### Domain & SSL
- Domain name pointing to your server
- SSL certificates (Let's Encrypt recommended)

## 🔐 Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/netz-ai.git
cd netz-ai/backend
```

### 2. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Generate secure secrets
openssl rand -hex 32  # For JWT_SECRET
openssl rand -base64 32  # For ADMIN_PASSWORD
```

### 3. Edit .env File
```bash
# Critical settings to update:
JWT_SECRET=<your-generated-secret>
ADMIN_PASSWORD=<your-secure-password>
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://netzai:password@localhost:5432/netzai
REDIS_PASSWORD=<redis-password>
```

## 🚀 Deployment Methods

### Method 1: Docker Compose (Recommended)
```bash
# Deploy all services
./scripts/deploy.sh production

# Or manually:
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Method 2: Kubernetes
```yaml
# Save as netz-ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: netz-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: netz-ai
  template:
    metadata:
      labels:
        app: netz-ai
    spec:
      containers:
      - name: netz-ai
        image: netz-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
```

### Method 3: Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/netz-ai.service

[Unit]
Description=NETZ AI API Service
After=network.target

[Service]
Type=exec
User=netzai
WorkingDirectory=/opt/netz-ai
Environment="PATH=/usr/local/bin:/usr/bin"
ExecStart=/usr/local/bin/uvicorn simple_api:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable netz-ai
sudo systemctl start netz-ai
```

## 🔒 Security Configuration

### 1. SSL/TLS Setup
```bash
# Using Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Firewall Configuration
```bash
# UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Nginx Configuration
```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/netz-ai
sudo ln -s /etc/nginx/sites-available/netz-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. API Security
```bash
# Create admin user
curl -X POST https://api.yourdomain.com/api/security/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@yourdomain.com", "password": "your-password"}'

# Generate API key
curl -X POST https://api.yourdomain.com/api/security/api-keys \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Production App", "permissions": ["read", "write"]}'
```

## 📊 Monitoring Setup

### 1. Prometheus & Grafana
```bash
# Access Grafana
# URL: http://your-server:3000
# Default: admin/netzai_grafana_password

# Import dashboard
# Dashboard ID: 15749 (FastAPI metrics)
```

### 2. Health Monitoring
```bash
# Start health monitoring
./scripts/health_check.sh &

# One-time health check
./scripts/health_check.sh once

# Configure alerts (edit script)
export SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export EMAIL_ALERTS="admin@yourdomain.com"
```

### 3. Logging
```bash
# View logs
docker-compose logs -f netz-api

# Log aggregation
# Configure rsyslog or use ELK stack
```

## 💾 Backup & Recovery

### 1. Automated Backups
```bash
# Create backup script
cat > /opt/netz-ai/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/netz-ai/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Database backup
docker exec netz-postgres pg_dump -U netzai netzai > "$BACKUP_DIR/database.sql"

# Data directories
tar -czf "$BACKUP_DIR/data.tar.gz" /data/netz_ai/

# Keep last 30 days
find /backups/netz-ai -type d -mtime +30 -exec rm -rf {} +
EOF

# Schedule with cron
echo "0 2 * * * /opt/netz-ai/backup.sh" | crontab -
```

### 2. Recovery Process
```bash
# Restore database
docker exec -i netz-postgres psql -U netzai netzai < backup/database.sql

# Restore data
tar -xzf backup/data.tar.gz -C /
```

## 🔧 Troubleshooting

### Common Issues

#### 1. API Not Responding
```bash
# Check services
docker-compose ps
docker-compose logs netz-api

# Restart services
docker-compose restart netz-api

# Check health
curl http://localhost:8000/health
```

#### 2. High Memory Usage
```bash
# Check memory
docker stats

# Limit container memory
# Add to docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

#### 3. Database Connection Issues
```bash
# Test connection
docker exec -it netz-postgres psql -U netzai -d netzai

# Check logs
docker-compose logs postgres
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
docker-compose up
```

## 🛠️ Maintenance

### 1. Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
./scripts/deploy.sh production
```

### 2. Database Maintenance
```bash
# Vacuum database
docker exec netz-postgres vacuumdb -U netzai -d netzai -z

# Reindex
docker exec netz-postgres reindexdb -U netzai -d netzai
```

### 3. Model Updates
```bash
# Pull new models
docker exec netz-ollama ollama pull mistral:latest
docker exec netz-ollama ollama pull llama3.2:latest
```

### 4. Security Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild image
docker-compose build --no-cache netz-api
```

## 📊 Performance Tuning

### 1. API Optimization
```python
# In config.py
API_WORKERS = 4  # Adjust based on CPU cores
CACHE_TTL = 3600  # Increase for stable data
MAX_CONCURRENT_REQUESTS = 100  # Adjust based on load
```

### 2. Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_created_at ON audit_logs(created_at);
CREATE INDEX idx_user_id ON api_keys(user_id);
```

### 3. Nginx Optimization
```nginx
# In nginx.conf
worker_processes auto;
worker_connections 2048;
keepalive_timeout 65;
keepalive_requests 100;
```

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Database initialized
- [ ] Admin credentials changed
- [ ] Monitoring setup
- [ ] Backup script scheduled
- [ ] Health checks passing
- [ ] API endpoints tested
- [ ] Documentation updated

## 🆘 Support

- **Logs**: `/var/log/netz_ai/`
- **Metrics**: `http://your-server:9090/metrics`
- **Health**: `https://api.yourdomain.com/health`
- **Documentation**: [API Docs](https://api.yourdomain.com/docs)

---

## 📝 Quick Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart netz-api

# Check health
curl https://api.yourdomain.com/health

# Run tests
docker run --rm -v $(pwd):/app python:3.11 pytest

# Backup
./scripts/backup.sh

# Deploy
./scripts/deploy.sh production
```

---

*Last Updated: 2025-01-10*
*Version: 1.0*