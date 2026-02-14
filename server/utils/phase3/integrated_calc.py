"""
PwrSysPro Analysis Suite - Integrated Calculation Service (Phase 3)
Combines per-unit system, short circuit, and load flow calculations
into a unified analysis framework.

This service:
1. Builds per-unit system from project data
2. Constructs Y-bus matrix from topology
3. Runs short circuit analysis at all buses
4. Performs load flow analysis
5. Validates results against component ratings
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

from utils.topology import TopologyGraph, TopologyNode
from utils.per_unit import (
    PerUnitSystem,
    convert_cable_impedance_to_pu,
    convert_transformer_impedance_to_pu,
    convert_motor_impedance_to_pu,
    build_admittance_matrix
)
from utils.short_circuit import (
    IEC60909Calculator,
    ShortCircuitParameters,
    ShortCircuitResult,
    calculate_motor_contribution,
    validate_breaker_rating
)
from utils.load_flow import (
    NewtonRaphsonLoadFlow,
    Bus as LoadFlowBus,
    BusType,
    LoadFlowResult
)


@dataclass
class NetworkAnalysisResult:
    """Complete network analysis results."""
    per_unit_system: Dict
    y_bus_matrix: np.ndarray
    short_circuit_results: Dict[str, ShortCircuitResult]
    load_flow_result: Optional[LoadFlowResult]
    breaker_validations: Dict[str, Dict]
    summary: Dict


class IntegratedCalculationService:
    """
    Integrated calculation service for complete power system analysis.
    """
    
    def __init__(self, base_mva: float = 100.0, system_frequency: float = 50.0):
        """
        Initialize calculation service.
        
        Args:
            base_mva: System base MVA
            system_frequency: System frequency (Hz)
        """
        self.base_mva = base_mva
        self.system_frequency = system_frequency
        self.pu_system = PerUnitSystem(base_mva)
    
    def analyze_network(
        self,
        topology: TopologyGraph,
        component_data: Dict[str, Dict],
        run_load_flow: bool = True
    ) -> NetworkAnalysisResult:
        """
        Perform complete network analysis.
        
        Args:
            topology: Network topology graph
            component_data: Component specifications from database
            run_load_flow: Whether to run load flow analysis
        
        Returns:
            NetworkAnalysisResult with all calculations
        """
        # Step 1: Build per-unit system
        print("ðŸ“Š Step 1: Building per-unit system...")
        self._build_per_unit_system(topology)
        
        # Step 2: Convert all impedances to per-unit
        print("ðŸ”„ Step 2: Converting impedances...")
        impedances_pu = self._convert_network_impedances(topology, component_data)
        
        # Step 3: Build Y-bus matrix
        print("âš¡ Step 3: Building Y-bus matrix...")
        y_bus = self._build_ybus(topology, impedances_pu)
        
        # Step 4: Short circuit analysis
        print("âš¡ Step 4: Running short circuit analysis...")
        sc_results = self._analyze_short_circuits(topology, impedances_pu, component_data)
        
        # Step 5: Load flow analysis (optional)
        load_flow_result = None
        if run_load_flow:
            print("ðŸ“ˆ Step 5: Running load flow analysis...")
            load_flow_result = self._analyze_load_flow(topology, y_bus)
        
        # Step 6: Breaker validation
        print("ðŸ”’ Step 6: Validating breaker ratings...")
        breaker_validations = self._validate_breakers(topology, sc_results, component_data)
        
        # Compile summary
        summary = self._compile_summary(sc_results, load_flow_result, breaker_validations)
        
        return NetworkAnalysisResult(
            per_unit_system={
                'base_mva': self.base_mva,
                'voltage_bases': {
                    v: {'z_base': base.impedance_ohms, 'i_base': base.current_amps}
                    for v, base in self.pu_system.voltage_bases.items()
                }
            },
            y_bus_matrix=y_bus,
            short_circuit_results=sc_results,
            load_flow_result=load_flow_result,
            breaker_validations=breaker_validations,
            summary=summary
        )
    
    def _build_per_unit_system(self, topology: TopologyGraph):
        """Build per-unit system with all voltage levels."""
        for node in topology.nodes.values():
            voltage_kv = node.voltage_level
            self.pu_system.add_voltage_level(voltage_kv)
    
    def _convert_network_impedances(
        self,
        topology: TopologyGraph,
        component_data: Dict[str, Dict]
    ) -> Dict[Tuple[str, str], complex]:
        """Convert all network impedances to per-unit."""
        impedances_pu = {}
        
        for edge_id, edge in topology.edges.items():
            source_node = topology.nodes[edge.source_id]
            target_node = topology.nodes[edge.target_id]
            
            # Get component data
            if edge.cable_id and edge.cable_id in component_data:
                cable = component_data[edge.cable_id]
                
                # Convert cable impedance
                z_pu = convert_cable_impedance_to_pu(
                    resistance_per_km=cable.get('impedance_r', 0.161),
                    reactance_per_km=cable.get('impedance_x', 0.086),
                    length_km=edge.length / 1000.0,  # Convert m to km
                    voltage_kv=source_node.voltage_level,
                    base_mva=self.base_mva
                )
                
                impedances_pu[(edge.source_id, edge.target_id)] = z_pu
            
            # Handle transformers
            if source_node.type == "Transformer" or target_node.type == "Transformer":
                # Get transformer data
                transformer = component_data.get(source_node.id, {})
                if 'impedance_z_percent' in transformer:
                    z_pri, z_sec = convert_transformer_impedance_to_pu(
                        z_percent=transformer['impedance_z_percent'],
                        transformer_mva=transformer.get('rating_mva', 1.0),
                        voltage_primary_kv=source_node.voltage_level,
                        voltage_secondary_kv=target_node.voltage_level,
                        base_mva=self.base_mva
                    )
                    impedances_pu[(edge.source_id, edge.target_id)] = z_sec
        
        return impedances_pu
    
    def _build_ybus(
        self,
        topology: TopologyGraph,
        impedances_pu: Dict[Tuple[str, str], complex]
    ) -> np.ndarray:
        """Build nodal admittance matrix."""
        nodes = list(topology.nodes.keys())
        return build_admittance_matrix(nodes, impedances_pu)
    
    def _analyze_short_circuits(
        self,
        topology: TopologyGraph,
        impedances_pu: Dict[Tuple[str, str], complex],
        component_data: Dict[str, Dict]
    ) -> Dict[str, ShortCircuitResult]:
        """Analyze short circuits at all buses."""
        results = {}
        
        # Identify motor nodes for contribution calculation
        motors = []
        for node in topology.nodes.values():
            if node.type == "Motor":
                motor_data = component_data.get(node.id, {})
                if 'power_kw' in motor_data:
                    motors.append({
                        'power_kw': motor_data['power_kw'],
                        'voltage_kv': node.voltage_level
                    })
        
        # Calculate motor contribution
        z_motor = calculate_motor_contribution(motors, self.base_mva) if motors else None
        
        # Analyze each bus
        for node in topology.nodes.values():
            if node.type in ["Bus", "Busbar", "Load", "Motor"]:
                # Find path impedance from source to this node
                path = topology.find_path(topology.sources[0], node.id) if topology.sources else None
                
                if path:
                    # Calculate total impedance to fault point
                    z_fault = 0j
                    for i in range(len(path) - 1):
                        edge_key = (path[i], path[i+1])
                        if edge_key in impedances_pu:
                            z_fault += impedances_pu[edge_key]
                    
                    # Short circuit parameters
                    params = ShortCircuitParameters(
                        voltage_kv=node.voltage_level,
                        base_mva=self.base_mva,
                        source_impedance=0.05 + 0.5j,  # Utility impedance
                        voltage_factor_c=1.1,
                        frequency_hz=self.system_frequency
                    )
                    
                    # Calculate fault
                    calculator = IEC60909Calculator(params)
                    result = calculator.calculate_three_phase_fault(z_fault, z_motor)
                    
                    results[node.id] = result
        
        return results
    
    def _analyze_load_flow(
        self,
        topology: TopologyGraph,
        y_bus: np.ndarray
    ) -> Optional[LoadFlowResult]:
        """Run load flow analysis."""
        try:
            # Build bus dictionary for load flow
            buses = {}
            bus_index = {}
            
            for idx, (node_id, node) in enumerate(topology.nodes.items()):
                # Classify bus type
                if node.type == "Source":
                    bus_type = BusType.SLACK
                    p_spec = 0.0
                    q_spec = 0.0
                    v_spec = 1.0
                elif node.type in ["Motor", "Load"]:
                    bus_type = BusType.PQ
                    # Estimated load in pu
                    p_spec = -0.5  # Simplified
                    q_spec = -0.2
                    v_spec = 1.0
                else:
                    bus_type = BusType.PQ
                    p_spec = 0.0
                    q_spec = 0.0
                    v_spec = 1.0
                
                buses[node_id] = LoadFlowBus(
                    id=node_id,
                    bus_type=bus_type,
                    p_specified=p_spec,
                    q_specified=q_spec,
                    v_specified=v_spec
                )
                bus_index[node_id] = idx
            
            # Solve load flow
            solver = NewtonRaphsonLoadFlow(buses, y_bus, bus_index)
            result = solver.solve()
            
            return result
        
        except Exception as e:
            print(f"Load flow failed: {e}")
            return None
    
    def _validate_breakers(
        self,
        topology: TopologyGraph,
        sc_results: Dict[str, ShortCircuitResult],
        component_data: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """Validate all breakers against short circuit currents."""
        validations = {}
        
        for node in topology.nodes.values():
            if node.type == "Breaker":
                # Get breaker data
                breaker = component_data.get(node.id, {})
                breaker_rating = breaker.get('short_circuit_rating', 10.0)  # kA
                
                # Find downstream fault current
                downstream = topology.get_downstream_nodes(node.id)
                max_fault_current = 0.0
                
                for down_id in downstream:
                    if down_id in sc_results:
                        fault_i = sc_results[down_id].i_k3_initial
                        if fault_i > max_fault_current:
                            max_fault_current = fault_i
                
                # Validate
                if max_fault_current > 0:
                    validation = validate_breaker_rating(
                        fault_current_ka=max_fault_current,
                        breaker_rating_ka=breaker_rating,
                        voltage_kv=node.voltage_level
                    )
                    validations[node.id] = validation
        
        return validations
    
    def _compile_summary(
        self,
        sc_results: Dict[str, ShortCircuitResult],
        lf_result: Optional[LoadFlowResult],
        breaker_vals: Dict[str, Dict]
    ) -> Dict:
        """Compile analysis summary."""
        # Find maximum fault current
        max_fault = 0.0
        max_fault_bus = None
        for bus_id, result in sc_results.items():
            if result.i_k3_initial > max_fault:
                max_fault = result.i_k3_initial
                max_fault_bus = bus_id
        
        # Count breaker issues
        breakers_pass = sum(1 for v in breaker_vals.values() if v['is_adequate'])
        breakers_fail = len(breaker_vals) - breakers_pass
        
        summary = {
            'short_circuit': {
                'buses_analyzed': len(sc_results),
                'max_fault_current_ka': round(max_fault, 2),
                'max_fault_bus': max_fault_bus
            },
            'breakers': {
                'total': len(breaker_vals),
                'pass': breakers_pass,
                'fail': breakers_fail
            }
        }
        
        if lf_result:
            summary['load_flow'] = {
                'converged': lf_result.converged,
                'iterations': lf_result.iterations,
                'total_load_mw': round(lf_result.total_load_p * self.base_mva, 2),
                'total_losses_mw': round(lf_result.total_losses_p * self.base_mva, 2)
            }
        
        return summary


# Example usage
if __name__ == "__main__":
    print("âš¡ Integrated Calculation Service Test")
    print("=" * 70)
    print("This service combines:")
    print("  1. Per-unit system")
    print("  2. Short circuit analysis (IEC 60909)")
    print("  3. Load flow analysis (Newton-Raphson)")
    print("  4. Breaker validation")
    print("=" * 70)
    print("\nâœ… Service ready for integration!")
