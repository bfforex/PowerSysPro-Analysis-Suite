#!/bin/bash
# PwrSysPro Analysis Suite - Complete Setup & Initialization Script
# This script sets up the entire application from scratch

set -e

echo "⚡ PwrSysPro Analysis Suite - Complete Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() {
    echo -e "${BLUE}▶${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Python 3 is installed
step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.11 or higher."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
success "Python $PYTHON_VERSION found"

# Check if Node.js is installed
step "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 18 or higher."
    exit 1
fi
NODE_VERSION=$(node --version)
success "Node.js $NODE_VERSION found"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Phase 1: Backend Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd server

# Create virtual environment (optional but recommended)
step "Creating Python virtual environment (optional)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Virtual environment created"
else
    warn "Virtual environment already exists"
fi

# Install Python dependencies
step "Installing Python dependencies..."
if [ -f "venv/bin/pip" ]; then
    ./venv/bin/pip install -q --upgrade pip
    ./venv/bin/pip install -q -r requirements.txt
    PYTHON_CMD="./venv/bin/python3"
else
    pip3 install -q --upgrade pip --break-system-packages 2>/dev/null || pip3 install -q --upgrade pip
    pip3 install -q -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -q -r requirements.txt
    PYTHON_CMD="python3"
fi
success "Python dependencies installed"

# Initialize database
step "Initializing database..."
$PYTHON_CMD -c "
from models.database import Base, engine
Base.metadata.create_all(bind=engine)
print('✓ Database tables created')
"
success "Database initialized"

# Seed database
step "Seeding database with component library..."
$PYTHON_CMD seed_database.py > /dev/null 2>&1
success "Database seeded with 13 components"

cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 Phase 2: Frontend Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd client

# Install Node dependencies
step "Installing Node.js dependencies..."
npm install --silent 2>/dev/null || npm install
success "Node dependencies installed"

cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 Phase 3: Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Make scripts executable
step "Making scripts executable..."
chmod +x start.sh stop.sh verify_integration.sh
success "Scripts are executable"

# Create data directory
step "Creating data directory..."
mkdir -p data
success "Data directory created"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 To start the application:"
echo "   ./start.sh"
echo ""
echo "📊 To verify integration:"
echo "   ./verify_integration.sh"
echo ""
echo "📚 Access points:"
echo "   • Frontend:  http://localhost:5173"
echo "   • API:       http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo ""
echo "🎉 PwrSysPro is ready to use!"
echo ""
