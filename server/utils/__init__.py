"""
PwrSysPro Analysis Suite - Utilities Package
All calculation modules organized by implementation phase
"""

# Phase 1: Foundation
from .phase1.calculations import (
    calculate_voltage_drop_three_phase,
    calculate_cable_derating_factor,
    CableParameters,
    LoadParameters
)
from .phase1.tagging import generate_tag

# Phase 2: Topology & Files
from .phase2.topology import TopologyGraph, build_topology_from_database
from .phase2.serialization import PSPFileFormat
from .phase2.tagging_enhanced import SmartTagManager, update_all_tags

# Phase 3: Calculation Core
from .phase3.per_unit import PerUnitSystem
from .phase3.short_circuit import IEC60909Calculator, ShortCircuitParameters
from .phase3.load_flow import NewtonRaphsonLoadFlow, BusType
from .phase3.integrated_calc import IntegratedCalculationService

# Phase 4: Bonus Features
from .phase4.arc_flash import IEEE1584ArcFlashCalculator, calculate_arc_flash_for_bus
from .phase4.report_generator import PwrSysProReportGenerator, generate_analysis_report
from .phase4.protection import ProtectionCoordinator, ProtectiveDeviceSettings

# Phase 5: Advanced Features
from .phase5.rx_diagram import RXDiagramGenerator, generate_rx_diagram_from_project
from .phase5.bus_tie import BusTieController, BusParameters, BusTieParameters, TransferMode
from .phase5.loop_analysis import LoopFlowAnalyzer, LoopAnalysisResult
from .phase5.validation import ValidationEngine, ValidationIssue, ValidationSeverity
from .phase5.narrative_generator import NarrativeGenerator
from .phase5.excel_export import ExcelExporter

__all__ = [
    # Phase 1
    'calculate_voltage_drop_three_phase',
    'calculate_cable_derating_factor',
    'CableParameters',
    'LoadParameters',
    'generate_tag',
    
    # Phase 2
    'TopologyGraph',
    'build_topology_from_database',
    'PSPFileFormat',
    'SmartTagManager',
    'update_all_tags',
    
    # Phase 3
    'PerUnitSystem',
    'IEC60909Calculator',
    'ShortCircuitParameters',
    'NewtonRaphsonLoadFlow',
    'BusType',
    'IntegratedCalculationService',
    
    # Phase 4
    'IEEE1584ArcFlashCalculator',
    'calculate_arc_flash_for_bus',
    'PwrSysProReportGenerator',
    'generate_analysis_report',
    'ProtectionCoordinator',
    'ProtectiveDeviceSettings',
    
    # Phase 5
    'RXDiagramGenerator',
    'generate_rx_diagram_from_project',
    'BusTieController',
    'BusParameters',
    'BusTieParameters',
    'TransferMode',
    'LoopFlowAnalyzer',
    'LoopAnalysisResult',
    'ValidationEngine',
    'ValidationIssue',
    'ValidationSeverity',
    'NarrativeGenerator',
    'ExcelExporter',
]

__version__ = '5.0.0'
