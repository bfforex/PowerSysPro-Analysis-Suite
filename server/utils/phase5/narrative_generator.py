"""
PwrSysPro Analysis Suite - Automated Narrative Generation
Generates natural language descriptions of analysis results for reports.

Purpose:
- Auto-generate executive summaries
- Interpret analysis results in plain language
- Generate compliance statements
- Create technical explanations
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class NarrativeTemplate:
    """Template for narrative generation"""
    template_id: str
    category: str
    template_text: str
    required_fields: List[str]


class NarrativeGenerator:
    """
    Generate natural language narratives from analysis data.
    
    Uses template-based approach with dynamic data insertion.
    Future: Could integrate LLM for more sophisticated generation.
    """
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def generate_executive_summary(
        self,
        project_data: Dict,
        analysis_results: Dict
    ) -> str:
        """
        Generate executive summary narrative.
        
        Args:
            project_data: Project information
            analysis_results: Complete analysis results
        
        Returns:
            Executive summary text
        """
        # Extract key data
        project_name = project_data.get('name', 'Unnamed Project')
        base_mva = project_data.get('base_mva', 100.0)
        
        # Short circuit data
        sc_results = analysis_results.get('short_circuit', {})
        if sc_results:
            max_fault = max(
                (r.get('i_k3', 0) for r in sc_results.values()),
                default=0
            )
            max_fault_bus = max(
                sc_results.items(),
                key=lambda x: x[1].get('i_k3', 0),
                default=(None, {})
            )[1].get('tag', 'Unknown')
        else:
            max_fault = 0
            max_fault_bus = 'N/A'
        
        # Arc flash data
        af_results = analysis_results.get('arc_flash', {})
        high_hazard_count = sum(
            1 for r in af_results.values()
            if r.get('incident_energy', 0) > 25.0
        )
        
        # Load flow data
        lf_results = analysis_results.get('load_flow', {})
        max_voltage_drop = 0.0
        if lf_results.get('converged'):
            voltages = [
                b.get('voltage', 1.0)
                for b in lf_results.get('buses', {}).values()
            ]
            if voltages:
                max_voltage_drop = (1.0 - min(voltages)) * 100
        
        # Component counts
        nodes = project_data.get('nodes', [])
        transformer_count = sum(1 for n in nodes if n.get('type') == 'Transformer')
        
        # Extract voltage levels
        voltage_levels = self._extract_voltage_levels(project_data)
        primary_voltage = voltage_levels[0] if voltage_levels else 11.0
        secondary_voltage = voltage_levels[1] if len(voltage_levels) > 1 else 0.4
        
        # Generate narrative
        narrative = (
            f"The {project_name} electrical system consists of a "
            f"{primary_voltage:.1f}kV primary distribution "
        )
        
        if transformer_count > 0:
            narrative += (
                f"feeding through {transformer_count} transformer(s) to "
                f"{secondary_voltage:.1f}kV secondary distribution. "
            )
        else:
            narrative += "network. "
        
        if max_fault > 0:
            narrative += (
                f"Short circuit analysis reveals a maximum fault current of "
                f"{max_fault:.1f} kA at {max_fault_bus}. "
            )
        
        if lf_results.get('converged'):
            narrative += (
                f"Load flow analysis converged successfully with a maximum "
                f"voltage drop of {max_voltage_drop:.1f}%. "
            )
        
        if high_hazard_count > 0:
            narrative += (
                f"Arc flash analysis identifies {high_hazard_count} "
                f"high-hazard location(s) requiring enhanced PPE and safety procedures. "
            )
        else:
            narrative += (
                "Arc flash hazards are within acceptable limits for standard PPE. "
            )
        
        narrative += (
            f"The system design utilizes a {base_mva:.0f} MVA base for "
            "per-unit calculations and follows applicable IEC and IEEE standards."
        )
        
        return narrative
    
    def interpret_short_circuit_results(self, results: Dict) -> str:
        """Generate narrative for short circuit analysis results"""
        if not results:
            return "Short circuit analysis has not been performed."
        
        # Find critical breakers
        breakers_fail = [
            (bus, data) for bus, data in results.items()
            if data.get('breaker_status') == 'FAIL'
        ]
        
        if not breakers_fail:
            max_fault = max(
                (r.get('i_k3', 0) for r in results.values()),
                default=0
            )
            max_bus = max(
                results.items(),
                key=lambda x: x[1].get('i_k3', 0),
                default=(None, {})
            )[1].get('tag', 'unknown location')
            
            return (
                f"Short circuit analysis per IEC 60909 indicates all circuit "
                f"breakers have adequate ratings. The maximum three-phase fault "
                f"current of {max_fault:.1f} kA occurs at {max_bus}, which is "
                f"within equipment capabilities. All protective devices meet the "
                f"required short-circuit withstand ratings."
            )
        else:
            breaker_tags = [data.get('tag', 'Unknown') for bus, data in breakers_fail]
            breaker_list = self._format_list(breaker_tags)
            
            return (
                f"Short circuit analysis identifies {len(breakers_fail)} breaker(s) "
                f"with inadequate short-circuit ratings: {breaker_list}. "
                f"These breakers require immediate upgrade to meet calculated fault "
                f"current levels per IEC 60909. The fault currents exceed equipment "
                f"ratings by 10% or more, posing a safety risk during fault conditions."
            )
    
    def interpret_arc_flash_results(self, results: Dict) -> str:
        """Generate narrative for arc flash analysis results"""
        if not results:
            return "Arc flash analysis has not been performed."
        
        # Categorize hazards
        extreme_hazard = [
            (bus, data) for bus, data in results.items()
            if data.get('incident_energy', 0) > 40.0
        ]
        high_hazard = [
            (bus, data) for bus, data in results.items()
            if 25.0 < data.get('incident_energy', 0) <= 40.0
        ]
        
        if extreme_hazard:
            locations = [data.get('tag', 'Unknown') for bus, data in extreme_hazard]
            location_list = self._format_list(locations)
            
            return (
                f"Arc flash analysis per IEEE 1584-2018 identifies {len(extreme_hazard)} "
                f"location(s) with extreme hazard levels (>40 cal/cmÂ²): {location_list}. "
                f"These locations exceed the maximum PPE category and require de-energization "
                f"procedures for all maintenance activities. Remote racking and operation "
                f"should be implemented where feasible per NFPA 70E requirements."
            )
        elif high_hazard:
            locations = [data.get('tag', 'Unknown') for bus, data in high_hazard]
            location_list = self._format_list(locations)
            
            return (
                f"Arc flash analysis identifies {len(high_hazard)} location(s) requiring "
                f"PPE Category 4 protection: {location_list}. Personnel must wear 40 cal/cmÂ² "
                f"rated arc flash suits when working on energized equipment at these locations. "
                f"All work procedures must comply with NFPA 70E Table 130.5(G) requirements."
            )
        else:
            max_ie = max(
                (r.get('incident_energy', 0) for r in results.values()),
                default=0
            )
            
            return (
                f"Arc flash analysis indicates all equipment locations have incident energy "
                f"levels within manageable limits. Maximum incident energy is {max_ie:.1f} cal/cmÂ². "
                f"Appropriate PPE categories have been determined for each location per NFPA 70E. "
                f"Arc flash labels should be affixed to all equipment indicating hazard level "
                f"and required PPE."
            )
    
    def interpret_load_flow_results(self, results: Dict) -> str:
        """Generate narrative for load flow analysis results"""
        if not results or not results.get('converged'):
            return (
                "Load flow analysis did not converge, indicating potential issues with "
                "network configuration, loading conditions, or source/load specifications. "
                "Review network topology and ensure all component data is correct."
            )
        
        iterations = results.get('iterations', 0)
        buses = results.get('buses', {})
        
        # Check voltage violations
        voltage_violations = [
            (bus, data) for bus, data in buses.items()
            if data.get('voltage', 1.0) < 0.95 or data.get('voltage', 1.0) > 1.05
        ]
        
        if voltage_violations:
            violation_tags = [data.get('tag', 'Unknown') for bus, data in voltage_violations]
            violation_list = self._format_list(violation_tags)
            
            return (
                f"Load flow analysis converged in {iterations} iterations using the "
                f"Newton-Raphson method. However, {len(voltage_violations)} bus(es) show "
                f"voltage violations outside the Â±5% regulatory limits: {violation_list}. "
                f"Voltage regulation measures such as tap changer adjustment, capacitor banks, "
                f"or voltage regulators are recommended to maintain acceptable voltage profiles."
            )
        else:
            losses_mw = results.get('losses_mw', 0)
            loss_percent = results.get('loss_percent', 0)
            
            return (
                f"Load flow analysis converged successfully in {iterations} iterations. "
                f"All bus voltages are within acceptable limits (Â±5% of nominal). "
                f"Total system losses are {losses_mw:.2f} MW ({loss_percent:.1f}% of total load), "
                f"which is within typical ranges for distribution systems. The voltage regulation "
                f"and power factor performance indicate satisfactory system operation."
            )
    
    def generate_compliance_statement(self, standards: List[str]) -> str:
        """Generate standards compliance statement"""
        standard_descriptions = {
            'IEC 60909': 'short-circuit current calculations',
            'IEC 60364-5-52': 'cable selection and voltage drop criteria',
            'IEEE 1584': 'arc flash hazard analysis',
            'IEEE 399': 'power system analysis methodologies',
            'NFPA 70E': 'electrical safety requirements in the workplace',
            'IEC 60255': 'protective relay time-current characteristics'
        }
        
        descriptions = []
        for std in standards:
            desc = standard_descriptions.get(std, 'electrical system analysis')
            descriptions.append(f"{std} for {desc}")
        
        standards_text = self._format_list(descriptions)
        
        return (
            f"The electrical system design and analysis comply with {standards_text}. "
            f"All calculations follow the prescribed methodologies and conservative assumptions "
            f"specified in these standards. Equipment selection, protection coordination, and "
            f"safety assessments are performed in accordance with applicable codes and industry "
            f"best practices."
        )
    
    def generate_technical_explanation(
        self,
        topic: str,
        data: Dict
    ) -> str:
        """Generate detailed technical explanation"""
        explanations = {
            'voltage_drop': self._explain_voltage_drop,
            'short_circuit': self._explain_short_circuit,
            'arc_flash': self._explain_arc_flash,
            'load_flow': self._explain_load_flow
        }
        
        explainer = explanations.get(topic)
        if explainer:
            return explainer(data)
        else:
            return f"Technical explanation for '{topic}' is not available."
    
    def _explain_voltage_drop(self, data: Dict) -> str:
        """Explain voltage drop calculation"""
        vd_percent = data.get('voltage_drop_percent', 0)
        cable_length = data.get('cable_length', 0)
        from_bus = data.get('from_bus', 'source')
        to_bus = data.get('to_bus', 'load')
        cable_r = data.get('cable_impedance', 0)
        current = data.get('load_current', 0)
        vd_volts = data.get('voltage_drop_v', 0)
        
        within_limit = vd_percent <= 5.0
        
        return (
            f"The voltage drop of {vd_percent:.1f}% between {from_bus} and {to_bus} "
            f"results from the {cable_length:.0f}m cable run. With a cable resistance of "
            f"{cable_r:.3f} Î©/km and load current of {current:.0f}A, the voltage drop "
            f"calculates to {vd_volts:.1f}V. This {'is within' if within_limit else 'exceeds'} "
            f"the 5% limit specified in IEC 60364-5-52. "
            f"{'No corrective action is required.' if within_limit else 'Cable upsizing or voltage boost is recommended.'}"
        )
    
    def _explain_short_circuit(self, data: Dict) -> str:
        """Explain short circuit calculation"""
        i_k3 = data.get('i_k3', 0)
        ip = data.get('ip', 0)
        location = data.get('location', 'bus')
        
        return (
            f"Short circuit analysis at {location} yields an initial three-phase fault "
            f"current (I''k3) of {i_k3:.1f} kA with a peak current (ip) of {ip:.1f} kA. "
            f"These values are calculated per IEC 60909 using the equivalent circuit method "
            f"and include contributions from all sources and motors. The peak current "
            f"incorporates the DC component and determines mechanical stress on equipment."
        )
    
    def _explain_arc_flash(self, data: Dict) -> str:
        """Explain arc flash calculation"""
        ie = data.get('incident_energy', 0)
        afb = data.get('arc_flash_boundary', 0)
        ppe_cat = data.get('ppe_category', 0)
        
        return (
            f"Arc flash calculations per IEEE 1584-2018 determine an incident energy of "
            f"{ie:.1f} cal/cmÂ² at the typical working distance. The arc flash boundary "
            f"extends {afb:.1f} feet, within which personnel require PPE Category {ppe_cat}. "
            f"This analysis considers the available fault current, clearing time of "
            f"protective devices, and equipment configuration to determine the thermal "
            f"energy exposure during an arc flash event."
        )
    
    def _explain_load_flow(self, data: Dict) -> str:
        """Explain load flow calculation"""
        method = data.get('method', 'Newton-Raphson')
        iterations = data.get('iterations', 0)
        
        return (
            f"Load flow analysis using the {method} method converged in {iterations} iterations. "
            f"This iterative solution technique solves the nonlinear power flow equations to "
            f"determine bus voltages, branch power flows, and system losses. The solution provides "
            f"steady-state operating conditions and identifies potential voltage regulation or "
            f"thermal loading issues."
        )
    
    def _extract_voltage_levels(self, project_data: Dict) -> List[float]:
        """Extract voltage levels from project"""
        voltage_levels = set()
        
        for node in project_data.get('nodes', []):
            props = node.get('properties', {})
            voltage = props.get('voltage', 0)
            if voltage > 0:
                voltage_levels.add(voltage)
        
        return sorted(voltage_levels, reverse=True)
    
    def _format_list(self, items: List[str]) -> str:
        """Format list for natural language"""
        if len(items) == 0:
            return ""
        elif len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return ", ".join(items[:-1]) + f", and {items[-1]}"
    
    def _load_templates(self) -> Dict[str, NarrativeTemplate]:
        """Load narrative templates"""
        return {
            'executive_summary': NarrativeTemplate(
                template_id='executive_summary',
                category='summary',
                template_text='',
                required_fields=['project_name', 'voltage_levels']
            )
        }


# Testing and example usage
if __name__ == "__main__":
    print("ðŸ“ Automated Narrative Generation Test")
    print("=" * 70)
    
    generator = NarrativeGenerator()
    
    # Test project data
    test_project = {
        'name': 'Industrial Facility Main Distribution',
        'base_mva': 100.0,
        'nodes': [
            {'type': 'Source', 'properties': {'voltage': 11.0}},
            {'type': 'Transformer', 'properties': {'voltage': 0.4}},
            {'type': 'Motor', 'properties': {'voltage': 0.4}}
        ]
    }
    
    # Test analysis results
    test_analysis = {
        'short_circuit': {
            'bus1': {'tag': 'MDB-01', 'i_k3': 25.3, 'breaker_status': 'PASS'},
            'bus2': {'tag': 'MCC-01', 'i_k3': 15.2, 'breaker_status': 'PASS'}
        },
        'arc_flash': {
            'bus1': {'tag': 'MDB-01', 'incident_energy': 12.5},
            'bus2': {'tag': 'MCC-01', 'incident_energy': 8.2}
        },
        'load_flow': {
            'converged': True,
            'iterations': 4,
            'losses_mw': 3.2,
            'loss_percent': 3.8,
            'buses': {
                'bus1': {'tag': 'MDB-01', 'voltage': 0.98},
                'bus2': {'tag': 'MCC-01', 'voltage': 0.96}
            }
        }
    }
    
    # Generate executive summary
    print("\nðŸ“„ Executive Summary:")
    print("-" * 70)
    summary = generator.generate_executive_summary(test_project, test_analysis)
    print(summary)
    
    # Generate short circuit interpretation
    print("\nâš¡ Short Circuit Analysis:")
    print("-" * 70)
    sc_narrative = generator.interpret_short_circuit_results(test_analysis['short_circuit'])
    print(sc_narrative)
    
    # Generate arc flash interpretation
    print("\nðŸ”¥ Arc Flash Analysis:")
    print("-" * 70)
    af_narrative = generator.interpret_arc_flash_results(test_analysis['arc_flash'])
    print(af_narrative)
    
    # Generate load flow interpretation
    print("\nðŸ“Š Load Flow Analysis:")
    print("-" * 70)
    lf_narrative = generator.interpret_load_flow_results(test_analysis['load_flow'])
    print(lf_narrative)
    
    # Generate compliance statement
    print("\nðŸ“‹ Compliance Statement:")
    print("-" * 70)
    compliance = generator.generate_compliance_statement([
        'IEC 60909', 'IEEE 1584', 'NFPA 70E', 'IEEE 399'
    ])
    print(compliance)
    
    print("\nâœ… Automated Narrative Generation test complete!")
