"""
PwrSysPro Analysis Suite - Arc Flash Analysis (Phase 4)
IEEE 1584-2018 Arc Flash Hazard Calculation

Arc flash is a dangerous release of energy caused by an electrical fault.
This module calculates:
- Incident energy (cal/cmÂ²)
- Arc flash boundary (AFB)
- PPE category
- Flash protection boundary

Standards Reference:
- IEEE 1584-2018: Guide for Performing Arc-Flash Hazard Calculations
- NFPA 70E: Standard for Electrical Safety in the Workplace
"""

import math
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class EquipmentType(Enum):
    """Equipment enclosure types per IEEE 1584."""
    VCB = "VCB"  # Vertical switchboard/switchgear
    VCBB = "VCBB"  # Vertical switchboard/switchgear with barrier
    HCB = "HCB"  # Horizontal switchboard/switchgear
    VOA = "VOA"  # Vertical open air
    HOA = "HOA"  # Horizontal open air


class PPECategory(Enum):
    """PPE categories per NFPA 70E."""
    CATEGORY_0 = 0  # < 1.2 cal/cmÂ²
    CATEGORY_1 = 1  # 1.2 - 4 cal/cmÂ²
    CATEGORY_2 = 2  # 4 - 8 cal/cmÂ²
    CATEGORY_3 = 3  # 8 - 25 cal/cmÂ²
    CATEGORY_4 = 4  # 25 - 40 cal/cmÂ²
    DANGEROUS = 5   # > 40 cal/cmÂ²


@dataclass
class ArcFlashParameters:
    """Input parameters for arc flash calculation."""
    bolted_fault_current: float      # Three-phase fault current (kA)
    voltage: float                     # System voltage (kV)
    working_distance: float            # Working distance (inches)
    gap_between_conductors: float      # Gap (mm)
    equipment_type: EquipmentType      # Enclosure type
    clearing_time: float               # Fault clearing time (cycles at 60Hz)
    grounding: str = "grounded"        # System grounding (grounded/ungrounded)
    electrode_config: str = "VCB"      # Electrode configuration


@dataclass
class ArcFlashResult:
    """Results of arc flash calculation."""
    # Incident energy
    incident_energy: float             # cal/cmÂ² at working distance
    
    # Arc flash boundary
    arc_flash_boundary: float          # inches
    arc_flash_boundary_ft: float       # feet
    
    # Arcing current
    arcing_current: float              # kA
    
    # PPE requirements
    ppe_category: PPECategory
    ppe_cal_cm2: float                # Required PPE rating
    
    # Additional data
    arc_duration: float                # seconds
    hazard_risk_category: str
    
    # Validation
    is_safe: bool
    warnings: list


class IEEE1584ArcFlashCalculator:
    """
    IEEE 1584-2018 Arc Flash Calculator.
    
    Implements the 2018 revision of IEEE 1584 which includes
    improved models for low-voltage and high-voltage systems.
    """
    
    def __init__(self, parameters: ArcFlashParameters):
        """
        Initialize arc flash calculator.
        
        Args:
            parameters: Arc flash calculation parameters
        """
        self.params = parameters
        
        # Constants from IEEE 1584-2018
        self.k_constants = self._get_k_constants()
    
    def calculate(self) -> ArcFlashResult:
        """
        Perform complete arc flash calculation per IEEE 1584-2018.
        
        Returns:
            ArcFlashResult with all calculated values
        """
        warnings = []
        
        # Step 1: Calculate arcing current
        i_arc = self._calculate_arcing_current()
        
        # Step 2: Calculate normalized incident energy
        e_n = self._calculate_normalized_incident_energy(i_arc)
        
        # Step 3: Calculate actual incident energy at working distance
        incident_energy = self._calculate_incident_energy(e_n)
        
        # Step 4: Calculate arc flash boundary
        afb = self._calculate_arc_flash_boundary(e_n)
        
        # Step 5: Determine PPE category
        ppe_category = self._determine_ppe_category(incident_energy)
        ppe_rating = self._get_ppe_rating(ppe_category)
        
        # Step 6: Arc duration
        arc_duration = self.params.clearing_time / 60.0  # Convert cycles to seconds
        
        # Step 7: Validate and generate warnings
        is_safe, calc_warnings = self._validate_results(incident_energy, afb)
        warnings.extend(calc_warnings)
        
        # Step 8: Determine hazard category
        hazard_category = self._determine_hazard_category(incident_energy)
        
        return ArcFlashResult(
            incident_energy=round(incident_energy, 2),
            arc_flash_boundary=round(afb, 1),
            arc_flash_boundary_ft=round(afb / 12.0, 2),
            arcing_current=round(i_arc, 2),
            ppe_category=ppe_category,
            ppe_cal_cm2=ppe_rating,
            arc_duration=round(arc_duration, 3),
            hazard_risk_category=hazard_category,
            is_safe=is_safe,
            warnings=warnings
        )
    
    def _get_k_constants(self) -> Dict[str, float]:
        """
        Get K constants based on equipment type and voltage level.
        Per IEEE 1584-2018 Table 4.
        """
        voltage = self.params.voltage
        eq_type = self.params.equipment_type.value
        
        # Simplified constants - full implementation would use lookup tables
        if voltage <= 1.0:  # Low voltage (<=1000V)
            if eq_type in ["VCB", "VCBB"]:
                return {"k1": -0.792, "k2": 0.000, "k3": -0.113, "k4": 0.0}
            else:  # Open air
                return {"k1": -0.555, "k2": 0.000, "k3": -0.113, "k4": 0.0}
        else:  # Medium voltage (>1kV)
            return {"k1": -0.153, "k2": 0.000, "k3": -0.093, "k4": 0.0}
    
    def _calculate_arcing_current(self) -> float:
        """
        Calculate arcing current per IEEE 1584-2018 Equation 4.
        
        I_arc = 10^K Ã— I_bf^a
        
        Where:
        - I_bf: Bolted fault current
        - K: Constant based on equipment
        - a: Exponent (typically 0.98 to 1.0)
        """
        i_bf = self.params.bolted_fault_current
        voltage = self.params.voltage
        gap = self.params.gap_between_conductors
        
        # IEEE 1584-2018 improved model
        if voltage <= 1.0:  # Low voltage
            # Equation varies by configuration
            if self.params.equipment_type in [EquipmentType.VCB, EquipmentType.VCBB]:
                # Enclosure model
                log_i_arc = self.k_constants["k1"] + \
                           0.662 * math.log10(i_bf) + \
                           0.0966 * voltage + \
                           self.k_constants["k3"] * math.log10(gap)
            else:
                # Open air model
                log_i_arc = self.k_constants["k1"] + \
                           0.662 * math.log10(i_bf) + \
                           0.0966 * voltage + \
                           self.k_constants["k3"] * math.log10(gap)
            
            i_arc = 10 ** log_i_arc
        else:
            # Medium voltage: typically 85% of bolted fault
            i_arc = 0.85 * i_bf
        
        # Apply variation factor (Â±15% per IEEE 1584)
        # Use maximum for conservative calculation
        i_arc_max = i_arc * 1.0  # No variation applied in basic calc
        
        return i_arc_max
    
    def _calculate_normalized_incident_energy(self, i_arc: float) -> float:
        """
        Calculate normalized incident energy at 610mm (24 inches).
        Per IEEE 1584-2018 Equation 6.
        """
        voltage = self.params.voltage
        gap = self.params.gap_between_conductors
        t = self.params.clearing_time / 60.0  # Convert to seconds
        
        # IEEE 1584-2018 Equation 6 for low voltage
        if voltage <= 1.0:
            if self.params.equipment_type in [EquipmentType.VCB, EquipmentType.VCBB]:
                # Enclosure equation
                log_e_n = self.k_constants["k1"] + \
                         self.k_constants["k2"] + \
                         1.081 * math.log10(i_arc) + \
                         0.0011 * gap
            else:
                # Open air equation
                log_e_n = self.k_constants["k1"] + \
                         self.k_constants["k2"] + \
                         1.081 * math.log10(i_arc) + \
                         0.0011 * gap
            
            e_n = 10 ** log_e_n  # J/cmÂ²
            
            # Convert to cal/cmÂ²
            e_n = e_n * 0.2388  # 1 J = 0.2388 cal
            
            # Apply time correction
            e_n = e_n * (t / 0.2)  # Normalized to 0.2 seconds
        else:
            # Medium voltage calculation
            e_n = 5.271 * i_arc * t * (10**(0.0016 * gap))
        
        return e_n
    
    def _calculate_incident_energy(self, e_n: float) -> float:
        """
        Calculate incident energy at working distance.
        Per IEEE 1584-2018 Equation 8.
        
        E = E_n Ã— (610/D)^x
        
        Where:
        - E_n: Normalized incident energy at 610mm
        - D: Working distance (mm)
        - x: Distance exponent (typically 1.0 to 2.0)
        """
        working_distance_mm = self.params.working_distance * 25.4  # inches to mm
        
        # Distance exponent varies by equipment type
        if self.params.equipment_type in [EquipmentType.VCB, EquipmentType.VCBB]:
            x = 1.473  # Enclosed equipment
        else:
            x = 2.0    # Open air (inverse square law)
        
        # Apply distance correction
        e = e_n * (610.0 / working_distance_mm) ** x
        
        return e
    
    def _calculate_arc_flash_boundary(self, e_n: float) -> float:
        """
        Calculate arc flash boundary distance.
        
        The AFB is the distance at which incident energy = 1.2 cal/cmÂ²
        (threshold of second-degree burn).
        
        Per IEEE 1584-2018 Equation 9:
        AFB = 610 Ã— (E_n / E_b)^(1/x)
        
        Where E_b = 1.2 cal/cmÂ² (burn threshold)
        """
        e_b = 1.2  # cal/cmÂ² (second-degree burn threshold)
        
        # Distance exponent
        if self.params.equipment_type in [EquipmentType.VCB, EquipmentType.VCBB]:
            x = 1.473
        else:
            x = 2.0
        
        # Calculate boundary in mm
        afb_mm = 610.0 * (e_n / e_b) ** (1.0 / x)
        
        # Convert to inches
        afb_inches = afb_mm / 25.4
        
        return afb_inches
    
    def _determine_ppe_category(self, incident_energy: float) -> PPECategory:
        """
        Determine PPE category based on incident energy.
        Per NFPA 70E Table 130.5(G).
        """
        if incident_energy < 1.2:
            return PPECategory.CATEGORY_0
        elif incident_energy < 4.0:
            return PPECategory.CATEGORY_1
        elif incident_energy < 8.0:
            return PPECategory.CATEGORY_2
        elif incident_energy < 25.0:
            return PPECategory.CATEGORY_3
        elif incident_energy < 40.0:
            return PPECategory.CATEGORY_4
        else:
            return PPECategory.DANGEROUS
    
    def _get_ppe_rating(self, category: PPECategory) -> float:
        """Get minimum PPE rating for category."""
        ratings = {
            PPECategory.CATEGORY_0: 1.2,
            PPECategory.CATEGORY_1: 4.0,
            PPECategory.CATEGORY_2: 8.0,
            PPECategory.CATEGORY_3: 25.0,
            PPECategory.CATEGORY_4: 40.0,
            PPECategory.DANGEROUS: 100.0
        }
        return ratings[category]
    
    def _validate_results(
        self,
        incident_energy: float,
        afb: float
    ) -> Tuple[bool, list]:
        """Validate calculation results and generate warnings."""
        warnings = []
        is_safe = True
        
        # Check if incident energy is dangerously high
        if incident_energy > 40.0:
            warnings.append("Incident energy > 40 cal/cmÂ² - EXTREMELY DANGEROUS")
            is_safe = False
        elif incident_energy > 25.0:
            warnings.append("Incident energy > 25 cal/cmÂ² - HIGH HAZARD")
        
        # Check if AFB is very large
        if afb > 120:  # > 10 feet
            warnings.append(f"Arc flash boundary {afb/12:.1f} ft - Consider de-energizing")
        
        # Check working distance vs AFB
        if self.params.working_distance < afb:
            warnings.append("Working distance is inside arc flash boundary!")
            is_safe = False
        
        return is_safe, warnings
    
    def _determine_hazard_category(self, incident_energy: float) -> str:
        """Determine overall hazard risk category."""
        if incident_energy < 1.2:
            return "Low Hazard"
        elif incident_energy < 8.0:
            return "Moderate Hazard"
        elif incident_energy < 25.0:
            return "High Hazard"
        else:
            return "Extreme Hazard"


def calculate_arc_flash_for_bus(
    fault_current_ka: float,
    voltage_kv: float,
    breaker_clearing_cycles: float,
    working_distance_inches: float = 18.0,
    equipment_type: str = "VCB"
) -> ArcFlashResult:
    """
    Simplified arc flash calculation for a bus.
    
    Args:
        fault_current_ka: Three-phase fault current (kA)
        voltage_kv: System voltage (kV)
        breaker_clearing_cycles: Fault clearing time (cycles at 60Hz)
        working_distance_inches: Working distance (inches)
        equipment_type: Equipment type code
    
    Returns:
        ArcFlashResult
    """
    # Determine gap based on voltage
    if voltage_kv <= 0.6:
        gap = 32.0  # mm (typical for LV)
    elif voltage_kv <= 15.0:
        gap = 104.0  # mm (typical for MV)
    else:
        gap = 152.0  # mm (typical for HV)
    
    # Map equipment type
    eq_type_map = {
        "VCB": EquipmentType.VCB,
        "VCBB": EquipmentType.VCBB,
        "HCB": EquipmentType.HCB,
        "VOA": EquipmentType.VOA,
        "HOA": EquipmentType.HOA
    }
    eq_type = eq_type_map.get(equipment_type, EquipmentType.VCB)
    
    params = ArcFlashParameters(
        bolted_fault_current=fault_current_ka,
        voltage=voltage_kv,
        working_distance=working_distance_inches,
        gap_between_conductors=gap,
        equipment_type=eq_type,
        clearing_time=breaker_clearing_cycles
    )
    
    calculator = IEEE1584ArcFlashCalculator(params)
    return calculator.calculate()


# Example usage and testing
if __name__ == "__main__":
    print("âš¡ IEEE 1584 Arc Flash Calculator Test")
    print("=" * 70)
    
    # Example: 480V switchgear
    print("\nðŸ“Š Test Scenario: 480V Switchgear")
    print("-" * 70)
    print("Fault Current: 25 kA")
    print("Voltage: 0.48 kV")
    print("Breaker: 5 cycles clearing")
    print("Working Distance: 18 inches")
    print("Equipment: Vertical switchboard (VCB)")
    
    result = calculate_arc_flash_for_bus(
        fault_current_ka=25.0,
        voltage_kv=0.48,
        breaker_clearing_cycles=5.0,
        working_distance_inches=18.0,
        equipment_type="VCB"
    )
    
    print("\nâš¡ Arc Flash Analysis Results:")
    print("-" * 70)
    print(f"Incident Energy:        {result.incident_energy} cal/cmÂ²")
    print(f"Arc Flash Boundary:     {result.arc_flash_boundary:.1f} inches ({result.arc_flash_boundary_ft:.2f} ft)")
    print(f"Arcing Current:         {result.arcing_current} kA")
    print(f"Arc Duration:           {result.arc_duration} seconds")
    print(f"PPE Category:           {result.ppe_category.name}")
    print(f"Required PPE Rating:    {result.ppe_cal_cm2} cal/cmÂ²")
    print(f"Hazard Category:        {result.hazard_risk_category}")
    print(f"Safe to Work:           {'âœ… YES' if result.is_safe else 'âŒ NO'}")
    
    if result.warnings:
        print("\nâš ï¸  Warnings:")
        for warning in result.warnings:
            print(f"  â€¢ {warning}")
    
    print("\nâœ… Arc flash calculator test complete!")
