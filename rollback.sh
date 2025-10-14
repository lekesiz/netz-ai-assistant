#!/bin/bash
# NETZ AI Rollback Script

BACKUP_DIR="/opt/backups/netz-ai"
LATEST_BACKUP=$(ls -1t $BACKUP_DIR | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backups found"
    exit 1
fi

echo "🔄 Rolling back to backup: $LATEST_BACKUP"

# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Restore backup
if [ -d "$BACKUP_DIR/$LATEST_BACKUP/production_data" ]; then
    rm -rf ./production_data
    cp -r $BACKUP_DIR/$LATEST_BACKUP/production_data ./
fi

# Start services
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback completed"
