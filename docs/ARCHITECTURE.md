# 🏗️ PwrSysPro Analysis Suite - Technical Architecture

**Version**: 5.0.0  
**Last Updated**: February 13, 2026  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Database Architecture](#database-architecture)
4. [API Endpoints](#api-endpoints)
5. [Module Dependencies](#module-dependencies)
6. [Frontend Architecture](#frontend-architecture)
7. [Calculation Engines](#calculation-engines)
8. [File Format Specification](#file-format-specification)
9. [Integration Points](#integration-points)
10. [Deployment Architecture](#deployment-architecture)

---

## 🎯 System Overview

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                        │
│                  (http://localhost:5173)                │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  FastAPI Backend                         │
│                (http://localhost:8000)                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │          API Layer (main.py)                   │    │
│  │          40 REST Endpoints                     │    │
│  └─────────┬──────────────────────────────────────┘    │
│            │                                             │
│  ┌─────────▼──────────────────────────────────────┐    │
│  │       Business Logic Layer                     │    │
│  │       22 Calculation Modules                   │    │
│  │       - Phase 1: Calculations, Tagging         │    │
│  │       - Phase 2: Topology, Serialization       │    │
│  │       - Phase 3: Per-Unit, Short Circuit, LF   │    │
│  │       - Phase 4: Arc Flash, Reports, Protection│    │
│  │       - Phase 5: 6 Advanced Features           │    │
│  └─────────┬──────────────────────────────────────┘    │
│            │                                             │
│  ┌─────────▼──────────────────────────────────────┐    │
│  │       Data Access Layer                        │    │
│  │       SQLAlchemy ORM                           │    │
│  └─────────┬──────────────────────────────────────┘    │
└────────────┼─────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────┐
│         SQLite / PostgreSQL                      │
│         5 Tables                                 │
└──────────────────────────────────────────────────┘
```

---

## 💻 Technology Stack

### Backend Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Runtime environment |
| **FastAPI** | 0.109.0 | REST API framework |
| **Uvicorn** | 0.27.0 | ASGI server |
| **SQLAlchemy** | 2.0.25 | Database ORM |
| **NumPy** | 1.26.3 | Numerical calculations |
| **Pandas** | 2.2.0 | Data manipulation |
| **ReportLab** | 4.0.9 | PDF generation |
| **Matplotlib** | 3.8.2 | Diagram generation |
| **OpenPyXL** | 3.1.2 | Excel export |
| **Pydantic** | 2.5.3 | Data validation |

### Frontend Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **Vite** | 5.0.8 | Build tool & dev server |
| **ReactFlow** | 11.10.1 | Canvas/flowchart |
| **Tailwind CSS** | 3.4.1 | Styling framework |
| **Axios** | 1.6.5 | HTTP client |

### Database

| Environment | Database | Notes |
|-------------|----------|-------|
| **Development** | SQLite | Single-file database |
| **Production** | PostgreSQL | Recommended for scale |

---

## 🗄️ Database Architecture

### Schema Design

#### Entity-Relationship Diagram

```
┌─────────────┐        ┌──────────────────┐
│  projects   │───────<│  project_nodes   │
└─────────────┘        └──────────────────┘
      │                         │
      │                         │
      │                ┌────────▼──────────────┐
      └───────────────<│ project_connections  │
                       └───────────────────────┘

┌──────────────────┐
│ component_library│
└──────────────────┘
        │
        │
┌───────▼──────┐
│ manufacturers│
└──────────────┘
```

### Table Definitions

#### 1. projects

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    base_mva REAL DEFAULT 100.0,
    system_frequency REAL DEFAULT 50.0,
    standards TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Stores project metadata and global settings  
**Key Fields**:
- `base_mva`: Base MVA for per-unit calculations
- `system_frequency`: 50 Hz or 60 Hz
- `standards`: Applied standards (IEC, IEEE, etc.)

---

#### 2. project_nodes

```sql
CREATE TABLE project_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- 'Source', 'Breaker', 'Transformer', etc.
    custom_tag TEXT,
    position_x REAL,
    position_y REAL,
    component_library_id INTEGER,
    properties JSON,  -- Component-specific properties
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (component_library_id) REFERENCES component_library(id)
);
```

**Purpose**: Canvas components (nodes)  
**Indexed Fields**: `project_id`, `type`, `component_library_id`  
**JSON Properties Example**:
```json
{
  "voltage": 11.0,
  "rated_current": 1000,
  "power_factor": 0.85,
  "efficiency": 95.0
}
```

---

#### 3. project_connections

```sql
CREATE TABLE project_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    source_node_id INTEGER NOT NULL,
    target_node_id INTEGER NOT NULL,
    cable_library_id INTEGER,
    length REAL,  -- meters
    installation_method TEXT,  -- 'E', 'F', 'G', etc. per IEC
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (source_node_id) REFERENCES project_nodes(id),
    FOREIGN KEY (target_node_id) REFERENCES project_nodes(id),
    FOREIGN KEY (cable_library_id) REFERENCES component_library(id)
);
```

**Purpose**: Cable connections between nodes  
**Indexed Fields**: `project_id`, `source_node_id`, `target_node_id`

---

#### 4. component_library

```sql
CREATE TABLE component_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,  -- 'Breaker', 'Cable', 'Transformer', etc.
    manufacturer TEXT,
    model TEXT,
    voltage_rating REAL,
    ampacity_base REAL,
    short_circuit_rating REAL,
    impedance_r REAL,  -- Resistance (Ω/km or pu)
    impedance_x REAL,  -- Reactance (Ω/km or pu)
    impedance_z_percent REAL,  -- For transformers
    cross_section REAL,  -- mm² for cables
    conductor_material TEXT,  -- 'Copper', 'Aluminum'
    insulation_type TEXT,  -- 'XLPE', 'PVC', etc.
    properties JSON,  -- Type-specific properties
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Standard component definitions  
**Records**: ~100+ seeded components

---

#### 5. manufacturers

```sql
CREATE TABLE manufacturers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    country TEXT,
    website TEXT
);
```

**Purpose**: Component manufacturers  
**Records**: 13 seeded manufacturers

---

## 🔌 API Endpoints

### Complete Endpoint Reference (40 Total)

#### Projects (5 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create new project |
| GET | `/api/projects/{id}` | Get project details |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |

**Example Request:**
```bash
POST /api/projects
Content-Type: application/json

{
  "name": "Industrial Facility",
  "description": "Main distribution system",
  "base_mva": 100.0,
  "system_frequency": 50.0
}
```

---

#### Component Library (3 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/component-library` | List components |
| POST | `/api/component-library` | Add component |
| GET | `/api/manufacturers` | List manufacturers |

---

#### Nodes - Canvas Components (4 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/projects/{id}/nodes` | List project nodes |
| POST | `/api/projects/{id}/nodes` | Create node |
| PUT | `/api/projects/{id}/nodes/{node_id}` | Update node |
| DELETE | `/api/projects/{id}/nodes/{node_id}` | Delete node |

**Example Request:**
```bash
POST /api/projects/1/nodes
Content-Type: application/json

{
  "type": "Breaker",
  "position_x": 100,
  "position_y": 200,
  "component_library_id": 5,
  "properties": {
    "voltage": 11.0,
    "rated_current": 1000
  }
}
```

---

#### Connections - Cables (3 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/projects/{id}/connections` | List connections |
| POST | `/api/projects/{id}/connections` | Create connection |
| DELETE | `/api/projects/{id}/connections/{conn_id}` | Delete connection |

---

#### Topology Analysis (2 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/projects/{id}/topology` | Analyze network topology |
| POST | `/api/projects/{id}/update-tags` | Regenerate all tags |

**Topology Response:**
```json
{
  "nodes_count": 15,
  "connections_count": 14,
  "buses": [
    {"bus_id": 1, "nodes": ["SOURCE-01", "CB-01"]},
    {"bus_id": 2, "nodes": ["CB-01", "XFMR-01"]}
  ],
  "loops": [
    ["BUS1", "BUS2", "BUS3", "BUS1"]
  ],
  "levels": {
    "SOURCE-01": 0,
    "CB-01": 1,
    "XFMR-01": 2
  }
}
```

---

#### File Operations (2 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/projects/{id}/export` | Export .psp file |
| POST | `/api/projects/import` | Import .psp file |

---

#### Calculations (4 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/calculate/voltage-drop` | Calculate voltage drop |
| POST | `/api/calculate/cable-sizing` | Size cable |
| POST | `/api/projects/{id}/analyze/short-circuit` | IEC 60909 analysis |
| POST | `/api/projects/{id}/analyze/load-flow` | Newton-Raphson |

**Short Circuit Request:**
```bash
POST /api/projects/1/analyze/short-circuit
Content-Type: application/json

{
  "fault_type": "three_phase",
  "voltage_factor": 1.1
}
```

**Short Circuit Response:**
```json
{
  "results": {
    "bus1": {
      "tag": "MDB-01",
      "i_k3": 25.3,      // kA
      "ip": 65.2,        // Peak current (kA)
      "ib": 25.3,        // Breaking current (kA)
      "sk_mva": 482.5,   // Fault MVA
      "breaker_rating": 31.5,
      "breaker_status": "PASS"
    }
  }
}
```

---

#### Analysis (3 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/projects/{id}/analyze/complete` | Run all analyses |
| POST | `/api/projects/{id}/analyze/arc-flash` | IEEE 1584 analysis |
| POST | `/api/projects/{id}/analyze-loops` | Loop flow analysis |

**Arc Flash Response:**
```json
{
  "results": {
    "bus1": {
      "tag": "MDB-01",
      "incident_energy": 12.5,  // cal/cm²
      "arc_flash_boundary": 48.0,  // inches
      "ppe_category": 2,
      "hazard_level": "Medium"
    }
  }
}
```

---

#### Reports (2 endpoints)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/projects/{id}/generate-report` | Generate PDF |
| POST | `/api/protection/coordinate` | TCC coordination |

---

#### Phase 5 Advanced Features (12 endpoints)

**R-X Diagrams (3)**
```
POST   /api/projects/{id}/rx-diagram
GET    /api/projects/{id}/rx-diagram/export/png
GET    /api/projects/{id}/rx-diagram/export/svg
```

**Bus Tie (2)**
```
POST   /api/projects/{id}/bus-tie/check-sync
POST   /api/projects/{id}/bus-tie/plan-transfer
```

**Validation (1)**
```
POST   /api/projects/{id}/validate
```

**Narratives (1)**
```
POST   /api/projects/{id}/generate-narrative
```

**Excel Export (2)**
```
GET    /api/projects/{id}/export/excel/equipment
GET    /api/projects/{id}/export/excel/calculations/{type}
```

**Health Check (1)**
```
GET    /health
```

---

## 📦 Module Dependencies

### Dependency Graph

```
┌─────────────────────────────────────────────────┐
│              Phase 1: Foundation                 │
├─────────────────────────────────────────────────┤
│  database.py  (no dependencies)                 │
│  calculations.py  (numpy)                       │
│  tagging.py  (database.py)                      │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│           Phase 2: Topology & Files             │
├─────────────────────────────────────────────────┤
│  topology.py  → database.py                     │
│  serialization.py  → database.py                │
│  tagging_enhanced.py  → topology.py, tagging.py │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Phase 3: Calculation Core               │
├─────────────────────────────────────────────────┤
│  per_unit.py  (standalone, numpy)               │
│  short_circuit.py  → per_unit.py, database.py   │
│  load_flow.py  → per_unit.py, database.py       │
│  integrated_calc.py  → short_circuit, load_flow │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│         Phase 4: Bonus Features                 │
├─────────────────────────────────────────────────┤
│  arc_flash.py  → short_circuit.py               │
│  report_generator.py  → all analysis modules    │
│  protection.py  (standalone)                    │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│      Phase 5: Advanced Features                │
├─────────────────────────────────────────────────┤
│  rx_diagram.py  → per_unit.py, matplotlib       │
│  bus_tie.py  → load_flow.py (conceptual)        │
│  loop_analysis.py  → topology.py                │
│  validation.py  → short_circuit, load_flow      │
│  narrative_generator.py  → all analysis modules │
│  excel_export.py  → database.py, openpyxl       │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Architecture

### Component Hierarchy

```
App.jsx
├── Canvas.jsx
│   ├── ElectricalNode.jsx (custom nodes)
│   └── ConnectionEdge (ReactFlow)
│
├── ComponentLibrary.jsx (left panel)
│   └── ComponentCard
│
├── PropertyInspector.jsx (right panel)
│   └── PropertyField
│
├── TopologyViewer.jsx (modal)
│   └── TopologyStats
│
├── NetworkAnalysis.jsx
│   ├── ShortCircuitPanel
│   ├── LoadFlowPanel
│   └── ArcFlashPanel
│
├── ReportGenerator.jsx
│   └── ReportOptions
│
├── FileOperations.jsx
│   ├── ImportDialog
│   └── ExportDialog
│
└── RXDiagram.jsx
    └── DiagramViewer
```

### State Management

**Global State** (React Context):
- Current project
- Canvas nodes
- Canvas edges
- Selected node
- Analysis results

**Local State** (Component):
- UI interactions
- Form inputs
- Modal visibility

### API Service Layer

```javascript
// api.js - Centralized API calls
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const projectsAPI = {
  list: () => axios.get(`${API_URL}/projects`),
  create: (data) => axios.post(`${API_URL}/projects`, data),
  get: (id) => axios.get(`${API_URL}/projects/${id}`),
  update: (id, data) => axios.put(`${API_URL}/projects/${id}`, data),
  delete: (id) => axios.delete(`${API_URL}/projects/${id}`)
};

export const analysisAPI = {
  shortCircuit: (id) => axios.post(`${API_URL}/projects/${id}/analyze/short-circuit`),
  loadFlow: (id) => axios.post(`${API_URL}/projects/${id}/analyze/load-flow`),
  arcFlash: (id) => axios.post(`${API_URL}/projects/${id}/analyze/arc-flash`)
};
```

---

## ⚙️ Calculation Engines

### Per-Unit System

**Module**: `per_unit.py`  
**Standard**: IEEE Std 399

```python
class PerUnitSystem:
    def __init__(self, base_mva):
        self.base_mva = base_mva
        self.voltage_levels = {}
    
    def add_voltage_level(self, voltage_kv):
        # Calculate base values
        # Z_base = V² / S_base
        # I_base = S_base / (√3 × V_base)
```

**Purpose**: Normalize multi-voltage systems

---

### Short Circuit Calculator

**Module**: `short_circuit.py`  
**Standard**: IEC 60909-0

```python
class IEC60909Calculator:
    def calculate_three_phase_fault(self, bus_data):
        # I"k3 = (c × Un) / (√3 × |Zk|)
        # ip = κ × √2 × I"k3  (peak current)
        # Ib = μ × I"k3  (breaking current)
```

**Features**:
- Three-phase fault currents
- Motor contributions
- Voltage factor (c)
- Peak factor (κ)

---

### Load Flow Solver

**Module**: `load_flow.py`  
**Method**: Newton-Raphson

```python
class NewtonRaphsonLoadFlow:
    def solve(self, y_bus, pq_buses, pv_buses, slack_bus):
        # Iterative solution
        # P = Σ|V||Y|cos(θ-φ)
        # Q = Σ|V||Y|sin(θ-φ)
        # Jacobian matrix
```

**Features**:
- PQ, PV, Slack bus types
- 3-7 iteration convergence
- Branch power flows
- System losses

---

### Arc Flash Calculator

**Module**: `arc_flash.py`  
**Standard**: IEEE 1584-2018

```python
class IEEE1584ArcFlashCalculator:
    def calculate(self, bus_data):
        # Arcing current
        # log(Iarc) = k + 0.662×log(Ibf) + 0.0966×V
        
        # Incident energy
        # E = En × (610/D)^x
        
        # Arc flash boundary
        # AFB = 610 × (En / 1.2)^(1/x)
```

---

## 📄 File Format Specification

### .psp Format (PwrSysPro Project)

**Structure**: JSON + gzip compression

```json
{
  "version": "5.0",
  "format": "psp",
  "project": {
    "id": 1,
    "name": "Industrial Facility",
    "base_mva": 100.0,
    "system_frequency": 50.0,
    "created_at": "2026-02-13T10:30:00Z"
  },
  "nodes": [
    {
      "id": 1,
      "type": "Source",
      "custom_tag": "SOURCE-01",
      "position": {"x": 100, "y": 100},
      "component_library_id": 1,
      "properties": {
        "voltage": 11.0,
        "short_circuit_mva": 500.0
      }
    }
  ],
  "connections": [
    {
      "id": 1,
      "source_node_id": 1,
      "target_node_id": 2,
      "cable_library_id": 10,
      "length": 50.0
    }
  ],
  "settings": {
    "grid_size": 15,
    "show_labels": true
  }
}
```

**Compression**: gzip level 9  
**Extension**: .psp  
**MIME**: application/x-pwrsyspro

---

## 🔗 Integration Points

### Frontend ↔ Backend

```
Component Action          →  API Call              →  Backend Handler
─────────────────────────────────────────────────────────────────────
Create Node              →  POST /nodes           →  create_node()
Run Short Circuit        →  POST /analyze/sc      →  analyze_short_circuit()
Generate Report          →  POST /generate-report →  generate_report()
Export Excel             →  GET /export/excel     →  export_equipment_list()
```

### Module Integration

```
User Action: "Run Complete Analysis"
  ↓
IntegratedCalculationService.analyze_network()
  ↓
├── TopologyGraph.build() [Phase 2]
├── PerUnitSystem.convert() [Phase 3]
├── IEC60909Calculator.calculate() [Phase 3]
├── NewtonRaphsonLoadFlow.solve() [Phase 3]
├── IEEE1584ArcFlashCalculator.calculate() [Phase 4]
└── ValidationEngine.validate() [Phase 5]
  ↓
Return unified results
```

---

## 🚀 Deployment Architecture

### Development

```
Developer Machine
├── Python 3.11 venv
├── Node.js 18+
├── SQLite database
└── Local ports: 8000, 5173
```

### Production (Future)

```
┌─────────────────────────────────────┐
│         Load Balancer               │
│         (nginx/caddy)               │
└──────────┬──────────────────────────┘
           │
     ┌─────┴─────┐
     │           │
┌────▼────┐ ┌───▼─────┐
│ FastAPI │ │ FastAPI │
│ Worker  │ │ Worker  │
└────┬────┘ └───┬─────┘
     │          │
     └────┬─────┘
          │
     ┌────▼──────────┐
     │  PostgreSQL   │
     │  Database     │
     └───────────────┘
```

---

## 📊 Performance Metrics

### Response Times (Target)

| Operation | Target | Notes |
|-----------|--------|-------|
| Create Project | <100ms | Database insert |
| Add Node | <50ms | Simple insert |
| Short Circuit | <2s | Complex calculation |
| Load Flow | <3s | Iterative solver |
| Generate PDF | <5s | Report generation |
| Export Excel | <3s | Multi-sheet workbook |

### Scalability

| Metric | Limit | Notes |
|--------|-------|-------|
| Nodes per Project | 1,000 | Practical limit |
| Projects per DB | 10,000+ | SQLite limit ~1TB |
| Concurrent Users | 100+ | With PostgreSQL |
| API Requests | 1,000/min | Default rate limit |

---

## 🔐 Security Considerations

### API Security
- CORS configured
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy)
- File upload validation

### Data Security
- Database encryption (at rest)
- HTTPS in production
- No hardcoded secrets
- Environment variables

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 5.0.0 | Feb 2026 | Complete implementation (Phases 1-5) |
| 4.0.0 | Feb 2026 | Bonus features (Arc Flash, Reports) |
| 3.0.0 | Feb 2026 | Calculation core complete |
| 2.0.0 | Feb 2026 | Topology & files |
| 1.0.0 | Feb 2026 | Foundation |

---

**Last Updated**: February 13, 2026  
**For User Guide**: See README.md  
**For Development**: See PwrSysPro_Development_Specification.md
