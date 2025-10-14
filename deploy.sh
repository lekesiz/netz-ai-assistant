#!/bin/bash
# NETZ AI Production Deployment Script

set -e

echo "🚀 Starting NETZ AI Production Deployment..."

# Configuration
PROJECT_NAME="netz-ai"
BACKUP_DIR="/opt/backups/netz-ai"
LOG_FILE="/var/log/netz-ai-deploy.log"

# Create log file
mkdir -p $(dirname $LOG_FILE)
echo "$(date): Starting deployment" >> $LOG_FILE

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Create backup directory
echo "📁 Creating backup directory..."
mkdir -p $BACKUP_DIR/$(date +%Y%m%d_%H%M%S)

# Backup current deployment (if exists)
if [ -d "./production_data" ]; then
    echo "💾 Backing up current data..."
    cp -r ./production_data $BACKUP_DIR/$(date +%Y%m%d_%H%M%S)/
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Pull latest images
echo "📦 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

# Build application
echo "🔨 Building NETZ AI application..."
docker-compose -f docker-compose.prod.yml build

# Start services
echo "▶️ Starting NETZ AI services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for health check
echo "🏥 Waiting for health check..."
sleep 30

# Verify deployment
echo "✅ Verifying deployment..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "🎉 Deployment successful!"
    echo "$(date): Deployment successful" >> $LOG_FILE
    
    # Clean up old backups (keep last 5)
    find $BACKUP_DIR -type d -name "20*" | sort -r | tail -n +6 | xargs -r rm -rf
    
    echo "📊 Deployment Summary:"
    echo "   - Application: Running ✅"
    echo "   - Health Check: Passed ✅"
    echo "   - Backup: Created ✅"
    echo "   - Logs: $LOG_FILE"
    
else
    echo "❌ Health check failed. Rolling back..."
    echo "$(date): Deployment failed, rolling back" >> $LOG_FILE
    
    # Rollback
    docker-compose -f docker-compose.prod.yml down
    
    # Restore backup
    if [ -d "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)/production_data" ]; then
        cp -r $BACKUP_DIR/$(date +%Y%m%d_%H%M%S)/production_data ./
    fi
    
    exit 1
fi

echo "🚀 NETZ AI is now running in production!"
echo "   URL: https://netzinformatique.fr"
echo "   Admin: https://netzinformatique.fr/admin"
echo "   API Docs: https://netzinformatique.fr/docs"
