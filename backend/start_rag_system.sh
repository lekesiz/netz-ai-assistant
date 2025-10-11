#!/bin/bash

# NETZ AI - RAG System Startup Script
# This script starts all necessary services for the full RAG system

echo "🚀 Starting NETZ AI RAG System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found, trying docker compose..."
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "📦 Starting Qdrant and Redis with Docker..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 5

# Setup Qdrant
echo "🔧 Setting up Qdrant vector database..."
python setup_qdrant.py

if [ $? -ne 0 ]; then
    echo "❌ Qdrant setup failed. Please check the logs."
    exit 1
fi

# Stop simple_api if running
echo "🛑 Stopping simple_api.py if running..."
pkill -f "python simple_api.py" 2>/dev/null

# Load existing data
echo "📊 Loading data into RAG system..."
echo "This may take a few minutes..."

# Check if data ingestion scripts exist and run them
if [ -f "load_real_data.py" ]; then
    echo "Loading real data..."
    python load_real_data.py
fi

if [ -f "pennylane_ingestion.py" ]; then
    echo "Loading PennyLane data..."
    python pennylane_ingestion.py
fi

# Start the main API with RAG
echo "🌟 Starting main API with full RAG support..."
echo "The API will be available at http://localhost:8000"
echo ""
echo "📝 API Endpoints:"
echo "  - Health: http://localhost:8000/health"
echo "  - Chat: POST http://localhost:8000/api/chat"
echo "  - RAG Query: POST http://localhost:8000/api/rag/query"
echo "  - Streaming: GET http://localhost:8000/api/chat/stream"
echo "  - Models: GET http://localhost:8000/api/models"
echo ""

# Start main.py in the foreground
python main.py