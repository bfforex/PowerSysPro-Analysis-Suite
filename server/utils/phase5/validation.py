"""
PwrSysPro Analysis Suite - Visual Red-Flag Validation System
Comprehensive validation engine with structured output for visual display.

Purpose:
- Real-time validation of electrical design
- Categorized issues with severity levels
- Support for visual indicators on canvas
- Auto-fix suggestions where possible
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json


class ValidationSeverity(Enum):
    """Severity level for validation issues"""
    CRITICAL = "critical"    # Red - Must fix immediately
    WARNING = "warning"      # Yellow - Should fix
    INFO = "info"            # Blue - FYI/recommendation
    SUCCESS = "success"      # Green - All OK


class ValidationCategory(Enum):
    """Category of validation issue"""
    TOPOLOGY = "topology"              # Network connectivity
    ELECTRICAL = "electrical"          # Electrical violations
    CODE_COMPLIANCE = "code"           # Code/standard compliance
    SAFETY = "safety"                  # Safety concerns
    PERFORMANCE = "performance"        # Performance optimization


@dataclass
class ValidationIssue:
    """Single validation issue with all details"""
    id: str
    severity: ValidationSeverity
    category: ValidationCategory
    title: str
    message: str
    
    # Canvas positioning
    node_id: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    
    # Auto-fix support
    auto_fix_available: bool = False
    fix_description: Optional[str] = None
    fix_action: Optional[str] = None  # Action identifier for backend
    
    # Additional context
    affected_components: List[str] = None
    standard_reference: Optional[str] = None
    
    def __post_init__(self):
        if self.affected_components is None:
            self.affected_components = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'severity': self.severity.value,
            'category': self.category.value,
            'title': self.title,
            'message': self.message,
            'node_id': self.node_id,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'auto_fix_available': self.auto_fix_available,
            'fix_description': self.fix_description,
            'fix_action': self.fix_action,
            'affected_components': self.affected_components,
            'standard_reference': self.standard_reference
        }


class ValidationEngine:
    """
    Comprehensive validation engine for electrical systems.
    
    Performs validation across multiple categories and generates
    structured issues for visual display.
    """
    
    def __init__(self):
        self.issues: List[ValidationIssue] = []
        self.issue_counter = 0
    
    def validate_project(
        self,
        project_data: Dict,
        topology_data: Dict = None,
        analysis_results: Dict = None
    ) -> List[ValidationIssue]:
        """
        Run all validations and return structured issues.
        
        Args:
            project_data: Project and component data
            topology_data: Network topology information
            analysis_results: Results from electrical analysis
        
        Returns:
            List of ValidationIssue objects
        """
        self.issues = []
        self.issue_counter = 0
        
        # Run all validation categories
        self._validate_topology(project_data, topology_data)
        self._validate_electrical(project_data, analysis_results)
        self._validate_code_compliance(project_data)
        self._validate_safety(project_data, analysis_results)
        self._validate_performance(project_data, analysis_results)
        
        return self.issues
    
    def _validate_topology(
        self,
        project_data: Dict,
        topology_data: Dict
    ):
        """Validate network topology and connectivity"""
        nodes = project_data.get('nodes', [])
        connections = project_data.get('connections', [])
        
        # Check for dangling nodes
        connected_nodes = set()
        for conn in connections:
            connected_nodes.add(conn.get('source_node_id'))
            connected_nodes.add(conn.get('target_node_id'))
        
        for node in nodes:
            node_id = node.get('id')
            if node_id not in connected_nodes and node.get('type') != 'Source':
                self._add_issue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.TOPOLOGY,
                    title="Dangling Node",
                    message=f"Component {node.get('custom_tag', node_id)} is not connected",
                    node_id=str(node_id),
                    position_x=node.get('position_x'),
                    position_y=node.get('position_y'),
                    auto_fix_available=False
                )
        
        # Check for missing source
        has_source = any(n.get('type') == 'Source' for n in nodes)
        if not has_source and len(nodes) > 0:
            self._add_issue(
                severity=ValidationSeverity.CRITICAL,
                category=ValidationCategory.TOPOLOGY,
                title="No Power Source",
                message="Network has no power source defined",
                auto_fix_available=False,
                standard_reference="Basic electrical design"
            )
        
        # Check for loops (from topology data if available)
        if topology_data and topology_data.get('loops'):
            loops = topology_data['loops']
            if len(loops) > 0:
                self._add_issue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.TOPOLOGY,
                    title=f"{len(loops)} Loop(s) Detected",
                    message=f"Network contains {len(loops)} closed loop(s). Verify this is intentional.",
                    affected_components=[],
                    auto_fix_available=False
                )
    
    def _validate_electrical(
        self,
        project_data: Dict,
        analysis_results: Dict
    ):
        """Validate electrical parameters and ratings"""
        if not analysis_results:
            return
        
        # Check breaker ratings from short circuit analysis
        sc_results = analysis_results.get('short_circuit', {})
        
        for bus_id, result in sc_results.items():
            if result.get('breaker_status') == 'FAIL':
                self._add_issue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.ELECTRICAL,
                    title="Breaker Rating Exceeded",
                    message=(
                        f"Breaker at {result.get('tag')} rated {result.get('breaker_rating', 0):.1f} kA "
                        f"but fault current is {result.get('i_k3', 0):.1f} kA"
                    ),
                    node_id=result.get('node_id'),
                    position_x=result.get('position_x'),
                    position_y=result.get('position_y'),
                    auto_fix_available=True,
                    fix_description="Upgrade to higher-rated breaker",
                    fix_action="upgrade_breaker",
                    standard_reference="IEC 60909"
                )
        
        # Check voltage limits from load flow
        lf_results = analysis_results.get('load_flow', {})
        if lf_results.get('converged'):
            buses = lf_results.get('buses', {})
            for bus_id, bus_data in buses.items():
                voltage_pu = bus_data.get('voltage', 1.0)
                
                if voltage_pu < 0.95:
                    self._add_issue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.ELECTRICAL,
                        title="Low Voltage",
                        message=(
                            f"Bus {bus_data.get('tag')} voltage {voltage_pu:.3f} pu "
                            f"is below 0.95 pu limit"
                        ),
                        node_id=bus_data.get('node_id'),
                        auto_fix_available=False,
                        standard_reference="Voltage regulation standards"
                    )
                elif voltage_pu > 1.05:
                    self._add_issue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.ELECTRICAL,
                        title="High Voltage",
                        message=(
                            f"Bus {bus_data.get('tag')} voltage {voltage_pu:.3f} pu "
                            f"exceeds 1.05 pu limit"
                        ),
                        node_id=bus_data.get('node_id'),
                        auto_fix_available=False,
                        standard_reference="Voltage regulation standards"
                    )
    
    def _validate_code_compliance(self, project_data: Dict):
        """Validate code compliance (IEC, NEC, etc.)"""
        connections = project_data.get('connections', [])
        
        # Check cable sizing (simplified)
        for conn in connections:
            length = conn.get('length', 0)
            if length > 500:  # meters
                self._add_issue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.CODE_COMPLIANCE,
                    title="Long Cable Run",
                    message=(
                        f"Cable run of {length}m exceeds typical limits. "
                        f"Verify voltage drop compliance."
                    ),
                    auto_fix_available=False,
                    standard_reference="IEC 60364-5-52"
                )
    
    def _validate_safety(
        self,
        project_data: Dict,
        analysis_results: Dict
    ):
        """Validate safety requirements"""
        if not analysis_results:
            return
        
        # Check arc flash hazards
        af_results = analysis_results.get('arc_flash', {})
        
        for bus_id, result in af_results.items():
            incident_energy = result.get('incident_energy', 0)
            
            if incident_energy > 40:
                self._add_issue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.SAFETY,
                    title="Extreme Arc Flash Hazard",
                    message=(
                        f"Bus {result.get('tag')} has incident energy "
                        f"{incident_energy:.1f} cal/cmÂ² (>40). "
                        f"De-energization strongly recommended."
                    ),
                    node_id=result.get('node_id'),
                    position_x=result.get('position_x'),
                    position_y=result.get('position_y'),
                    auto_fix_available=False,
                    standard_reference="NFPA 70E"
                )
            elif incident_energy > 25:
                self._add_issue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.SAFETY,
                    title="High Arc Flash Hazard",
                    message=(
                        f"Bus {result.get('tag')} requires PPE Category 4. "
                        f"Incident energy: {incident_energy:.1f} cal/cmÂ²"
                    ),
                    node_id=result.get('node_id'),
                    auto_fix_available=False,
                    standard_reference="NFPA 70E Table 130.5(G)"
                )
    
    def _validate_performance(
        self,
        project_data: Dict,
        analysis_results: Dict
    ):
        """Validate system performance and optimization"""
        if not analysis_results:
            return
        
        lf_results = analysis_results.get('load_flow', {})
        
        # Check system losses
        if lf_results.get('converged'):
            losses_percent = lf_results.get('loss_percent', 0)
            
            if losses_percent > 5.0:
                self._add_issue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    title="High System Losses",
                    message=(
                        f"Total system losses of {losses_percent:.1f}% "
                        f"exceed typical 3-5% range. Consider optimization."
                    ),
                    auto_fix_available=False
                )
    
    def _add_issue(
        self,
        severity: ValidationSeverity,
        category: ValidationCategory,
        title: str,
        message: str,
        **kwargs
    ):
        """Add an issue to the validation results"""
        self.issue_counter += 1
        
        issue = ValidationIssue(
            id=f"VAL-{self.issue_counter:04d}",
            severity=severity,
            category=category,
            title=title,
            message=message,
            **kwargs
        )
        
        self.issues.append(issue)
    
    def get_summary(self) -> Dict:
        """Get validation summary statistics"""
        summary = {
            'total_issues': len(self.issues),
            'critical': sum(1 for i in self.issues if i.severity == ValidationSeverity.CRITICAL),
            'warning': sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING),
            'info': sum(1 for i in self.issues if i.severity == ValidationSeverity.INFO),
            'by_category': {}
        }
        
        for category in ValidationCategory:
            count = sum(1 for i in self.issues if i.category == category)
            if count > 0:
                summary['by_category'][category.value] = count
        
        return summary
    
    def to_json(self) -> str:
        """Export all issues as JSON"""
        return json.dumps(
            {
                'issues': [issue.to_dict() for issue in self.issues],
                'summary': self.get_summary()
            },
            indent=2
        )


# Testing and example usage
if __name__ == "__main__":
    print("ðŸš¨ Visual Red-Flag Validation Test")
    print("=" * 70)
    
    engine = ValidationEngine()
    
    # Create test project data
    test_project = {
        'nodes': [
            {'id': 1, 'type': 'Source', 'custom_tag': 'SOURCE-01', 'position_x': 100, 'position_y': 100},
            {'id': 2, 'type': 'Breaker', 'custom_tag': 'CB-01', 'position_x': 200, 'position_y': 100},
            {'id': 3, 'type': 'Motor', 'custom_tag': 'MOTOR-01', 'position_x': 300, 'position_y': 100},
            {'id': 4, 'type': 'Load', 'custom_tag': 'LOAD-01', 'position_x': 400, 'position_y': 100}
        ],
        'connections': [
            {'source_node_id': 1, 'target_node_id': 2},
            {'source_node_id': 2, 'target_node_id': 3}
            # Node 4 is dangling - intentionally not connected
        ]
    }
    
    # Test analysis results
    test_analysis = {
        'short_circuit': {
            'bus2': {
                'tag': 'CB-01',
                'i_k3': 28.5,
                'breaker_rating': 25.0,
                'breaker_status': 'FAIL',
                'node_id': '2',
                'position_x': 200,
                'position_y': 100
            }
        },
        'arc_flash': {
            'bus2': {
                'tag': 'CB-01',
                'incident_energy': 32.5,
                'node_id': '2',
                'position_x': 200,
                'position_y': 100
            }
        },
        'load_flow': {
            'converged': True,
            'loss_percent': 6.2,
            'buses': {
                'bus3': {
                    'tag': 'MOTOR-01',
                    'voltage': 0.92,
                    'node_id': '3'
                }
            }
        }
    }
    
    # Run validation
    issues = engine.validate_project(test_project, None, test_analysis)
    
    print(f"\nâœ… Validation complete: {len(issues)} issues found")
    
    # Display summary
    summary = engine.get_summary()
    print(f"\nðŸ“Š Summary:")
    print(f"  Total Issues: {summary['total_issues']}")
    print(f"  Critical: {summary['critical']}")
    print(f"  Warnings: {summary['warning']}")
    print(f"  Info: {summary['info']}")
    
    # Display issues by severity
    print(f"\nðŸš¨ Issues by Severity:")
    for issue in issues:
        icon = {
            ValidationSeverity.CRITICAL: "ðŸ”´",
            ValidationSeverity.WARNING: "âš ï¸",
            ValidationSeverity.INFO: "â„¹ï¸",
            ValidationSeverity.SUCCESS: "âœ…"
        }.get(issue.severity, "â€¢")
        
        print(f"  {icon} [{issue.severity.value.upper()}] {issue.title}")
        print(f"     {issue.message}")
        if issue.auto_fix_available:
            print(f"     ðŸ”§ Auto-fix: {issue.fix_description}")
    
    print("\nâœ… Visual Red-Flag Validation test complete!")
