# PwrSysPro-Analysis-Suite
A power system analysis software

This is the master blueprint for PwrsysPro Analysis Suite. This document is designed to guide the development team, architecture review, and project management from Day 1 through to the final release.
PwrsysPro Analysis Suite: Master Design Document
1. Executive Summary
PwrsysPro Analysis Suite is a next-generation electrical engineering software that bridges the gap between Single Line Diagram (SLD) drafting and complex power system calculations.
Unlike traditional tools that require separate drafting and calculation workflows, PwrsysPro operates on a "Live Digital Twin" model. As the user draws the network, the system automatically builds the mathematical impedance matrix in the background. This allows for instant validation of Short Circuit currents, Voltage Drops, and Load Flow scenarios, concluding with the automated generation of professional, reviewer-ready engineering reports.
2. High-Level System Architecture
The software follows a Decoupled Service-Oriented Architecture (SOA) to ensure that heavy mathematical computations do not freeze the User Interface.
The Four Pillars of PwrsysPro:
 * The Interactive Canvas (Frontend): The user-facing layer for drafting, property editing, and results visualization.
 * The Calculation Engine (Backend Core): The mathematical brain that processes topology and solves network equations.
 * The Data Librarian (Persistence Layer): A relational database managing component libraries, project metadata, and libraries of standards.
 * The Reporter (Output Module): An automated document generator that compiles schedules, diagrams, and narrative analyses.
3. Detailed Component Functions
A. The Interactive Canvas (UI Layer)
 * Drafting Workspace: A vector-based (SVG/Canvas) environment supporting drag-and-drop placement of electrical symbols.
 * Dynamic Tagging Engine:
   * Function: Automatically assigns component tags based on connectivity.
   * Syntax Logic: [Component Type]-[Voltage]-[From Bus]-[To Bus]-[Sequence #] (e.g., C-0.48-MDP1-M1-01).
   * Behavior: Updates automatically if a component is moved to a different bus.
 * Topology Listener:
   * Function: Real-time monitoring of connections. Prevents "dangling" components and identifies "Loops" or "Parallel Paths" instantly.
 * Location Manager:
   * Function: A hierarchical tree view (Site > Building > Room) that assigns physical locations to components for cable length estimates and ambient temperature derating.
B. The Calculation Engine (The Brain)
 * Topology Processor: Converts the visual drawing into a Nodal Admittance Matrix (Y_{bus}).
 * Short Circuit Solver:
   * Standards: IEC 60909 / ANSI C37.
   * Logic: Calculates symmetrical and asymmetrical fault currents (I_{k}'', I_{p}, I_{b}).
   * Motor Feedback: Dynamic inclusion of induction motor back-feed based on pre-fault voltage.
 * Load Flow & Voltage Drop Solver:
   * Method: Newton-Raphson or Gauss-Seidel iterative methods.
   * Features: Handles Synchronized Bus Ties (closed-loop operation) and calculates phase-by-phase voltage drop, power factor, and active/reactive power flow (P, Q).
 * Validation Logic ("The Red Flag"):
   * Function: Compares calculated results against component ratings.
   * Output: Returns error flags (e.g., Fault > kAIC, V_drop > 5%) to the UI for visualization.
C. The Data Librarian (Database)
 * Component Library:
   * Stores manufacturer data (Cables, Breakers, Transformers, Motors).
   * Key Fields: Impedance (R, X), Thermal Limits (I^2t), Trip Curves (TCC), and Physical Dimensions.
 * Project State: Saves the current topology, user inputs, and calculation results.
 * Standards Library: Contains lookup tables for cable ampacity (IEC 60364-5-52), dielectric constants, and diversity factors.
D. The Reporter (Output Module)
 * Schedule Generator:
   * Automated creation of Cable Schedules, Load Schedules (Panel Directories), and Equipment Lists.
   * Logic: Aggregates loads by parent bus and applies diversity factors.
 * Narrative Analysis Engine:
   * Function: Auto-generates a text-based "Executive Summary" report.
   * Content: Describes the system scope, basis of design, worst-case fault scenarios, and justifications for engineering decisions based on the calculated data.
 * Twin Diagram Generator:
   * Renders the R&X (Resistance & Reactance) Diagram, stripping away symbols and showing the raw impedance map for reviewer validation.
4. Key Features & Capabilities
⚡ Core Analysis
| Feature | Description |
|---|---|
| Short Circuit | Multi-scenario fault analysis (3-Phase, L-G, L-L) with Pass/Fail validation against breaker kAIC ratings. |
| Load Flow | Steady-state power flow analysis to identify overloaded buses, poor power factor, and voltage drops > 5%. |
| Bus Tie Sync | "What-If" scenario manager allowing users to toggle Bus Ties (Open/Closed/Synchronized) to simulate load sharing. |
| Protection | Basic Coordination check and Arc Flash Incident Energy calculation based on clearing times. |
🛠️ Modeling & Data
| Feature | Description |
|---|---|
| Thermal Derating | Auto-correction of cable ampacity based on Installation Method (Tray/Conduit), Grouping, and Ambient Temp. |
| Phase Balancing | Checks load distribution across Phases A, B, and C for single-phase loads. |
| Library Import | Ability to download manufacturer catalogs or bulk-import data via CSV/Excel. |
📊 Visualization & Output
| Feature | Description |
|---|---|
| Heat Map | Color-coded visualization on the SLD (Red = Critical, Orange = Warning, Green = Pass). |
| Data Blocks | Customizable text boxes next to components showing live results (e.g., "14.2 kA"). |
| Comprehensive Report | One-click PDF generation including Cover, Narrative, SLD, R&X Map, and all Schedules. |
5. Development Roadmap (Implementation Plan)
Phase 1: Foundation (Weeks 1-4)
 * Objective: Database & Basic UI Shell.
 * Tasks:
   * Define SQL/JSON Schemas for Cables, Breakers, and Project Metadata.
   * Setup Electron/React environment.
   * Implement the "Library Manager" to allow data entry.
Phase 2: The Drafting Engine (Weeks 5-8)
 * Objective: A working SLD Canvas.
 * Tasks:
   * Implement Drag-and-Drop symbols (Source, Bus, Transformer, Load).
   * Develop the Topology Listener to track connections.
   * Implement the Auto-Tagging Logic (A-VVVV-FFFFF-TTTTT-NN).
Phase 3: The Calculation Core (Weeks 9-12)
 * Objective: Validated Math Results.
 * Tasks:
   * Build the "Per-Unit" conversion module.
   * Implement Short Circuit (IEC 60909) logic.
   * Implement Voltage Drop & Cable Derating logic.
   * Milestone: User can draw a simple circuit and get a correct voltage drop result.
Phase 4: Advanced Logic (Weeks 13-16)
 * Objective: Complex Scenarios.
 * Tasks:
   * Implement Bus Tie Synchronizer and Loop Flow logic.
   * Develop the R&X Twin Diagram generator.
   * Implement "Red-Flag" validation visualization on the canvas.
Phase 5: Reporting & Polish (Weeks 17-20)
 * Objective: "Reviewer-Ready" Outputs.
 * Tasks:
   * Build the Narrative Analysis Engine.
   * Generate PDF/Excel exports for Schedules.
   * Final UI styling and User Acceptance Testing (UAT).
6. Technical Stack Recommendation
 * Frontend: React.js (Component structure) + Konva.js or Fabric.js (Canvas manipulation).
 * Backend API: Python (Flask/FastAPI) using NumPy for matrix operations and Pandas for schedule generation.
 * Database: SQLite (Local storage) / PostgreSQL (Enterprise features).
 * Distribution: Electron (Cross-platform desktop application).
Appendix A: Auto-Tagging Syntax Definition
The system enforces the following unique identifier structure:
[TYPE] - [VOLTAGE_KV] - [SOURCE_TAG] - [DEST_TAG] - [SEQ]
 * Example: C-0.48-MDP1-M1-01
   * C: Cable
   * 0.48: 480V System
   * MDP1: Fed from Main Distribution Panel 1
   * M1: Feeding Motor 1
   * 01: Parallel Run #1

The Missing "Rigof" Factors
Before Phase 1 starts, we should clarify these three items:
 * The "PSP" File Format: We need a custom file extension (e.g., .psp) that is essentially a zipped JSON package containing the diagram, the project metadata, and the local library used. This ensures portability.
 * Verification & Validation (V&V): We need a "Gold Standard" project—a simple system where the math is done by hand (or in ETAP). Every time the developer changes the code, the app must run this "Benchmark" to ensure the results still match.
 * Unit Handling: The app must strictly handle conversions (e.g., HP to kW, feet to meters) in the background so the user can input data in their preferred units without breaking the math.
2. Development Phase Checklists
These checklists define the "Definition of Done" for each phase. A developer shouldn't move to Phase 2 until everything in Phase 1 is checked off.
Phase 1: Foundation & Data Schema
 * [ ] Schema Lockdown: Database tables for Cables, Breakers, Transformers, and Motors are finalized.
 * [ ] Library CRUD: User can Create, Read, Update, and Delete components in the library.
 * [ ] Validation Logic: Library prevents "impossible" data (e.g., negative resistance or 0V voltage).
 * [ ] Import Engine: Working prototype for CSV/Excel data ingestion.
Phase 2: The CAD Canvas & Topology
 * [ ] Node-Link Logic: The software recognizes that "Line A" is connected to "Bus B."
 * [ ] Auto-Tagging: Moving a component triggers an immediate tag update based on the syntax.
 * [ ] Snap-to-Grid: Ensuring a professional, aligned look for the SLD.
 * [ ] Serialization: User can save a drawing to a file and reopen it with 100% data retention.
Phase 3: The Calculation Brain
 * [ ] Per-Unit Engine: Successfull conversion of all R and X values to a common base (S_{base} = 100\text{ MVA}).
 * [ ] The Matrix Solver: The code can build a Nodal Admittance Matrix (Y_{bus}) from the diagram.
 * [ ] Short Circuit V&V: The calculated I_{sc} matches a hand-calculated 3-phase fault for a single-transformer system.
 * [ ] Voltage Drop V&V: Calculated V_d matches the standard formula: V_d = \sqrt{3} \cdot I \cdot (R \cos \phi + X \sin \phi) \cdot L.
Phase 4: Advanced Logic & UI Feedback
 * [ ] Parallel Path Solving: The engine correctly calculates currents when the Bus Tie is closed (Loop flow).
 * [ ] Thermal Derating: Changing "Installation Method" or "Ambient Temp" live-updates the cable's Ampacity rating.
 * [ ] The Red-Flag System: UI components change color (Green to Red) based on calculation thresholds.
 * [ ] The R&X View: A toggle that successfully replaces symbols with their R + jX values.
Phase 5: Reporting & Polish
 * [ ] Narrative Accuracy: The auto-generated text correctly identifies the "Worst Case" bus and the "Longest Path."
 * [ ] Schedule Alignment: Data in the PDF matches the data on the Canvas 1:1.
 * [ ] Export Formats: High-resolution PDF, clean Excel, and basic DXF (AutoCAD) export verified.
 * [ ] Final V&V: The "Comprehensive Narrative" passes a peer review by a Senior Electrical Engineer.
3. Final Architecture "Safety Gate"
One thing we should add to the architecture is a "Calculation History" or "Audit Trail." If a user changes a setting, the app should know that the previous results are now "Invalid" and force a recalculation before allowing a report export. This prevents a user from exporting a "Pass" report for a system that actually "Fails" after a late-stage modification.

To ensure a smooth transition from theory to code, each phase must result in tangible Deliverables. These are the "handover" items that allow the project manager to verify progress.
Here is the expanded Deliverables Roadmap for PwrsysPro Analysis Suite.

Phase 1: Foundation & Data Architecture
Focus: Building the "Source of Truth."
 * Database Schema Document: A full mapping of SQL/JSON tables, including constraints for every electrical parameter (e.g., R, X, Z\%, Ampacity).
 * Library Manager Module: A functional UI where users can input manufacturer data.
 * Standardized Import Templates: Pre-formatted Excel/CSV files for bulk data ingestion (Cables, Breakers, Motors).
 * Validation Script: Code that checks for "Garbage In" (e.g., ensuring a 480V breaker isn't assigned to a 13.8kV bus).
Phase 2: The CAD Canvas & Topology Layer
Focus: The "Digital Twin" interface.
 * Vector Symbol Library: A complete set of industry-standard electrical symbols (IEC/ANSI) optimized for the canvas.
 * Topology Graph Engine: A background module that converts the drawing into a "Node-Link" data structure.
 * The .psp File Format Specification: A technical definition of the proprietary project file format.
 * Auto-Tagging Module: The logic script that generates and updates tags (A-VVVV-FFFFF-TTTTT-NN) in real-time.
Phase 3: The Calculation Core
Focus: Turning the drawing into math.
 * Per-Unit Conversion Module: A script that automatically normalizes all system impedances to a common base MVA.
 * Calculation API Documentation: Internal documentation detailing the formulas used for Short Circuit (IEC 60909) and Voltage Drop.
 * V&V Benchmark Report: A comparison document showing that PwrsysPro results match "Gold Standard" hand-calculated examples.
 * Steady-State Solver: The engine capable of solving V_d and I_{load} for radial systems.
Phase 4: Advanced Logic & Validation
Focus: Intelligence and "What-If" capabilities.
 * Network Loop Solver: Logic capable of handling the "Bus Tie Synchronizer" and parallel load sharing.
 * Thermal Derating Algorithm: A module that calculates I_z (Effective Ampacity) based on installation environment variables.
 * Visual Alert System: The UI components responsible for the "Red-Flag" overlays and the "Heat Map" visualization.
 * R&X Diagram Generator: A sub-module that renders the mathematical twin of the SLD.
Phase 5: Reporting & Final Compiled Build
Focus: The "Professional Product."
 * Reporting Template Suite: Finalized layouts for the Cable Schedule, Load Schedule, and Equipment List.
 * Narrative Generation Engine: The logic that assembles the "Comprehensive Narrative Power System Analysis" into a professional PDF.
 * Export Module: Functionality for PDF, .xlsx, and .dxf (CAD) file generation.
 * Final Compiled Binary: An installation-ready .exe (Windows) or .dmg (Mac) package.
 * Integrated Help/User Manual: A searchable guide embedded within the app.
Summary Checklist of Tangibles
| Phase | Principal Deliverable | Status |
|---|---|---|
| 1 | Validated Component Library & Schema | ▢ |
| 2 | Functional SLD Canvas with Auto-Tagging | ▢ |
| 3 | Validated Math Engine (Radial) | ▢ |
| 4 | Loop Solver & Red-Flag UI | ▢ |
| 5 | Automated "Comprehensive Narrative" Report | ▢ |
PwrsysPro Development "Pro-Tip":
To prevent "Scope Creep," the developer should use Unit Tests for Phase 3. This means every time a new feature is added (like a Bus Tie), the engine automatically re-runs every previous calculation to make sure nothing broke. This is what makes a software "Pro."

