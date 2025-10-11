#!/bin/bash

# NETZ AI Assistant - Complete Startup Script

echo "🚀 Starting NETZ AI Assistant..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_DIR"

# Check if all services are installed
check_service() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        exit 1
    fi
}

echo "Checking required services..."
check_service docker
check_service redis-cli
check_service psql
check_service ollama
check_service node
check_service python3

# Function to wait for a service
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=0
    
    echo -n "Waiting for $service on port $port..."
    while ! nc -z localhost $port &> /dev/null; do
        if [ $attempt -eq $max_attempts ]; then
            echo -e " ${RED}Failed!${NC}"
            return 1
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    echo -e " ${GREEN}Ready!${NC}"
    return 0
}

# Start services
echo -e "\n${YELLOW}Starting backend services...${NC}"

# 1. Start PostgreSQL
echo "Starting PostgreSQL..."
brew services start postgresql@15 &> /dev/null

# 2. Start Redis
echo "Starting Redis..."
brew services start redis &> /dev/null

# 3. Start Qdrant
echo "Starting Qdrant vector database..."
docker run -d --name qdrant \
    -p 6333:6333 -p 6334:6334 \
    -v "$PROJECT_DIR/qdrant_storage:/qdrant/storage:z" \
    qdrant/qdrant &> /dev/null || docker start qdrant &> /dev/null

# 4. Check Ollama
echo "Checking Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &> /dev/null &
fi

# Wait for services
wait_for_service "PostgreSQL" 5432
wait_for_service "Redis" 6379
wait_for_service "Qdrant" 6333
wait_for_service "Ollama" 11434

# 5. Start FastAPI backend
echo -e "\n${YELLOW}Starting FastAPI backend...${NC}"
cd "$PROJECT_DIR/backend"
source ../venv_mac/bin/activate
python main.py &> ../logs/backend.log &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend
wait_for_service "Backend API" 8000

# 6. Start Next.js frontend
echo -e "\n${YELLOW}Starting Next.js frontend...${NC}"
cd "$PROJECT_DIR/frontend"
npm run dev &> ../logs/frontend.log &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend
wait_for_service "Frontend" 3000

# Summary
echo -e "\n${GREEN}✅ All services started successfully!${NC}"
echo -e "\nAccess points:"
echo -e "  ${GREEN}►${NC} Frontend: http://localhost:3000"
echo -e "  ${GREEN}►${NC} Backend API: http://localhost:8000"
echo -e "  ${GREEN}►${NC} API Docs: http://localhost:8000/docs"
echo -e "  ${GREEN}►${NC} Qdrant Dashboard: http://localhost:6333/dashboard"

# Create PID file for shutdown
echo "$BACKEND_PID $FRONTEND_PID" > "$PROJECT_DIR/logs/app.pid"

echo -e "\nTo stop all services, run: ${YELLOW}./scripts/stop-all.sh${NC}"
echo -e "\nLogs are available in: ${YELLOW}$PROJECT_DIR/logs/${NC}"

# Keep script running
echo -e "\nPress ${YELLOW}Ctrl+C${NC} to stop all services..."
trap 'echo -e "\nStopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait