"""
PwrSysPro Analysis Suite - Calculation Engine
Core electrical calculations following IEC and ANSI standards.

Standards Reference:
- Voltage Drop: IEC 60364-5-52
- Short Circuit: IEC 60909, ANSI/IEEE C37
- Cable Derating: IEC 60364-5-52, Table 52-3 through 52-17
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CableParameters:
    """Cable electrical and physical parameters."""
    resistance_per_km: float  # Ohms/km
    reactance_per_km: float   # Ohms/km
    length_km: float          # km
    ampacity_base: float      # Amps (base rating)
    
    # Derating factors
    ambient_temp_factor: float = 1.0
    grouping_factor: float = 1.0
    installation_factor: float = 1.0
    
    @property
    def total_resistance(self) -> float:
        """Total resistance (R) in Ohms."""
        return self.resistance_per_km * self.length_km
    
    @property
    def total_reactance(self) -> float:
        """Total reactance (X) in Ohms."""
        return self.reactance_per_km * self.length_km
    
    @property
    def total_impedance(self) -> float:
        """Total impedance |Z| in Ohms."""
        return math.sqrt(self.total_resistance**2 + self.total_reactance**2)
    
    @property
    def effective_ampacity(self) -> float:
        """
        Effective ampacity after applying derating factors.
        Per IEC 60364-5-52, I_z = I_base Ã— k1 Ã— k2 Ã— k3
        """
        return (self.ampacity_base * 
                self.ambient_temp_factor * 
                self.grouping_factor * 
                self.installation_factor)


@dataclass
class LoadParameters:
    """Load current and power factor parameters."""
    current_amps: float       # Load current in Amps
    power_factor: float       # cos(Ï†), range [0, 1]
    voltage_nominal: float    # Nominal voltage in Volts
    
    @property
    def power_factor_angle(self) -> float:
        """Power factor angle Ï† in radians."""
        return math.acos(self.power_factor)
    
    @property
    def active_power_kw(self) -> float:
        """Active power P in kW (for 3-phase)."""
        return math.sqrt(3) * self.voltage_nominal * self.current_amps * self.power_factor / 1000
    
    @property
    def reactive_power_kvar(self) -> float:
        """Reactive power Q in kVAR (for 3-phase)."""
        sin_phi = math.sqrt(1 - self.power_factor**2)
        return math.sqrt(3) * self.voltage_nominal * self.current_amps * sin_phi / 1000


def calculate_voltage_drop_three_phase(
    cable: CableParameters,
    load: LoadParameters
) -> Dict[str, float]:
    """
    Calculate voltage drop for a three-phase AC system.
    
    Formula (IEC 60364-5-52):
        Î”V = âˆš3 Ã— I Ã— (R Ã— cos(Ï†) + X Ã— sin(Ï†)) Ã— L
    
    Where:
        I = Load current (A)
        R = Cable resistance per unit length (Î©/km)
        X = Cable reactance per unit length (Î©/km)
        L = Cable length (km)
        Ï† = Power factor angle
    
    Args:
        cable: Cable parameters including R, X, and length
        load: Load parameters including current and power factor
    
    Returns:
        Dictionary containing:
            - voltage_drop_volts: Voltage drop in Volts
            - voltage_drop_percent: Voltage drop as percentage
            - voltage_at_load: Voltage at load end in Volts
            - power_loss_watts: Power loss in the cable (IÂ²R loss)
    """
    # Calculate sin(Ï†) from cos(Ï†)
    cos_phi = load.power_factor
    sin_phi = math.sqrt(1 - cos_phi**2)
    
    # Voltage drop formula
    voltage_drop_volts = (math.sqrt(3) * 
                          load.current_amps * 
                          (cable.total_resistance * cos_phi + cable.total_reactance * sin_phi))
    
    # Percentage drop
    voltage_drop_percent = (voltage_drop_volts / load.voltage_nominal) * 100
    
    # Voltage at load
    voltage_at_load = load.voltage_nominal - voltage_drop_volts
    
    # Power loss (3-phase): P_loss = 3 Ã— IÂ² Ã— R
    power_loss_watts = 3 * (load.current_amps**2) * cable.total_resistance
    
    # Check against IEC limit (typically 5% for final circuits, 3% for distribution)
    within_limit_5_percent = voltage_drop_percent <= 5.0
    within_limit_3_percent = voltage_drop_percent <= 3.0
    
    return {
        "voltage_drop_volts": round(voltage_drop_volts, 2),
        "voltage_drop_percent": round(voltage_drop_percent, 2),
        "voltage_at_load": round(voltage_at_load, 2),
        "power_loss_watts": round(power_loss_watts, 2),
        "power_loss_kw": round(power_loss_watts / 1000, 3),
        "within_5_percent_limit": within_limit_5_percent,
        "within_3_percent_limit": within_limit_3_percent,
        "status": "PASS" if within_limit_5_percent else "FAIL"
    }


def calculate_voltage_drop_single_phase(
    cable: CableParameters,
    load: LoadParameters
) -> Dict[str, float]:
    """
    Calculate voltage drop for a single-phase AC system.
    
    Formula:
        Î”V = 2 Ã— I Ã— (R Ã— cos(Ï†) + X Ã— sin(Ï†)) Ã— L
    
    The factor of 2 accounts for both go and return conductors.
    
    Args:
        cable: Cable parameters
        load: Load parameters
    
    Returns:
        Voltage drop results dictionary
    """
    cos_phi = load.power_factor
    sin_phi = math.sqrt(1 - cos_phi**2)
    
    voltage_drop_volts = (2 * 
                          load.current_amps * 
                          (cable.total_resistance * cos_phi + cable.total_reactance * sin_phi))
    
    voltage_drop_percent = (voltage_drop_volts / load.voltage_nominal) * 100
    voltage_at_load = load.voltage_nominal - voltage_drop_volts
    
    # Power loss (single-phase): P_loss = 2 Ã— IÂ² Ã— R
    power_loss_watts = 2 * (load.current_amps**2) * cable.total_resistance
    
    within_limit_5_percent = voltage_drop_percent <= 5.0
    within_limit_3_percent = voltage_drop_percent <= 3.0
    
    return {
        "voltage_drop_volts": round(voltage_drop_volts, 2),
        "voltage_drop_percent": round(voltage_drop_percent, 2),
        "voltage_at_load": round(voltage_at_load, 2),
        "power_loss_watts": round(power_loss_watts, 2),
        "power_loss_kw": round(power_loss_watts / 1000, 3),
        "within_5_percent_limit": within_limit_5_percent,
        "within_3_percent_limit": within_limit_3_percent,
        "status": "PASS" if within_limit_5_percent else "FAIL"
    }


def calculate_cable_derating_factor(
    ambient_temp_celsius: float = 30.0,
    reference_temp_celsius: float = 30.0,
    number_of_cables_grouped: int = 1,
    installation_method: str = "E"  # Tray, Conduit, Underground
) -> Dict[str, float]:
    """
    Calculate cable derating factors per IEC 60364-5-52.
    
    Args:
        ambient_temp_celsius: Actual ambient temperature
        reference_temp_celsius: Reference temperature for base rating (typically 30Â°C)
        number_of_cables_grouped: Number of cables in the same group
        installation_method: Installation method code (E, F, etc.)
    
    Returns:
        Dictionary with individual derating factors
    """
    # Temperature derating factor (IEC 60364-5-52, Table 52-14)
    # Linear approximation: k = 1 - 0.02 Ã— (T_ambient - T_reference)
    temp_delta = ambient_temp_celsius - reference_temp_celsius
    temp_factor = max(0.5, 1.0 - 0.02 * temp_delta)  # Min 0.5 for safety
    
    # Grouping factor (IEC 60364-5-52, Table 52-19)
    grouping_factors = {
        1: 1.00,
        2: 0.80,
        3: 0.70,
        4: 0.65,
        5: 0.60,
        6: 0.57
    }
    grouping_factor = grouping_factors.get(
        min(number_of_cables_grouped, 6), 
        0.50  # Conservative for >6 cables
    )
    
    # Installation method factor (simplified)
    installation_factors = {
        "E": 1.00,  # Cables on perforated tray (reference)
        "F": 0.95,  # Cables on ladder/solid tray
        "C": 0.90,  # Cables in conduit/trunking
        "D": 0.85   # Cables directly buried underground
    }
    installation_factor = installation_factors.get(installation_method, 0.90)
    
    # Overall derating factor
    overall_factor = temp_factor * grouping_factor * installation_factor
    
    return {
        "temperature_factor": round(temp_factor, 3),
        "grouping_factor": grouping_factor,
        "installation_factor": installation_factor,
        "overall_factor": round(overall_factor, 3)
    }


def check_cable_sizing(
    load_current: float,
    cable_ampacity_base: float,
    derating_factors: Dict[str, float]
) -> Dict[str, any]:
    """
    Check if cable is properly sized for the load.
    
    Per IEC 60364-5-52:
        I_z â‰¥ I_b
    Where:
        I_z = Effective ampacity after derating
        I_b = Design current (load current)
    
    Args:
        load_current: Design load current (A)
        cable_ampacity_base: Base cable ampacity (A)
        derating_factors: Dictionary of derating factors
    
    Returns:
        Sizing check results
    """
    effective_ampacity = cable_ampacity_base * derating_factors["overall_factor"]
    utilization_percent = (load_current / effective_ampacity) * 100
    
    is_adequate = load_current <= effective_ampacity
    margin_amps = effective_ampacity - load_current
    margin_percent = (margin_amps / effective_ampacity) * 100
    
    return {
        "load_current": round(load_current, 1),
        "cable_ampacity_base": round(cable_ampacity_base, 1),
        "cable_ampacity_effective": round(effective_ampacity, 1),
        "utilization_percent": round(utilization_percent, 1),
        "margin_amps": round(margin_amps, 1),
        "margin_percent": round(margin_percent, 1),
        "is_adequate": is_adequate,
        "status": "PASS" if is_adequate else "FAIL - UNDERSIZED"
    }


def calculate_short_circuit_simplified(
    source_voltage_kv: float,
    source_fault_mva: float,
    transformer_mva: float,
    transformer_z_percent: float,
    cable_impedance_ohms: Optional[float] = None
) -> Dict[str, float]:
    """
    Simplified 3-phase short circuit calculation (IEC 60909).
    Full implementation would be in Phase 3.
    
    Args:
        source_voltage_kv: Source voltage (kV)
        source_fault_mva: Available fault MVA at source
        transformer_mva: Transformer rating (MVA)
        transformer_z_percent: Transformer impedance (%)
        cable_impedance_ohms: Optional cable impedance
    
    Returns:
        Short circuit current results
    """
    # Source impedance
    Z_source = (source_voltage_kv**2 * 1000) / source_fault_mva  # Ohms
    
    # Transformer impedance (referred to secondary)
    V_secondary_kv = 0.4  # Assume 400V secondary
    Z_transformer = (transformer_z_percent / 100) * (V_secondary_kv**2 * 1000) / transformer_mva
    
    # Total impedance
    Z_total = Z_source + Z_transformer
    if cable_impedance_ohms:
        Z_total += cable_impedance_ohms
    
    # Short circuit current (3-phase)
    I_sc_ka = (V_secondary_kv * 1000) / (math.sqrt(3) * Z_total * 1000)
    
    return {
        "fault_current_ka": round(I_sc_ka, 2),
        "source_impedance_ohms": round(Z_source, 4),
        "transformer_impedance_ohms": round(Z_transformer, 4),
        "total_impedance_ohms": round(Z_total, 4),
        "calculation_method": "IEC 60909 (Simplified)"
    }


# Example usage
if __name__ == "__main__":
    print("âš¡ PwrSysPro Calculation Engine Test")
    print("=" * 70)
    
    # Test Case: 400V feeder to a motor
    cable = CableParameters(
        resistance_per_km=0.161,  # NYY 4x120 cable
        reactance_per_km=0.086,
        length_km=0.050,  # 50 meters
        ampacity_base=285,
        ambient_temp_factor=0.91,  # 40Â°C ambient
        grouping_factor=0.80,  # 2 cables grouped
        installation_factor=1.0
    )
    
    load = LoadParameters(
        current_amps=200,
        power_factor=0.85,
        voltage_nominal=400
    )
    
    print("\nðŸ“Š Voltage Drop Calculation (3-Phase)")
    print("-" * 70)
    results = calculate_voltage_drop_three_phase(cable, load)
    for key, value in results.items():
        print(f"   {key:25}: {value}")
    
    print("\nðŸ“Š Cable Derating Factors")
    print("-" * 70)
    derating = calculate_cable_derating_factor(
        ambient_temp_celsius=40,
        number_of_cables_grouped=2,
        installation_method="E"
    )
    for key, value in derating.items():
        print(f"   {key:25}: {value}")
    
    print("\nðŸ“Š Cable Sizing Check")
    print("-" * 70)
    sizing = check_cable_sizing(200, 285, derating)
    for key, value in sizing.items():
        print(f"   {key:25}: {value}")
    
    print("\nâœ… Calculation engine test complete!")
