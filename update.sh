#!/bin/bash
# NETZ AI Update Script

echo "🔄 Updating NETZ AI..."

# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Verify
sleep 20
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Update successful!"
else
    echo "❌ Update failed"
    exit 1
fi
