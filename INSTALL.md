# 📦 PwrSysPro Complete Package - Installation Guide

**Version**: 5.0.0  
**Package Date**: February 14, 2026  
**Status**: Production Ready

---

## 📋 What's Included

This complete package contains:

✅ **Backend** (Python FastAPI)
  - 22 calculation modules organized by phase
  - 40 API endpoints
  - 8 international standards implemented
  - SQLite database setup

✅ **Frontend** (React + Vite)
  - 10 interactive components
  - Professional UI with Tailwind CSS
  - ReactFlow canvas for SLD editing

✅ **Documentation**
  - User guide (README.md)
  - Technical architecture (docs/ARCHITECTURE.md)
  - Development specification
  - Implementation summary

✅ **Scripts**
  - Automated setup
  - Start/stop scripts
  - Integration tests

---

## 🚀 Quick Start

### Prerequisites

Ensure you have installed:
- **Python 3.11** or higher
- **Node.js 18.0** or higher
- **npm** (comes with Node.js)

Check versions:
```bash
python3 --version  # Should show 3.11 or higher
node --version     # Should show v18 or higher
npm --version      # Should show 8 or higher
```

### Installation (3 Simple Steps)

#### Step 1: Extract Package
```bash
# Extract the package
unzip pwrsyspro_complete_package.zip
# or
tar -xzf pwrsyspro_complete_package.tar.gz

# Navigate into the directory
cd pwrsyspro_complete_package
```

#### Step 2: Run Setup
```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run automated setup
./scripts/setup.sh
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies  
- ✅ Initialize the database
- ✅ Seed the component library
- ✅ Make all scripts executable

#### Step 3: Start Application
```bash
# Start both backend and frontend
./scripts/start.sh
```

**Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📁 Package Structure

```
pwrsyspro_complete_package/
│
├── 📁 server/                      # Python Backend
│   ├── main.py                    # FastAPI application
│   ├── database.py                # Database models
│   ├── seed_database.py           # Component library data
│   ├── requirements.txt           # Python dependencies
│   │
│   └── 📁 utils/                   # Calculation Modules
│       ├── phase1/                # Foundation (calculations, tagging)
│       ├── phase2/                # Topology (graph, files)
│       ├── phase3/                # Calculations (per-unit, SC, LF)
│       ├── phase4/                # Bonus (arc flash, reports)
│       └── phase5/                # Advanced (R-X, bus tie, etc.)
│
├── 📁 client/                      # React Frontend
│   ├── src/
│   │   ├── components/            # 10 React components
│   │   ├── services/              # API service layer
│   │   ├── main.jsx               # React entry point
│   │   └── index.css              # Tailwind styles
│   │
│   ├── public/
│   │   └── index.html             # HTML template
│   │
│   ├── package.json               # Node.js dependencies
│   ├── vite.config.js             # Vite configuration
│   └── tailwind.config.js         # Tailwind config
│
├── 📁 scripts/                     # Automation Scripts
│   ├── setup.sh                   # Initial setup
│   ├── start.sh                   # Start application
│   ├── stop.sh                    # Stop application
│   └── verify_integration.sh      # Integration tests
│
├── 📁 docs/                        # Documentation
│   ├── ARCHITECTURE.md            # Technical architecture
│   ├── PwrSysPro_Development_Specification.md
│   └── PHASE5_IMPLEMENTATION_SUMMARY.md
│
├── 📁 data/                        # Database (auto-created)
│   └── pwrsyspro.db               # SQLite database
│
├── 📁 reports/                     # Generated Reports
│   ├── *.pdf                      # PDF reports
│   └── *.xlsx                     # Excel exports
│
├── 📄 README.md                    # Main user guide
├── 📄 INSTALL.md                   # This file
├── 📄 LICENSE                      # MIT License
├── 📄 .gitignore                   # Git ignore rules
└── 📄 .env.example                 # Environment variables example
```

---

## 🔧 Manual Installation (If Setup Script Fails)

### Backend Setup

```bash
# 1. Navigate to server directory
cd server

# 2. Create Python virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install Python dependencies
pip install -r requirements.txt --break-system-packages

# 5. Initialize database
python3 database.py

# 6. Seed component library
python3 seed_database.py

# 7. Test backend
python3 main.py
# Should start on http://localhost:8000
```

### Frontend Setup

```bash
# Open new terminal window

# 1. Navigate to client directory
cd client

# 2. Install Node.js dependencies
npm install

# 3. Start development server
npm run dev
# Should start on http://localhost:5173
```

---

## 🎯 Verifying Installation

### 1. Check Backend

Open browser to: http://localhost:8000/docs

You should see the Swagger API documentation with 40 endpoints.

### 2. Check Frontend

Open browser to: http://localhost:5173

You should see the PwrSysPro application interface.

### 3. Run Integration Tests

```bash
./scripts/verify_integration.sh
```

Expected output:
```
✅ All files present
✅ Python imports working
✅ Database initialized
✅ Component library seeded
✅ Frontend files present
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd server
source venv/bin/activate  # Make sure venv is activated
pip install -r requirements.txt --break-system-packages
```

---

**Error**: `Port 8000 already in use`

**Solution**:
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
cd server
uvicorn main:app --port 8001
```

---

### Frontend Won't Start

**Error**: `Cannot find module 'vite'`

**Solution**:
```bash
cd client
rm -rf node_modules package-lock.json
npm install
```

---

**Error**: `Port 5173 already in use`

**Solution**:
```bash
# Kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or Vite will automatically use next available port
```

---

### Database Errors

**Error**: `Table does not exist`

**Solution**:
```bash
cd server
rm -f data/pwrsyspro.db  # Delete old database
python3 database.py       # Recreate
python3 seed_database.py  # Reseed
```

---

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'utils.phase1'`

**Solution**:
Make sure you're running from the correct directory and __init__.py files exist:
```bash
# Check __init__.py files
find server/utils -name "__init__.py"

# Should show:
# server/utils/__init__.py
# server/utils/phase1/__init__.py
# server/utils/phase2/__init__.py
# etc.
```

---

## 📚 Next Steps

### 1. Read Documentation

- **User Guide**: `README.md` - Learn how to use the application
- **Architecture**: `docs/ARCHITECTURE.md` - Understand the system
- **Development**: `docs/PwrSysPro_Development_Specification.md` - Full technical spec

### 2. Create Your First Project

1. Open http://localhost:5173
2. Click "New Project"
3. Add components from the library
4. Connect components with cables
5. Run analysis
6. Generate reports

### 3. Explore Features

- ✅ Short circuit analysis (IEC 60909)
- ✅ Load flow analysis (Newton-Raphson)
- ✅ Arc flash analysis (IEEE 1584)
- ✅ R-X impedance diagrams
- ✅ Professional PDF reports
- ✅ Excel exports
- ✅ Visual validation

---

## 🔐 Production Deployment

For production deployment:

1. **Use PostgreSQL** instead of SQLite
   ```bash
   # Install PostgreSQL
   # Update .env file
   DATABASE_URL=postgresql://user:pass@localhost/pwrsyspro
   ```

2. **Build Frontend for Production**
   ```bash
   cd client
   npm run build
   # Outputs to client/dist/
   ```

3. **Use Production Server**
   ```bash
   cd server
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

4. **Set Up Reverse Proxy** (nginx/caddy)
5. **Enable HTTPS**
6. **Set Up Monitoring**

See `docs/ARCHITECTURE.md` for detailed deployment instructions.

---

## 🆘 Getting Help

### Documentation
- Main README: `README.md`
- Architecture: `docs/ARCHITECTURE.md`
- API Docs: http://localhost:8000/docs (when running)

### Common Tasks

**Stop the Application**:
```bash
./scripts/stop.sh
```

**Restart the Application**:
```bash
./scripts/stop.sh
./scripts/start.sh
```

**Check Logs**:
```bash
# Backend logs (if running in background)
tail -f server/logs/pwrsyspro.log

# Frontend logs (in terminal where you ran npm run dev)
```

**Update Dependencies**:
```bash
# Python
cd server
pip install -r requirements.txt --upgrade

# Node.js
cd client
npm update
```

---

## ✅ Installation Checklist

Before reporting issues, verify:

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Ran `./scripts/setup.sh` successfully
- [ ] Backend starts without errors (`./scripts/start.sh`)
- [ ] Frontend accessible at http://localhost:5173
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Can create a new project
- [ ] Can add components to canvas

---

## 🎊 Success!

If you can:
1. ✅ Start the application
2. ✅ See the frontend interface
3. ✅ Create a project
4. ✅ Run an analysis

**You're ready to start using PwrSysPro!**

For detailed usage instructions, see the main README.md file.

---

**Installation Guide Version**: 1.0  
**Package Version**: 5.0.0  
**Last Updated**: February 14, 2026
