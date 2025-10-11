#!/bin/bash

# NETZ AI Assistant - Complete Application Launcher
# This script starts all services and opens the web interface

echo "🚀 NETZ AI Assistant - Starting up..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/Users/mikail/Desktop/NETZ-AI-Project"
cd "$BASE_DIR"

# Function to check if service is running
check_service() {
    local name=$1
    local port=$2
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name is running on port $port${NC}"
        return 0
    else
        echo -e "${RED}✗ $name is not running${NC}"
        return 1
    fi
}

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check PostgreSQL
if brew services list | grep "postgresql@15.*started" > /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    brew services start postgresql@15
fi

# Check Redis
if brew services list | grep "redis.*started" > /dev/null; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${YELLOW}Starting Redis...${NC}"
    brew services start redis
fi

# Check Qdrant
if ! check_service "Qdrant" 6333; then
    echo -e "${YELLOW}Starting Qdrant...${NC}"
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
        -v $(pwd)/qdrant_storage:/qdrant/storage:z \
        qdrant/qdrant > /dev/null 2>&1
    sleep 3
fi

# Check Ollama
if ! check_service "Ollama" 11434; then
    echo -e "${YELLOW}Starting Ollama...${NC}"
    ollama serve > logs/ollama.log 2>&1 &
    sleep 5
    
    # Ensure Mistral model is available
    echo -e "${YELLOW}Checking Mistral model...${NC}"
    ollama pull mistral
fi

# Start Backend
echo -e "\n${YELLOW}Starting Backend API...${NC}"
if ! check_service "Backend API" 8000; then
    cd backend
    source ../venv_mac/bin/activate
    export PYTHONUNBUFFERED=1
    export TOKENIZERS_PARALLELISM=false
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    cd ..
    
    echo "Waiting for backend to start..."
    sleep 10
fi

# Start Frontend
echo -e "\n${YELLOW}Starting Frontend...${NC}"
if ! check_service "Frontend" 3000; then
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    cd ..
    
    echo "Waiting for frontend to start..."
    sleep 8
fi

# Final status check
echo -e "\n${YELLOW}Final Status Check:${NC}"
echo "=================================="

check_service "PostgreSQL" 5432
check_service "Redis" 6379
check_service "Qdrant" 6333
check_service "Ollama" 11434
check_service "Backend API" 8000
check_service "Frontend" 3000

# Check if all services are running
if check_service "Frontend" 3000 && check_service "Backend API" 8000; then
    echo -e "\n${GREEN}✨ All services are running! ✨${NC}"
    echo -e "\n${YELLOW}Opening NETZ AI Assistant...${NC}"
    echo "=================================="
    
    # Wait a moment for services to stabilize
    sleep 2
    
    # Open browser
    open http://localhost:3000
    
    echo -e "\n${GREEN}NETZ AI Assistant is ready!${NC}"
    echo -e "Web Interface: ${YELLOW}http://localhost:3000${NC}"
    echo -e "API Documentation: ${YELLOW}http://localhost:8000/docs${NC}"
    echo -e "\n${YELLOW}To stop all services, run: ./scripts/stop-all.sh${NC}"
else
    echo -e "\n${RED}Some services failed to start. Check logs in the 'logs' directory.${NC}"
    echo "Backend log: tail -f logs/backend.log"
    echo "Frontend log: tail -f logs/frontend.log"
fi