#!/bin/bash
# NETZ AI Quick Deployment (Development/Testing)

echo "🚀 Quick NETZ AI Deployment..."

# Build and start
docker-compose up -d --build

# Wait and verify
sleep 15
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ NETZ AI is running!"
    echo "   API: http://localhost:8001"
    echo "   Docs: http://localhost:8001/docs"
else
    echo "❌ Deployment failed"
    docker-compose logs
fi
