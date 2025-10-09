# NETZ AI - macOS Development Guide

## 🍎 M4 Max Development Environment Setup

### System Requirements Check
- ✅ M4 Max (CPU + GPU with Neural Engine)
- ✅ 128GB Unified Memory
- ✅ 2TB SSD Storage
- ✅ macOS Sonoma or later

## 🛠️ Phase 1: macOS Development Setup

### 1. Install Prerequisites

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install essential tools
brew install python@3.11 git docker colima kubectl helm

# Install development tools
brew install --cask visual-studio-code iterm2 postman

# Install database tools
brew install postgresql@15 redis

# Install Python ML tools
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install transformers accelerate sentencepiece
```

### 2. Docker Setup on Apple Silicon

```bash
# Install Colima (Docker for Mac alternative, better for M1/M2/M3/M4)
brew install colima docker docker-compose

# Start Colima with adequate resources
colima start --cpu 8 --memory 16 --disk 100 --vm-type=vz --vz-rosetta

# Verify Docker
docker run hello-world
```

### 3. Local LLM Testing with Ollama

```bash
# Install Ollama (optimized for Apple Silicon)
brew install ollama

# Start Ollama service
brew services start ollama

# Download and test Mistral model
ollama pull mistral
ollama run mistral "Bonjour, comment allez-vous?"
```

### 4. Python Environment Setup

```bash
# Create project directory
cd ~/Desktop/NETZ-AI-Project

# Create Python virtual environment
python3.11 -m venv venv_mac
source venv_mac/bin/activate

# Install core dependencies
pip install -r requirements_mac.txt
```

Create `requirements_mac.txt`:
```txt
# Core ML packages (macOS optimized)
torch==2.1.2
transformers==4.36.2
accelerate==0.25.0
sentencepiece==0.1.99

# LLM tools
langchain==0.1.0
openai==1.6.1
anthropic==0.8.0
google-generativeai==0.3.2

# Vector databases
qdrant-client==1.7.0
chromadb==0.4.22

# Web framework
fastapi==0.108.0
uvicorn==0.25.0
pydantic==2.5.3

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
redis==5.0.1

# Utils
python-dotenv==1.0.0
pytest==7.4.4
black==23.12.1
```

### 5. PostgreSQL Setup

```bash
# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb netzai_dev
psql netzai_dev

# In psql:
CREATE USER netzai_dev WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE netzai_dev TO netzai_dev;
\q
```

## 🧪 Phase 2: Local Testing

### 1. Test LLM Inference

Create `test_llm_mac.py`:
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def test_local_llm():
    # Use smaller model for testing
    model_name = "microsoft/phi-2"
    
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype=torch.float16,
        device_map="mps",  # Use Apple Metal Performance Shaders
        trust_remote_code=True
    )
    
    # Test inference
    prompt = "Qu'est-ce que NETZ Informatique?"
    inputs = tokenizer(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=100)
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"Response: {response}")

if __name__ == "__main__":
    test_local_llm()
```

### 2. Docker Compose for Local Development

Create `docker-compose.mac.yml`:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    platform: linux/arm64
    environment:
      POSTGRES_DB: netzai_dev
      POSTGRES_USER: netzai_dev
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    platform: linux/arm64
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant:latest
    platform: linux/arm64
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
```

### 3. API Development

Create `app_mac.py`:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama

app = FastAPI(title="NETZ AI Local API")

class QueryRequest(BaseModel):
    prompt: str
    model: str = "mistral"

@app.post("/api/chat")
async def chat(request: QueryRequest):
    try:
        response = ollama.chat(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}]
        )
        return {"response": response['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "platform": "macOS"}

# Run with: uvicorn app_mac:app --reload
```

## 🔄 Phase 3: Platform-Agnostic Development

### 1. Use Docker for Everything

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Platform Detection

```python
# platform_utils.py
import platform
import torch

def get_device():
    """Get appropriate device for current platform"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        if torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    elif system == "Linux":
        if torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    else:
        return "cpu"

def get_optimal_batch_size():
    """Get optimal batch size based on platform"""
    system = platform.system()
    
    if system == "Darwin":
        return 4  # Smaller for unified memory
    else:
        return 8  # Larger for dedicated GPU memory
```

## 📦 Phase 4: Migration Preparation

### 1. Export/Import Scripts

```bash
# export_mac_data.sh
#!/bin/bash

# Export PostgreSQL
pg_dump netzai_dev > backup/netzai_dev.sql

# Export Redis
redis-cli --rdb backup/redis_backup.rdb

# Export Qdrant
curl -X POST http://localhost:6333/snapshots

# Package everything
tar -czf netzai_backup_$(date +%Y%m%d).tar.gz backup/
```

### 2. Environment Configuration

Create `.env.mac` and `.env.ubuntu`:
```bash
# .env.mac
DATABASE_URL=postgresql://netzai_dev:dev_password@localhost:5432/netzai_dev
REDIS_URL=redis://localhost:6379
DEVICE=mps
MODEL_PATH=/Users/$USER/models

# .env.ubuntu  
DATABASE_URL=postgresql://netzai:prod_password@localhost:5432/netzai
REDIS_URL=redis://localhost:6379
DEVICE=cuda
MODEL_PATH=/opt/netz-ai/models
```

## ✅ Testing Checklist

### Local macOS Testing
- [ ] LLM inference works with MPS
- [ ] API endpoints respond correctly
- [ ] Database connections work
- [ ] Vector search functions properly
- [ ] Memory usage stays under 100GB
- [ ] Performance benchmarks recorded

### Docker Testing
- [ ] All services start correctly
- [ ] Cross-platform images work
- [ ] Volume mounts function properly
- [ ] Network connectivity verified

### Migration Readiness
- [ ] All code is platform-agnostic
- [ ] Docker images are multi-arch
- [ ] Data export/import tested
- [ ] Configuration separated by environment
- [ ] Documentation updated

## 🚀 Migration to Ubuntu

When ready to migrate:

1. **Export all data** using the backup scripts
2. **Push Docker images** to registry
3. **Clone repository** on Ubuntu server
4. **Import data** using restore scripts
5. **Update configurations** for production
6. **Run comprehensive tests**

## 💡 Tips for macOS Development

1. **Use Rosetta 2** for x86_64 compatibility when needed:
   ```bash
   docker run --platform linux/amd64 image:tag
   ```

2. **Monitor Memory** usage with Activity Monitor
   - Unified memory can be misleading
   - Watch for swap usage

3. **Use Metal Performance Shaders** (MPS) for GPU acceleration:
   ```python
   device = torch.device("mps")
   ```

4. **Optimize for Apple Silicon**:
   - Use native ARM64 binaries when possible
   - Avoid unnecessary architecture translation

5. **Test Resource Limits**:
   ```bash
   # Test with limited resources
   docker run --memory="8g" --cpus="4" your-image
   ```

---
*Last updated: 2025-01-09*