# ⚡ PwrSysPro Analysis Suite

**Professional Power System Analysis & Design Software**

Version 5.0.0 | February 2026

---

## 📋 Overview

PwrSysPro is a comprehensive electrical power system analysis tool that implements international standards for electrical design, safety analysis, and professional reporting. Built for electrical engineers, consultants, and facilities managers.

### Key Features

✅ **Interactive Single-Line Diagram Editor**  
✅ **IEC 60909 Short Circuit Analysis**  
✅ **IEEE 1584 Arc Flash Calculations**  
✅ **Newton-Raphson Load Flow**  
✅ **Protection Coordination**  
✅ **Professional PDF & Excel Reports**  
✅ **R-X Impedance Diagrams**  
✅ **Automated Narrative Generation**  

---

## 🎯 Standards Implemented

| Standard | Purpose |
|----------|---------|
| **IEC 60364-5-52** | Cable selection and voltage drop |
| **IEC 60909-0** | Short-circuit current calculation |
| **IEEE Std 399** | Power system analysis |
| **IEEE 1584-2018** | Arc flash hazard calculation |
| **NFPA 70E** | Electrical safety in the workplace |
| **IEC 60255** | Protective relay characteristics |
| **IEEE C37.113** | Protection and coordination |
| **IEEE 1547** | Interconnection standards |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11** or higher
- **Node.js 18.0** or higher
- **npm** or **yarn**

### Installation

```bash
# 1. Clone or extract the project
cd pwrsyspro

# 2. Run automated setup
chmod +x setup.sh
./setup.sh

# This will:
# - Create Python virtual environment
# - Install Python dependencies
# - Install Node.js dependencies
# - Initialize database
# - Seed component library
```

### Running the Application

```bash
# Start both backend and frontend
./start.sh

# Access the application:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### Stopping the Application

```bash
./stop.sh
```

---

## 📖 User Guide

### Creating Your First Project

1. **Launch Application**
   ```bash
   ./start.sh
   ```

2. **Create New Project**
   - Click "New Project" button
   - Enter project name and settings
   - Base MVA: 100 (default)
   - Frequency: 50 Hz or 60 Hz

3. **Add Components**
   - Drag components from left panel
   - Place on canvas
   - Connect components with cables

4. **Configure Properties**
   - Click any component
   - Edit properties in right panel
   - Set ratings, voltages, etc.

5. **Run Analysis**
   - Click "Analysis" menu
   - Choose analysis type:
     - Short Circuit
     - Load Flow
     - Arc Flash
     - Complete Analysis

6. **Generate Reports**
   - Click "Generate Report" button
   - Professional PDF created
   - Export to Excel available

---

## 🔧 Features in Detail

### 1. Interactive Canvas

- **ReactFlow-based** visual editor
- **Drag-and-drop** component placement
- **Auto-tagging** system
- **Snap-to-grid** (15×15 pixels)
- **Zoom and pan**
- **Component library** with 15+ types

### 2. Network Analysis

#### Short Circuit Analysis (IEC 60909)
- Three-phase fault currents
- Peak current (ip)
- Breaking current (Ib)
- Fault MVA
- Motor contributions
- Breaker validation

#### Load Flow Analysis (Newton-Raphson)
- Bus voltages
- Branch power flows
- System losses
- Convergence in 3-7 iterations
- Voltage regulation check

#### Arc Flash Analysis (IEEE 1584)
- Incident energy (cal/cm²)
- Arc flash boundary
- PPE category (NFPA 70E)
- Working distance
- Equipment configuration

### 3. Advanced Features (Phase 5)

#### R-X Impedance Diagrams
- Component impedance visualization
- Protection coordination aid
- Constant impedance circles
- Constant angle lines
- PNG/SVG export

#### Bus Tie Synchronization
- IEEE 1547 synchronization check
- Voltage: ±5%
- Frequency: ±0.3 Hz
- Phase: ±20°
- Load transfer planning
- 3 transfer modes

#### Loop Flow Analysis
- Mesh analysis
- Circulating currents
- Power distribution
- Loss calculation
- Optimization suggestions

#### Visual Red-Flag Validation
- Real-time validation
- Color-coded severity:
  - 🔴 Critical
  - ⚠️ Warning
  - ℹ️ Info
- Canvas position markers
- Auto-fix suggestions

#### Automated Narratives
- Executive summaries
- Result interpretation
- Technical explanations
- Compliance statements

#### Excel Exports
- Equipment lists
- Cable schedules
- Calculation worksheets
- Multi-sheet workbooks

### 4. Professional Reports

#### PDF Reports Include:
- Cover page
- Executive summary
- Design basis
- Short circuit results
- Arc flash analysis
- Load flow results
- Equipment schedules
- Engineer signature block

#### Excel Reports Include:
- Summary sheet
- Breakers sheet
- Transformers sheet
- Motors sheet
- Cable schedule
- Calculation worksheets

---

## 🗂️ File Format

### .psp Format

PwrSysPro uses `.psp` (PwrSysPro Project) format:
- JSON-based structure
- Gzip compressed
- Complete project data
- 100% data retention
- Version controlled

**Example Usage:**
```javascript
// Export project
POST /api/projects/{id}/export

// Import project
POST /api/projects/import
```

---

## 🔌 API Documentation

### API Endpoints (40 total)

Full API documentation available at: `http://localhost:8000/docs`

#### Quick Reference:

**Projects**
```http
GET    /api/projects                 # List all projects
POST   /api/projects                 # Create project
GET    /api/projects/{id}            # Get project
PUT    /api/projects/{id}            # Update project
DELETE /api/projects/{id}            # Delete project
```

**Analysis**
```http
POST   /api/projects/{id}/analyze/short-circuit
POST   /api/projects/{id}/analyze/load-flow
POST   /api/projects/{id}/analyze/arc-flash
POST   /api/projects/{id}/analyze/complete
POST   /api/projects/{id}/analyze-loops
```

**Reports**
```http
POST   /api/projects/{id}/generate-report
GET    /api/projects/{id}/export/excel/equipment
GET    /api/projects/{id}/export/excel/calculations/{type}
```

**Advanced Features**
```http
POST   /api/projects/{id}/rx-diagram
POST   /api/projects/{id}/bus-tie/check-sync
POST   /api/projects/{id}/validate
POST   /api/projects/{id}/generate-narrative
```

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (API framework)
- SQLAlchemy (Database ORM)
- NumPy & Pandas (Calculations)
- ReportLab (PDF generation)
- Matplotlib (Diagrams)
- OpenPyXL (Excel export)

**Frontend:**
- React 18
- Vite (Build tool)
- ReactFlow (Canvas)
- Tailwind CSS (Styling)
- Axios (HTTP client)

**Database:**
- SQLite (Development)
- PostgreSQL (Production ready)

### Project Structure

```
pwrsyspro/
├── server/              # Python backend
│   ├── main.py         # FastAPI application
│   ├── database.py     # Database models
│   ├── requirements.txt
│   └── utils/          # 22 calculation modules
│
├── client/             # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   ├── package.json
│   └── vite.config.js
│
├── setup.sh           # Automated setup
├── start.sh           # Start application
├── stop.sh            # Stop application
└── README.md          # This file
```

---

## 🧪 Testing

### Running Tests

```bash
# Verify integration
./verify_integration.sh

# Test Python modules
cd server
python3 -m pytest

# Test individual modules
python3 utils/short_circuit.py
python3 utils/arc_flash.py
python3 utils/rx_diagram.py
```

### Manual Testing Checklist

- [ ] Create new project
- [ ] Add components
- [ ] Connect components
- [ ] Run short circuit analysis
- [ ] Run load flow analysis
- [ ] Run arc flash analysis
- [ ] Generate PDF report
- [ ] Export to Excel
- [ ] Import/export .psp file
- [ ] Generate R-X diagram
- [ ] Validate project

---

## 📊 Component Library

### Included Components (15+ Types)

**Power Sources:**
- Utility connection
- Generator

**Transformers:**
- Power transformer
- Distribution transformer

**Switchgear:**
- Circuit breaker
- Disconnect switch
- Fuse

**Protection:**
- Protective relay
- Current transformer
- Voltage transformer

**Loads:**
- Motor
- Panel
- Lighting
- General load

**Cables:**
- Power cable
- Control cable

### Manufacturers (13 Seeded)

- Schneider Electric
- ABB
- Siemens
- Eaton
- General Electric
- Mitsubishi Electric
- Nexans
- Prysmian
- And more...

---

## 🔐 Data Storage

### Database Tables

1. **projects** - Project metadata
2. **project_nodes** - Canvas components
3. **project_connections** - Cable connections
4. **component_library** - Standard components
5. **manufacturers** - Component manufacturers

### Data Location

```
Development:
  ~/.pwrsyspro/pwrsyspro.db

Production:
  Configure via DATABASE_URL environment variable
```

---

## 🚀 Production Deployment

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/pwrsyspro

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
VITE_API_URL=http://your-domain.com:8000

# Report Output
REPORT_OUTPUT_DIR=/var/www/reports

# Base Calculation Parameters
DEFAULT_BASE_MVA=100
DEFAULT_FREQUENCY_HZ=50
```

### Production Build

```bash
# Build frontend
cd client
npm run build

# The dist/ folder contains production-ready files
```

### Deploy with Docker

```bash
# Build image
docker build -t pwrsyspro:5.0.0 .

# Run container
docker run -d -p 8000:8000 -p 5173:5173 pwrsyspro:5.0.0
```

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
cd server
pip install -r requirements.txt --break-system-packages
```

**Frontend won't start:**
```bash
# Check Node version
node --version  # Should be 18+

# Reinstall dependencies
cd client
rm -rf node_modules
npm install
```

**Database errors:**
```bash
# Reinitialize database
rm pwrsyspro.db
python3 server/database.py
python3 server/seed_database.py
```

**Port already in use:**
```bash
# Kill existing processes
./stop.sh

# Or manually
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

---

## 📝 License

Copyright © 2026 PwrSysPro

**Important**: This software implements international electrical standards. The use of this software does not replace the need for licensed professional engineer review and approval. Always consult with a licensed professional engineer for final design approval.

---

## 🤝 Support

### Documentation
- API Docs: http://localhost:8000/docs
- Architecture: See ARCHITECTURE.md
- Development: See PwrSysPro_Development_Specification.md

### Reporting Issues
- Check existing issues first
- Provide error logs
- Include steps to reproduce

---

## 🎯 Roadmap

### Completed (v5.0.0)
- ✅ All Phase 1-5 features
- ✅ 8 international standards
- ✅ 40 API endpoints
- ✅ Professional reporting

### Planned (v5.1.0+)
- 🔄 Electron desktop app
- 🔄 30-day trial system
- 🔄 License management
- 🔄 Auto-updates
- 🔄 Cloud sync
- 🔄 Mobile app

---

## 📊 Statistics

```
Total Code:        15,370 lines
Backend:            9,471 lines (Python)
Frontend:           2,181 lines (React)
Documentation:      3,142 lines
Standards:          8 international
API Endpoints:      40
Database Tables:    5
Component Types:    15+
Manufacturers:      13
```

---

## ✨ Acknowledgments

Built with:
- FastAPI
- React
- ReactFlow
- SQLAlchemy
- ReportLab
- Matplotlib
- NumPy
- Pandas

Standards by:
- IEC (International Electrotechnical Commission)
- IEEE (Institute of Electrical and Electronics Engineers)
- NFPA (National Fire Protection Association)

---

**PwrSysPro Analysis Suite v5.0.0**  
*Professional Power System Analysis Made Simple*

For detailed technical documentation, see `ARCHITECTURE.md`
