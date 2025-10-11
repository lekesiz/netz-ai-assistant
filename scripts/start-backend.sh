#!/bin/bash

# NETZ AI Backend Startup Script

cd /Users/mikail/Desktop/NETZ-AI-Project/backend

# Activate virtual environment
source ../venv_mac/bin/activate

# Export environment variables
export PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false

# Kill any existing backend processes
pkill -f "uvicorn main:app" || true

# Start the backend
echo "Starting NETZ AI Backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload