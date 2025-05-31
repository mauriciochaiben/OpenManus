#!/bin/bash

# OpenManus Development Startup Script
echo "🚀 Starting OpenManus Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Virtual environment not found. Please run 'python -m venv .venv' first.${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install/update Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt

# Check if node_modules exists in frontend
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Function to start backend
start_backend() {
    echo -e "${GREEN}Starting FastAPI backend on port 8000...${NC}"
    cd "$(dirname "$0")"
    python -m uvicorn app.api.main:app --reload --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend.pid
    echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
}

# Function to start frontend
start_frontend() {
    echo -e "${GREEN}Starting React frontend...${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../.frontend.pid
    echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"

    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
            kill $BACKEND_PID
        fi
        rm -f .backend.pid
    fi

    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
            kill $FRONTEND_PID
        fi
        rm -f .frontend.pid
    fi

    echo -e "${GREEN}Services stopped. Goodbye!${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
sleep 2
start_frontend

echo -e "\n${GREEN}🎉 OpenManus is starting up!${NC}"
echo -e "${BLUE}Backend API: http://localhost:8000${NC}"
echo -e "${BLUE}Frontend App: http://localhost:3000 (or next available port)${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for services
wait
