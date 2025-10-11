#\!/bin/bash

# NETZ AI Assistant - Stop All Services

echo "🛑 Stopping NETZ AI Assistant services..."
echo "======================================="

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Kill processes
echo -e "${YELLOW}Stopping Frontend...${NC}"
pkill -f "next dev" || true

echo -e "${YELLOW}Stopping Backend...${NC}"
pkill -f "uvicorn main:app" || true
pkill -f "python main.py" || true

echo -e "${YELLOW}Stopping Ollama...${NC}"
pkill -f "ollama serve" || true

echo -e "${YELLOW}Stopping Qdrant...${NC}"
docker stop qdrant > /dev/null 2>&1
docker rm qdrant > /dev/null 2>&1

echo -e "${YELLOW}Stopping PostgreSQL...${NC}"
brew services stop postgresql@15

echo -e "${YELLOW}Stopping Redis...${NC}"
brew services stop redis

echo -e "\n${RED}All services stopped.${NC}"
