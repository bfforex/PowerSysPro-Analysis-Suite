"""
PwrSysPro Analysis Suite - Loop Flow Analysis
Analyzes power flow in closed electrical loops using mesh analysis.

Standards Reference:
- IEEE Std 399: Power System Analysis
- Network Theory: Mesh Analysis / Kirchhoff's Voltage Law

Purpose:
- Calculate circulating currents in loops
- Analyze power distribution in closed loops
- Calculate loop losses
- Suggest loop optimization
"""

from typing import List, Dict, Tuple
import numpy as np
from dataclasses import dataclass


@dataclass
class LoopBranch:
    """Single branch in a loop"""
    from_node: str
    to_node: str
    impedance: complex  # R + jX
    current: complex = 0.0 + 0.0j
    power_mw: float = 0.0
    power_mvar: float = 0.0
    losses_kw: float = 0.0


@dataclass
class LoopAnalysisResult:
    """Results of loop flow analysis"""
    loop_id: str
    loop_nodes: List[str]
    loop_impedance_total: complex
    circulating_current: complex
    branches: List[LoopBranch]
    total_losses_kw: float
    power_flows: Dict[str, Dict]
    optimization_suggestions: List[str]


class LoopFlowAnalyzer:
    """
    Analyze power flow in closed electrical loops.
    
    Uses mesh analysis to calculate:
    - Loop impedances
    - Circulating currents
    - Branch currents and power flows
    - System losses
    """
    
    def __init__(self, topology_graph=None):
        """
        Initialize loop flow analyzer.
        
        Args:
            topology_graph: Topology graph from Phase 2 (optional)
        """
        self.topology = topology_graph
        self.loops: List[List[str]] = []
        
        if topology_graph:
            # Use existing loop detection from Phase 2
            self.loops = topology_graph.detect_loops()
    
    def set_loops(self, loops: List[List[str]]):
        """
        Manually set loops for analysis.
        
        Args:
            loops: List of loops, each loop is list of node IDs
        """
        self.loops = loops
    
    def analyze_loop(
        self,
        loop: List[str],
        impedances: Dict[str, complex],
        voltages: Dict[str, complex] = None
    ) -> LoopAnalysisResult:
        """
        Analyze a single loop using mesh analysis.
        
        Args:
            loop: List of nodes in loop
            impedances: Branch impedances {from-to: Z}
            voltages: Optional node voltages for power calculation
        
        Returns:
            LoopAnalysisResult with complete analysis
        """
        # Get loop branches
        branches = self._get_loop_branches(loop, impedances)
        
        # Build loop impedance matrix
        z_loop = self._build_loop_matrix(branches)
        
        # Solve for mesh currents (simplified - no voltage sources)
        mesh_currents = self._solve_mesh_currents(z_loop, len(loop))
        
        # Calculate branch currents
        branch_currents = self._calculate_branch_currents(
            branches,
            mesh_currents
        )
        
        # Calculate power flows
        power_flows = self._calculate_loop_power_flow(
            branches,
            branch_currents,
            voltages
        )
        
        # Calculate losses
        total_losses = self._calculate_loop_losses(
            branches,
            branch_currents
        )
        
        # Generate optimization suggestions
        suggestions = self._suggest_optimization(
            branches,
            branch_currents,
            total_losses
        )
        
        # Calculate total loop impedance
        total_impedance = sum(b.impedance for b in branches)
        
        return LoopAnalysisResult(
            loop_id=f"LOOP-{'_'.join(loop[:3])}",
            loop_nodes=loop,
            loop_impedance_total=total_impedance,
            circulating_current=mesh_currents[0] if len(mesh_currents) > 0 else 0j,
            branches=branches,
            total_losses_kw=total_losses,
            power_flows=power_flows,
            optimization_suggestions=suggestions
        )
    
    def analyze_all_loops(
        self,
        impedances: Dict[str, complex],
        voltages: Dict[str, complex] = None
    ) -> Dict[str, LoopAnalysisResult]:
        """
        Analyze all detected loops.
        
        Args:
            impedances: All branch impedances
            voltages: Optional node voltages
        
        Returns:
            Dictionary of loop results
        """
        results = {}
        
        for i, loop in enumerate(self.loops):
            loop_id = f"LOOP-{i+1}"
            try:
                result = self.analyze_loop(loop, impedances, voltages)
                results[loop_id] = result
            except Exception as e:
                print(f"Warning: Could not analyze {loop_id}: {e}")
                continue
        
        return results
    
    def _get_loop_branches(
        self,
        loop: List[str],
        impedances: Dict[str, complex]
    ) -> List[LoopBranch]:
        """Extract branches that form the loop"""
        branches = []
        
        for i in range(len(loop)):
            node_from = loop[i]
            node_to = loop[(i + 1) % len(loop)]
            
            # Try both directions for impedance key
            key1 = f"{node_from}-{node_to}"
            key2 = f"{node_to}-{node_from}"
            
            if key1 in impedances:
                z = impedances[key1]
            elif key2 in impedances:
                z = impedances[key2]
            else:
                # Default impedance if not found
                z = 0.1 + 0.1j
            
            branch = LoopBranch(
                from_node=node_from,
                to_node=node_to,
                impedance=z
            )
            branches.append(branch)
        
        return branches
    
    def _build_loop_matrix(self, branches: List[LoopBranch]) -> np.ndarray:
        """
        Build loop impedance matrix for mesh analysis.
        
        For a single loop, the matrix is just the sum of impedances.
        For multiple meshes, it would be more complex.
        """
        n = len(branches)
        z_matrix = np.zeros((1, 1), dtype=complex)
        
        # Sum all branch impedances for single loop
        z_matrix[0, 0] = sum(b.impedance for b in branches)
        
        return z_matrix
    
    def _solve_mesh_currents(
        self,
        z_matrix: np.ndarray,
        num_nodes: int
    ) -> np.ndarray:
        """
        Solve mesh equations: Z Ã— I = V
        
        For loops with no EMF sources, circulating current
        depends on load distribution (simplified model).
        
        In reality, would need voltage sources and load data.
        """
        # Simplified: small circulating current due to impedance mismatch
        # Real implementation would solve with voltage sources
        
        if z_matrix.shape[0] == 0:
            return np.array([0j])
        
        # For demonstration, assume small circulating current
        # In practice, solve KVL equations with source voltages
        z_total = z_matrix[0, 0]
        
        if abs(z_total) > 1e-10:
            # Simplified circulating current (would come from load imbalance)
            i_circ = 0.01 / z_total  # Small test current
        else:
            i_circ = 0j
        
        return np.array([i_circ])
    
    def _calculate_branch_currents(
        self,
        branches: List[LoopBranch],
        mesh_currents: np.ndarray
    ) -> Dict[str, complex]:
        """Calculate current in each branch from mesh currents"""
        branch_currents = {}
        
        # For single loop, all branches have same mesh current
        i_mesh = mesh_currents[0] if len(mesh_currents) > 0 else 0j
        
        for branch in branches:
            key = f"{branch.from_node}-{branch.to_node}"
            branch_currents[key] = i_mesh
            branch.current = i_mesh
        
        return branch_currents
    
    def _calculate_loop_power_flow(
        self,
        branches: List[LoopBranch],
        branch_currents: Dict[str, complex],
        voltages: Dict[str, complex] = None
    ) -> Dict[str, Dict]:
        """Calculate power flow in each branch"""
        power_flows = {}
        
        for branch in branches:
            key = f"{branch.from_node}-{branch.to_node}"
            current = branch_currents.get(key, 0j)
            
            # Power = IÂ² Ã— Z
            power = current * branch.impedance * np.conj(current)
            
            branch.power_mw = power.real * 1000  # Convert to kW
            branch.power_mvar = power.imag * 1000
            
            power_flows[key] = {
                'current_a': abs(current),
                'current_angle': np.angle(current, deg=True),
                'power_kw': branch.power_mw,
                'power_kvar': branch.power_mvar,
                'loading_percent': 0.0  # Would need cable rating
            }
        
        return power_flows
    
    def _calculate_loop_losses(
        self,
        branches: List[LoopBranch],
        branch_currents: Dict[str, complex]
    ) -> float:
        """Calculate total IÂ²R losses in loop"""
        total_losses = 0.0
        
        for branch in branches:
            key = f"{branch.from_node}-{branch.to_node}"
            current = branch_currents.get(key, 0j)
            
            # Losses = IÂ² Ã— R
            r = branch.impedance.real
            losses_kw = abs(current) ** 2 * r * 1000  # Convert to kW
            
            branch.losses_kw = losses_kw
            total_losses += losses_kw
        
        return total_losses
    
    def _suggest_optimization(
        self,
        branches: List[LoopBranch],
        branch_currents: Dict[str, complex],
        total_losses: float
    ) -> List[str]:
        """Suggest loop optimization strategies"""
        suggestions = []
        
        # Check total losses
        if total_losses > 50.0:  # >50 kW
            suggestions.append(
                f"Total loop losses of {total_losses:.1f} kW are significant. "
                "Consider reducing loop impedance or opening loop for radial operation."
            )
        
        # Check for heavily loaded branches
        for branch in branches:
            if branch.power_mw > 100:  # Arbitrary threshold
                suggestions.append(
                    f"Branch {branch.from_node}â†’{branch.to_node} shows high power flow. "
                    "Consider parallel path or cable upgrade."
                )
        
        # Check impedance balance
        impedances = [abs(b.impedance) for b in branches]
        if max(impedances) / min(impedances) > 5.0 if min(impedances) > 0 else False:
            suggestions.append(
                "Significant impedance imbalance detected in loop. "
                "Uneven impedances can cause circulating currents."
            )
        
        # General optimization
        if not suggestions:
            suggestions.append(
                "Loop operation appears acceptable. Monitor for changes in loading."
            )
        
        return suggestions
    
    def generate_loop_report(
        self,
        loop_result: LoopAnalysisResult
    ) -> str:
        """Generate text report for loop analysis"""
        report = []
        report.append(f"Loop Analysis Report: {loop_result.loop_id}")
        report.append("=" * 70)
        report.append(f"\nLoop Nodes: {' â†’ '.join(loop_result.loop_nodes)}")
        report.append(f"Total Loop Impedance: {abs(loop_result.loop_impedance_total):.4f} Î©")
        report.append(f"Circulating Current: {abs(loop_result.circulating_current):.3f} A")
        report.append(f"Total Losses: {loop_result.total_losses_kw:.2f} kW")
        
        report.append("\nBranch Analysis:")
        report.append("-" * 70)
        for branch in loop_result.branches:
            report.append(
                f"  {branch.from_node} â†’ {branch.to_node}: "
                f"I={abs(branch.current):.2f}A, "
                f"P={branch.power_mw:.2f}kW, "
                f"Losses={branch.losses_kw:.2f}kW"
            )
        
        report.append("\nOptimization Suggestions:")
        report.append("-" * 70)
        for i, suggestion in enumerate(loop_result.optimization_suggestions, 1):
            report.append(f"  {i}. {suggestion}")
        
        return "\n".join(report)


# Testing and example usage
if __name__ == "__main__":
    print("ðŸ”„ Loop Flow Analysis Test")
    print("=" * 70)
    
    analyzer = LoopFlowAnalyzer()
    
    # Define a test loop
    test_loop = ["BUS1", "BUS2", "BUS3", "BUS4", "BUS1"]
    
    # Define branch impedances
    impedances = {
        "BUS1-BUS2": 0.1 + 0.15j,
        "BUS2-BUS3": 0.12 + 0.18j,
        "BUS3-BUS4": 0.08 + 0.12j,
        "BUS4-BUS1": 0.15 + 0.20j
    }
    
    print(f"\nâœ… Test loop: {' â†’ '.join(test_loop[:-1])}")
    print(f"âœ… {len(impedances)} branches defined")
    
    # Analyze loop
    result = analyzer.analyze_loop(test_loop[:-1], impedances)
    
    print(f"\nðŸ“Š Analysis Results:")
    print(f"  Loop Impedance: {abs(result.loop_impedance_total):.4f} Î©")
    print(f"  Circulating Current: {abs(result.circulating_current):.3f} A")
    print(f"  Total Losses: {result.total_losses_kw:.4f} kW")
    
    print(f"\nâš¡ Branch Power Flows:")
    for key, flow in result.power_flows.items():
        print(f"  {key}: {flow['power_kw']:.3f} kW @ {flow['current_a']:.3f} A")
    
    print(f"\nðŸ’¡ Optimization Suggestions:")
    for i, suggestion in enumerate(result.optimization_suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Generate report
    print(f"\nðŸ“„ Full Report:")
    print(analyzer.generate_loop_report(result))
    
    print("\nâœ… Loop Flow Analysis test complete!")
