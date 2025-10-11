# NETZ AI Assistant - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- macOS with M4 Max (or compatible Apple Silicon)
- 16GB+ RAM recommended
- 50GB+ free disk space
- Node.js 18+
- Python 3.11+
- Docker/Colima

### One-Command Start
```bash
cd /Users/mikail/Desktop/NETZ-AI-Project
./scripts/start-all.sh
```

This will start all services:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)
- Ollama (port 11434)
- Backend API (port 8000)
- Frontend (port 3000)

### Access Points
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## 📦 Manual Installation

### 1. Backend Setup
```bash
cd backend
source ../venv_mac/bin/activate
pip install -r requirements_mac.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure:
- `PENNYLANE_API_KEY`: Your PennyLane API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## 🔧 Service Management

### Start Individual Services

**PostgreSQL**
```bash
brew services start postgresql@15
```

**Redis**
```bash
brew services start redis
```

**Qdrant**
```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant
```

**Ollama**
```bash
ollama serve
```

**Backend API**
```bash
cd backend
source ../venv_mac/bin/activate
python main.py
```

**Frontend**
```bash
cd frontend
npm run dev
```

### Stop All Services
```bash
./scripts/stop-all.sh
```

## 📊 Data Management

### Initial Data Ingestion

1. **Google Drive Documents**
```bash
curl -X POST http://localhost:8000/api/data/update/google_drive
```

2. **PennyLane Financial Data**
```bash
curl -X POST http://localhost:8000/api/data/update/pennylane
```

### Check Data Status
```bash
curl http://localhost:8000/api/data/status
```

### Manual Data Ingestion
```python
cd backend
python pennylane_ingestion.py
```

## 🔐 Security Configuration

### Production Checklist
- [ ] Change all default passwords
- [ ] Update `SECRET_KEY` in `.env`
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up user authentication
- [ ] Enable audit logging
- [ ] Regular backup schedule

### API Key Management
Store API keys securely:
```bash
# Never commit .env files
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Qdrant Not Starting**
```bash
# Remove old container
docker rm -f qdrant
# Restart
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

**Frontend Build Errors**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

**Database Connection Issues**
```bash
# Check PostgreSQL status
brew services list
# Restart if needed
brew services restart postgresql@15
```

### Logs Location
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`
- System: Check with `brew services list`

## 📈 Performance Optimization

### Memory Usage
Monitor with Activity Monitor or:
```bash
# Check Python memory
ps aux | grep python
# Check Node memory
ps aux | grep node
```

### Database Optimization
```sql
-- Vacuum and analyze
VACUUM ANALYZE;
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Vector Database
- Optimize collection size
- Regular index rebuilding
- Monitor query performance

## 🔄 Updates and Maintenance

### Update Dependencies
```bash
# Backend
cd backend
pip install --upgrade -r requirements_mac.txt

# Frontend
cd frontend
npm update
```

### Backup Data
```bash
# Database backup
pg_dump netzai_dev > backup_$(date +%Y%m%d).sql

# Vector database backup
docker exec qdrant qdrant-backup create /qdrant/backup/
```

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Check all services
./scripts/health-check.sh
```

## 🚢 Production Deployment

### Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Ubuntu Server Migration
See `documents/09-Ubuntu-Migration-Guide.md`

### Monitoring Setup
- Prometheus metrics endpoint: `/metrics`
- Grafana dashboards available
- Alert configuration in `configs/alerts.yml`

## 📞 Support

**Technical Issues**
- Email: support@netzinformatique.fr
- Phone: +33 3 67 31 02 01

**Documentation**
- API Docs: http://localhost:8000/docs
- Project Docs: `/documents` folder

---
*Last updated: 2025-01-10*