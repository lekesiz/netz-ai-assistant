#!/bin/bash
#
# NETZ Informatique AI System - Master Installation Script
# Version: 1.0.0
# Date: 2025-01-09
#

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/netz-ai"
DATA_DIR="/var/lib/netz-ai"
LOG_DIR="/var/log/netz-ai"
CONFIG_DIR="/etc/netz-ai"
BACKUP_DIR="/backup/netz-ai"

# Function definitions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

check_system() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine OS version"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]] || [[ "$VERSION_ID" != "22.04" ]]; then
        warning "This script is tested on Ubuntu 22.04. Current: $ID $VERSION_ID"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check hardware
    TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    TOTAL_MEM_GB=$((TOTAL_MEM / 1024 / 1024))
    
    if [[ $TOTAL_MEM_GB -lt 32 ]]; then
        error "Insufficient memory. Required: 32GB, Available: ${TOTAL_MEM_GB}GB"
        exit 1
    fi
    
    # Check GPU
    if ! command -v nvidia-smi &> /dev/null; then
        error "NVIDIA GPU driver not found. Please install CUDA drivers first."
        exit 1
    fi
    
    success "System requirements met"
}

create_directories() {
    log "Creating directory structure..."
    
    mkdir -p "$INSTALL_DIR"/{models,scripts,services,data}
    mkdir -p "$DATA_DIR"/{uploads,processed,embeddings,cache}
    mkdir -p "$LOG_DIR"/{app,system,audit}
    mkdir -p "$CONFIG_DIR"/{ssl,auth,models}
    mkdir -p "$BACKUP_DIR"/{daily,weekly,monthly}
    
    # Set permissions
    chmod 750 "$INSTALL_DIR"
    chmod 750 "$DATA_DIR"
    chmod 755 "$LOG_DIR"
    chmod 750 "$CONFIG_DIR"
    chmod 700 "$BACKUP_DIR"
    
    success "Directories created"
}

create_user() {
    log "Creating netz-ai system user..."
    
    if ! id "netz-ai" &>/dev/null; then
        useradd -r -s /bin/bash -d "$INSTALL_DIR" -c "NETZ AI System User" netz-ai
        usermod -aG docker netz-ai
    fi
    
    chown -R netz-ai:netz-ai "$INSTALL_DIR"
    chown -R netz-ai:netz-ai "$DATA_DIR"
    chown -R netz-ai:netz-ai "$LOG_DIR"
    
    success "User created"
}

install_dependencies() {
    log "Installing system dependencies..."
    
    apt-get update
    apt-get install -y \
        build-essential \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        python3-pip \
        git \
        wget \
        curl \
        jq \
        htop \
        iotop \
        nvtop \
        postgresql-14 \
        postgresql-contrib-14 \
        redis-server \
        nginx \
        certbot \
        python3-certbot-nginx \
        ufw \
        fail2ban \
        unattended-upgrades \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    success "Dependencies installed"
}

install_docker() {
    log "Installing Docker..."
    
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    fi
    
    # Configure Docker
    cat > /etc/docker/daemon.json <<EOF
{
    "data-root": "$DATA_DIR/docker",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF
    
    systemctl restart docker
    success "Docker installed"
}

install_nvidia_docker() {
    log "Installing NVIDIA Docker support..."
    
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
    
    apt-get update
    apt-get install -y nvidia-docker2
    systemctl restart docker
    
    # Test GPU access
    docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
    
    success "NVIDIA Docker support installed"
}

setup_python_env() {
    log "Setting up Python environment..."
    
    cd "$INSTALL_DIR"
    sudo -u netz-ai python3.11 -m venv venv
    
    # Activate and upgrade pip
    sudo -u netz-ai bash -c "source venv/bin/activate && pip install --upgrade pip setuptools wheel"
    
    # Install Python packages
    sudo -u netz-ai bash -c "source venv/bin/activate && pip install \
        torch==2.1.2+cu121 \
        transformers==4.36.2 \
        vllm==0.2.7 \
        langchain==0.1.0 \
        fastapi==0.108.0 \
        uvicorn==0.25.0 \
        pydantic==2.5.3 \
        sqlalchemy==2.0.25 \
        alembic==1.13.1 \
        redis==5.0.1 \
        celery==5.3.4 \
        psycopg2-binary==2.9.9 \
        qdrant-client==1.7.0 \
        google-auth==2.26.1 \
        google-api-python-client==2.114.0 \
        prometheus-client==0.19.0 \
        python-multipart==0.0.6 \
        python-jose[cryptography]==3.3.0 \
        passlib[bcrypt]==1.7.4 \
        python-dotenv==1.0.0"
    
    success "Python environment ready"
}

setup_postgresql() {
    log "Setting up PostgreSQL..."
    
    # Start PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user
    sudo -u postgres psql <<EOF
CREATE USER netzai WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';
CREATE DATABASE netzai_db OWNER netzai;
GRANT ALL PRIVILEGES ON DATABASE netzai_db TO netzai;

-- Create separate databases for different services
CREATE DATABASE keycloak_db OWNER netzai;
CREATE DATABASE kong_db OWNER netzai;
EOF
    
    # Configure PostgreSQL
    cat >> /etc/postgresql/14/main/postgresql.conf <<EOF

# NETZ AI Optimizations
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 20MB
min_wal_size = 1GB
max_wal_size = 4GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4
EOF
    
    systemctl restart postgresql
    success "PostgreSQL configured"
}

setup_redis() {
    log "Setting up Redis..."
    
    # Configure Redis
    cat >> /etc/redis/redis.conf <<EOF

# NETZ AI Configuration
maxmemory 4gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
requirepass CHANGE_ME_REDIS_PASSWORD
EOF
    
    systemctl restart redis-server
    systemctl enable redis-server
    
    success "Redis configured"
}

download_models() {
    log "Downloading AI models..."
    
    # Create model directory
    MODEL_DIR="$INSTALL_DIR/models"
    
    # Download Mistral 7B model
    if [[ ! -d "$MODEL_DIR/mistral-7b-instruct-v0.2" ]]; then
        sudo -u netz-ai bash -c "
            source $INSTALL_DIR/venv/bin/activate
            cd $MODEL_DIR
            python -c \"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='mistralai/Mistral-7B-Instruct-v0.2',
    local_dir='./mistral-7b-instruct-v0.2',
    local_dir_use_symlinks=False,
    resume_download=True
)
            \"
        "
    fi
    
    # Download embedding model
    if [[ ! -d "$MODEL_DIR/camembert-base" ]]; then
        sudo -u netz-ai bash -c "
            source $INSTALL_DIR/venv/bin/activate
            cd $MODEL_DIR
            python -c \"
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='dangvantuan/sentence-camembert-base',
    local_dir='./camembert-base',
    local_dir_use_symlinks=False,
    resume_download=True
)
            \"
        "
    fi
    
    success "Models downloaded"
}

setup_services() {
    log "Setting up system services..."
    
    # Copy service files
    cp "$INSTALL_DIR/services/"*.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable services
    systemctl enable netz-llm.service
    systemctl enable netz-api.service
    systemctl enable netz-worker.service
    systemctl enable netz-scheduler.service
    
    success "Services configured"
}

setup_nginx() {
    log "Setting up NGINX..."
    
    # Create NGINX configuration
    cat > /etc/nginx/sites-available/netz-ai <<EOF
server {
    listen 80;
    server_name netz-ai.local;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name netz-ai.local;
    
    ssl_certificate /etc/netz-ai/ssl/cert.pem;
    ssl_certificate_key /etc/netz-ai/ssl/key.pem;
    ssl_protocols TLSv1.3;
    ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/netz-ai /etc/nginx/sites-enabled/
    nginx -t
    systemctl restart nginx
    
    success "NGINX configured"
}

setup_firewall() {
    log "Setting up firewall..."
    
    # Configure UFW
    ufw --force enable
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (restricted)
    ufw allow from 192.168.1.0/24 to any port 22
    
    # Allow HTTPS
    ufw allow 443/tcp
    
    # Allow internal services
    ufw allow from 127.0.0.1 to any port 5432  # PostgreSQL
    ufw allow from 127.0.0.1 to any port 6379  # Redis
    ufw allow from 127.0.0.1 to any port 6333  # Qdrant
    ufw allow from 127.0.0.1 to any port 8000  # API
    ufw allow from 127.0.0.1 to any port 3000  # Frontend
    
    success "Firewall configured"
}

generate_ssl_cert() {
    log "Generating self-signed SSL certificate..."
    
    mkdir -p /etc/netz-ai/ssl
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/netz-ai/ssl/key.pem \
        -out /etc/netz-ai/ssl/cert.pem \
        -subj "/C=FR/ST=Doubs/L=Pontarlier/O=NETZ Informatique/CN=netz-ai.local"
    
    chmod 600 /etc/netz-ai/ssl/key.pem
    chmod 644 /etc/netz-ai/ssl/cert.pem
    
    success "SSL certificate generated"
}

setup_monitoring() {
    log "Setting up monitoring stack..."
    
    # Create monitoring compose file
    cat > "$INSTALL_DIR/docker-compose.monitoring.yml" <<EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: netz-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: netz-grafana
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=CHANGE_ME
      - GF_SECURITY_ADMIN_USER=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3001:3000"
    restart: unless-stopped

  loki:
    image: grafana/loki:latest
    container_name: netz-loki
    volumes:
      - ./monitoring/loki.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    ports:
      - "3100:3100"
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
  loki_data:
EOF
    
    cd "$INSTALL_DIR"
    docker compose -f docker-compose.monitoring.yml up -d
    
    success "Monitoring stack deployed"
}

final_steps() {
    log "Performing final configuration..."
    
    # Create systemd timer for backups
    cat > /etc/systemd/system/netz-backup.timer <<EOF
[Unit]
Description=NETZ AI Daily Backup Timer
Requires=netz-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF
    
    cat > /etc/systemd/system/netz-backup.service <<EOF
[Unit]
Description=NETZ AI Backup Service
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/netz-ai/scripts/backup.sh
User=netz-ai
Group=netz-ai
EOF
    
    systemctl enable netz-backup.timer
    systemctl start netz-backup.timer
    
    # Set up log rotation
    cat > /etc/logrotate.d/netz-ai <<EOF
$LOG_DIR/*/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 netz-ai netz-ai
    sharedscripts
    postrotate
        systemctl reload netz-api > /dev/null 2>&1 || true
    endscript
}
EOF
    
    success "Final configuration complete"
}

print_summary() {
    echo
    success "NETZ AI Installation Complete!"
    echo
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Installation Summary:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "• Install Directory: $INSTALL_DIR"
    echo "• Data Directory: $DATA_DIR"
    echo "• Config Directory: $CONFIG_DIR"
    echo "• Log Directory: $LOG_DIR"
    echo
    echo "Default Credentials (CHANGE IMMEDIATELY!):"
    echo "• PostgreSQL: netzai / CHANGE_ME_STRONG_PASSWORD"
    echo "• Redis: CHANGE_ME_REDIS_PASSWORD"
    echo "• Grafana: admin / CHANGE_ME"
    echo
    echo "Next Steps:"
    echo "1. Change all default passwords"
    echo "2. Configure SSL certificate (production)"
    echo "3. Update firewall rules for your network"
    echo "4. Start services:"
    echo "   systemctl start netz-llm"
    echo "   systemctl start netz-api"
    echo "   systemctl start netz-worker"
    echo
    echo "Access URLs:"
    echo "• Web Interface: https://netz-ai.local"
    echo "• API: https://netz-ai.local/api"
    echo "• Grafana: http://localhost:3001"
    echo "• Prometheus: http://localhost:9090"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main execution
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "NETZ Informatique AI System Installer"
    echo "Version 1.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    check_root
    check_system
    create_directories
    create_user
    install_dependencies
    install_docker
    install_nvidia_docker
    setup_python_env
    setup_postgresql
    setup_redis
    download_models
    setup_services
    setup_nginx
    setup_firewall
    generate_ssl_cert
    setup_monitoring
    final_steps
    print_summary
}

# Run main function
main "$@"