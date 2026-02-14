#!/bin/bash

# PwrSysPro Analysis Suite - Complete Startup Script
# This script starts both backend and frontend servers

echo "ðŸš€ Starting PwrSysPro Analysis Suite..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="/home/claude/pwrsyspro"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}ðŸ“‹ Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}âŒ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}âŒ Node.js is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}âœ… Prerequisites OK${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}ðŸ”§ Setting up Backend (Python/FastAPI)...${NC}"
cd "$PROJECT_ROOT/server"

# Check if database exists, if not, seed it
if [ ! -f "pwrsyspro.db" ]; then
    echo -e "${YELLOW}ðŸ“š Database not found. Initializing and seeding...${NC}"
    python3 seed_database.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}âŒ Database seeding failed${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}âœ… Database already exists${NC}"
fi

# Start backend in background
echo -e "${BLUE}ðŸš€ Starting FastAPI server on http://localhost:8000...${NC}"
python3 main.py > /tmp/pwrsyspro_backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/pwrsyspro_backend.pid

# Wait for backend to start
echo -e "${YELLOW}â³ Waiting for backend to start...${NC}"
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}âœ… Backend started (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}âŒ Backend failed to start. Check logs: /tmp/pwrsyspro_backend.log${NC}"
    exit 1
fi

echo ""

# Setup Frontend
echo -e "${BLUE}ðŸ”§ Setting up Frontend (React/Vite)...${NC}"
cd "$PROJECT_ROOT/client"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}ðŸ“¦ Installing npm dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}âŒ npm install failed${NC}"
        kill $BACKEND_PID
        exit 1
    fi
else
    echo -e "${GREEN}âœ… Dependencies already installed${NC}"
fi

# Start frontend in background
echo -e "${BLUE}ðŸš€ Starting Vite dev server on http://localhost:5173...${NC}"
npm run dev > /tmp/pwrsyspro_frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/pwrsyspro_frontend.pid

# Wait for frontend to start
echo -e "${YELLOW}â³ Waiting for frontend to start...${NC}"
sleep 5

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}âœ… Frontend started (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}âŒ Frontend failed to start. Check logs: /tmp/pwrsyspro_frontend.log${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo -e "${GREEN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
echo -e "${GREEN}âœ¨ PwrSysPro Analysis Suite is now running!${NC}"
echo -e "${GREEN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
echo ""
echo -e "${BLUE}ðŸŒ Application URL:${NC}      http://localhost:5173"
echo -e "${BLUE}ðŸ“Š API Documentation:${NC}     http://localhost:8000/docs"
echo -e "${BLUE}ðŸ”Œ Backend API:${NC}           http://localhost:8000/api"
echo ""
echo -e "${YELLOW}ðŸ“ Logs:${NC}"
echo -e "   Backend:  /tmp/pwrsyspro_backend.log"
echo -e "   Frontend: /tmp/pwrsyspro_frontend.log"
echo ""
echo -e "${YELLOW}ðŸ›‘ To stop the servers:${NC}"
echo -e "   kill $BACKEND_PID $FRONTEND_PID"
echo -e "   Or run: ./stop_servers.sh"
echo ""
echo -e "${GREEN}â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to view logs (servers will continue running)${NC}"
echo ""

# Follow logs
tail -f /tmp/pwrsyspro_backend.log /tmp/pwrsyspro_frontend.log
