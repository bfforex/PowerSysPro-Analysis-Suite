"""
PwrSysPro Analysis Suite - Per-Unit System (Phase 3)
Converts all impedances to a common base for network calculations.

The per-unit system simplifies power system calculations by normalizing
all quantities to dimensionless values based on chosen base values.

Base Values:
- S_base (MVA): Base apparent power (typically 100 MVA)
- V_base (kV): Base voltage at each voltage level
- Z_base (Î©): Base impedance = V_baseÂ² / S_base

Standards Reference:
- IEC 60909: Short-circuit current calculation
- IEEE Std 399: Power system analysis
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class PerUnitBase:
    """
    Base values for per-unit system at a specific voltage level.
    """
    voltage_kv: float           # Base voltage in kV
    power_mva: float           # Base power in MVA
    
    @property
    def impedance_ohms(self) -> float:
        """Base impedance in ohms: Z_base = V_baseÂ² / S_base"""
        return (self.voltage_kv ** 2 * 1000) / self.power_mva
    
    @property
    def current_amps(self) -> float:
        """Base current in amps: I_base = S_base / (âˆš3 Ã— V_base)"""
        return (self.power_mva * 1000) / (math.sqrt(3) * self.voltage_kv)
    
    def __repr__(self):
        return f"PerUnitBase({self.voltage_kv}kV, {self.power_mva}MVA, Z={self.impedance_ohms:.4f}Î©)"


class PerUnitSystem:
    """
    Manages per-unit conversions for multi-voltage level systems.
    """
    
    def __init__(self, base_mva: float = 100.0):
        """
        Initialize per-unit system.
        
        Args:
            base_mva: Base MVA for entire system (typically 100 MVA)
        """
        self.base_mva = base_mva
        self.voltage_bases: Dict[float, PerUnitBase] = {}
    
    def add_voltage_level(self, voltage_kv: float) -> PerUnitBase:
        """
        Add a voltage level to the system.
        
        Args:
            voltage_kv: Voltage level in kV
        
        Returns:
            PerUnitBase for this voltage level
        """
        if voltage_kv not in self.voltage_bases:
            self.voltage_bases[voltage_kv] = PerUnitBase(voltage_kv, self.base_mva)
        return self.voltage_bases[voltage_kv]
    
    def get_base(self, voltage_kv: float) -> PerUnitBase:
        """Get base values for a voltage level."""
        if voltage_kv not in self.voltage_bases:
            return self.add_voltage_level(voltage_kv)
        return self.voltage_bases[voltage_kv]
    
    def impedance_to_pu(self, impedance_ohms: complex, voltage_kv: float) -> complex:
        """
        Convert impedance from ohms to per-unit.
        
        Args:
            impedance_ohms: Impedance in ohms (R + jX)
            voltage_kv: Voltage level in kV
        
        Returns:
            Impedance in per-unit
        """
        base = self.get_base(voltage_kv)
        return impedance_ohms / base.impedance_ohms
    
    def impedance_to_ohms(self, impedance_pu: complex, voltage_kv: float) -> complex:
        """
        Convert impedance from per-unit to ohms.
        
        Args:
            impedance_pu: Impedance in per-unit
            voltage_kv: Voltage level in kV
        
        Returns:
            Impedance in ohms
        """
        base = self.get_base(voltage_kv)
        return impedance_pu * base.impedance_ohms
    
    def current_to_pu(self, current_amps: float, voltage_kv: float) -> float:
        """Convert current from amps to per-unit."""
        base = self.get_base(voltage_kv)
        return current_amps / base.current_amps
    
    def current_to_amps(self, current_pu: float, voltage_kv: float) -> float:
        """Convert current from per-unit to amps."""
        base = self.get_base(voltage_kv)
        return current_pu * base.current_amps
    
    def voltage_to_pu(self, voltage_kv: float, base_voltage_kv: float) -> float:
        """Convert voltage to per-unit."""
        return voltage_kv / base_voltage_kv
    
    def voltage_to_kv(self, voltage_pu: float, base_voltage_kv: float) -> float:
        """Convert voltage from per-unit to kV."""
        return voltage_pu * base_voltage_kv
    
    def power_to_pu(self, power_mva: float) -> float:
        """Convert power from MVA to per-unit."""
        return power_mva / self.base_mva
    
    def power_to_mva(self, power_pu: float) -> float:
        """Convert power from per-unit to MVA."""
        return power_pu * self.base_mva


def convert_cable_impedance_to_pu(
    resistance_per_km: float,
    reactance_per_km: float,
    length_km: float,
    voltage_kv: float,
    base_mva: float = 100.0
) -> complex:
    """
    Convert cable impedance to per-unit.
    
    Args:
        resistance_per_km: Cable resistance in Î©/km
        reactance_per_km: Cable reactance in Î©/km
        length_km: Cable length in km
        voltage_kv: Operating voltage in kV
        base_mva: Base MVA
    
    Returns:
        Cable impedance in per-unit
    """
    # Total impedance in ohms
    z_ohms = complex(
        resistance_per_km * length_km,
        reactance_per_km * length_km
    )
    
    # Convert to per-unit
    pu_system = PerUnitSystem(base_mva)
    return pu_system.impedance_to_pu(z_ohms, voltage_kv)


def convert_transformer_impedance_to_pu(
    z_percent: float,
    transformer_mva: float,
    voltage_primary_kv: float,
    voltage_secondary_kv: float,
    base_mva: float = 100.0
) -> Tuple[complex, complex]:
    """
    Convert transformer impedance to per-unit on system base.
    
    Transformer impedance is typically given as Z% at its own MVA rating.
    This converts it to the system base MVA.
    
    Args:
        z_percent: Transformer impedance in %
        transformer_mva: Transformer rating in MVA
        voltage_primary_kv: Primary voltage in kV
        voltage_secondary_kv: Secondary voltage in kV
        base_mva: System base MVA
    
    Returns:
        Tuple of (Z_pu_primary, Z_pu_secondary)
    """
    # Convert Z% to per-unit on transformer base
    z_pu_transformer_base = z_percent / 100.0
    
    # Convert to system base
    # Z_pu_system = Z_pu_transformer Ã— (S_base / S_transformer)
    z_pu_system_base = z_pu_transformer_base * (base_mva / transformer_mva)
    
    # For transformers, assume X/R ratio of 10 (typical for distribution)
    r_pu = z_pu_system_base / math.sqrt(1 + 10**2)
    x_pu = z_pu_system_base * (10 / math.sqrt(1 + 10**2))
    
    z_primary = complex(r_pu, x_pu)
    z_secondary = complex(r_pu, x_pu)
    
    return z_primary, z_secondary


def convert_motor_impedance_to_pu(
    motor_kw: float,
    voltage_kv: float,
    power_factor: float = 0.85,
    efficiency: float = 0.95,
    x_d_prime_prime: float = 0.15,  # Subtransient reactance
    base_mva: float = 100.0
) -> complex:
    """
    Convert motor impedance to per-unit for fault contribution.
    
    Motors contribute to fault currents during the first few cycles.
    
    Args:
        motor_kw: Motor rated power in kW
        voltage_kv: Operating voltage in kV
        power_factor: Motor power factor
        efficiency: Motor efficiency
        x_d_prime_prime: Subtransient reactance (typical: 0.15-0.20 pu)
        base_mva: System base MVA
    
    Returns:
        Motor impedance in per-unit
    """
    # Motor MVA rating
    motor_mva = (motor_kw / 1000.0) / (power_factor * efficiency)
    
    # Convert to system base
    # For motors, X'' is typically 0.15-0.20 pu on motor base
    z_pu_motor_base = complex(0.01, x_d_prime_prime)  # R is small
    
    # Convert to system base
    z_pu_system = z_pu_motor_base * (base_mva / motor_mva)
    
    return z_pu_system


def build_admittance_matrix(
    nodes: List[str],
    impedances: Dict[Tuple[str, str], complex]
) -> np.ndarray:
    """
    Build the nodal admittance matrix (Y-bus) from branch impedances.
    
    The Y-bus is fundamental for power system analysis:
    - Load flow studies
    - Short circuit analysis
    - Stability studies
    
    Args:
        nodes: List of node IDs
        impedances: Dictionary mapping (from_node, to_node) to impedance in pu
    
    Returns:
        Y-bus matrix (complex numpy array)
    """
    n = len(nodes)
    node_index = {node: i for i, node in enumerate(nodes)}
    
    # Initialize Y-bus
    Y_bus = np.zeros((n, n), dtype=complex)
    
    # Fill Y-bus
    for (from_node, to_node), z in impedances.items():
        if z == 0:
            continue  # Avoid division by zero
        
        # Admittance = 1 / Impedance
        y = 1.0 / z
        
        i = node_index[from_node]
        j = node_index[to_node]
        
        # Off-diagonal elements (negative admittance)
        Y_bus[i, j] -= y
        Y_bus[j, i] -= y
        
        # Diagonal elements (sum of all connected admittances)
        Y_bus[i, i] += y
        Y_bus[j, j] += y
    
    return Y_bus


def calculate_z_matrix(Y_bus: np.ndarray) -> np.ndarray:
    """
    Calculate the bus impedance matrix (Z-bus) from Y-bus.
    
    Z-bus = inv(Y-bus)
    
    Used for:
    - Short circuit calculations
    - Fault analysis
    - Voltage drop calculations
    
    Args:
        Y_bus: Nodal admittance matrix
    
    Returns:
        Z-bus matrix
    """
    try:
        Z_bus = np.linalg.inv(Y_bus)
        return Z_bus
    except np.linalg.LinAlgError:
        print("Warning: Y-bus is singular, cannot invert")
        return None


# Example usage and validation
if __name__ == "__main__":
    print("âš¡ Per-Unit System Test")
    print("=" * 70)
    
    # Create per-unit system
    pu_system = PerUnitSystem(base_mva=100.0)
    
    # Add voltage levels
    print("\nðŸ“Š Voltage Levels:")
    print("-" * 70)
    for voltage in [11.0, 0.4]:
        base = pu_system.add_voltage_level(voltage)
        print(f"{voltage}kV: Z_base = {base.impedance_ohms:.4f}Î©, "
              f"I_base = {base.current_amps:.2f}A")
    
    # Test cable impedance conversion
    print("\nðŸ”Œ Cable Impedance Conversion:")
    print("-" * 70)
    z_cable_pu = convert_cable_impedance_to_pu(
        resistance_per_km=0.161,  # NYY 4x120
        reactance_per_km=0.086,
        length_km=0.050,  # 50 meters
        voltage_kv=0.4,
        base_mva=100.0
    )
    print(f"Cable (50m, NYY 4x120):")
    print(f"  R+jX = {z_cable_pu.real:.6f} + j{z_cable_pu.imag:.6f} pu")
    print(f"  |Z| = {abs(z_cable_pu):.6f} pu")
    
    # Test transformer impedance conversion
    print("\nðŸ”„ Transformer Impedance Conversion:")
    print("-" * 70)
    z_pri, z_sec = convert_transformer_impedance_to_pu(
        z_percent=6.0,
        transformer_mva=1.0,
        voltage_primary_kv=11.0,
        voltage_secondary_kv=0.4,
        base_mva=100.0
    )
    print(f"Transformer (1MVA, 6% Z):")
    print(f"  Primary: {z_pri.real:.6f} + j{z_pri.imag:.6f} pu")
    print(f"  Secondary: {z_sec.real:.6f} + j{z_sec.imag:.6f} pu")
    
    # Test motor impedance conversion
    print("\nðŸ”§ Motor Impedance Conversion:")
    print("-" * 70)
    z_motor = convert_motor_impedance_to_pu(
        motor_kw=75.0,
        voltage_kv=0.4,
        power_factor=0.85,
        efficiency=0.95,
        base_mva=100.0
    )
    print(f"Motor (75kW, 0.4kV):")
    print(f"  Z = {z_motor.real:.6f} + j{z_motor.imag:.6f} pu")
    
    # Test Y-bus construction
    print("\nâš¡ Y-bus Matrix Construction:")
    print("-" * 70)
    nodes = ['1', '2', '3']
    impedances = {
        ('1', '2'): 0.01 + 0.05j,
        ('2', '3'): 0.02 + 0.06j
    }
    
    Y_bus = build_admittance_matrix(nodes, impedances)
    print("Y-bus (3x3):")
    print(np.array2string(Y_bus, precision=4, suppress_small=True))
    
    # Calculate Z-bus
    print("\nðŸ“ Z-bus Matrix Calculation:")
    print("-" * 70)
    Z_bus = calculate_z_matrix(Y_bus)
    if Z_bus is not None:
        print("Z-bus (3x3):")
        print(np.array2string(Z_bus, precision=4, suppress_small=True))
    
    print("\nâœ… Per-unit system test complete!")
