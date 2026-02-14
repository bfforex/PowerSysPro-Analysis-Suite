"""
PwrSysPro Analysis Suite - Bus Tie Synchronization
Manages bus tie breaker operations and load transfer sequences.

Standards Reference:
- IEEE 1547: Interconnection and Interoperability of Distributed Energy Resources
- IEEE C37.113: Guide for Protective Relay Applications
- IEEE 242 (Buff Book): Protection and Coordination

Purpose:
- Check synchronization between buses
- Plan load transfer sequences
- Calculate load sharing
- Ensure safe parallel operation
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional
import numpy as np


class BusTieMode(Enum):
    """Bus tie breaker operating mode"""
    OPEN = "open"
    CLOSED = "closed"
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class TransferMode(Enum):
    """Load transfer mode"""
    OPEN_TRANSITION = "open"          # Break before make
    CLOSED_TRANSITION = "closed"      # Make before break
    SOFT_TRANSFER = "soft"            # Gradual load shift


@dataclass
class BusParameters:
    """Parameters for an electrical bus"""
    bus_id: str
    bus_tag: str
    voltage_kv: float
    frequency_hz: float
    phase_angle_deg: float
    load_mw: float
    load_mvar: float
    available_capacity_mw: float
    source_impedance: complex = 0.0 + 0.0j


@dataclass
class BusTieParameters:
    """Bus tie breaker parameters"""
    breaker_id: str
    breaker_tag: str
    bus_1_id: str
    bus_2_id: str
    rating_mva: float
    mode: BusTieMode
    close_time_ms: float = 50.0
    open_time_ms: float = 30.0
    current_position: str = "open"  # "open" or "closed"


@dataclass
class SynchronizationCheck:
    """Results of synchronization check"""
    synchronized: bool
    voltage_diff_percent: float
    frequency_diff_hz: float
    phase_diff_deg: float
    issues: List[str]
    can_parallel: bool


@dataclass
class TransferSequenceStep:
    """Single step in load transfer sequence"""
    step_number: int
    action: str
    time_ms: float
    description: str
    safety_checks: List[str]


class BusTieController:
    """
    Manages bus tie breaker operations and load transfer.
    
    Features:
    - Synchronization checking per IEEE 1547
    - Load transfer planning
    - Parallel bus operation
    - Load sharing calculations
    """
    
    # IEEE 1547 synchronization limits
    VOLTAGE_LIMIT_PERCENT = 5.0      # Â±5% voltage difference
    FREQUENCY_LIMIT_HZ = 0.3         # Â±0.3 Hz frequency difference
    PHASE_ANGLE_LIMIT_DEG = 20.0     # Â±20Â° phase angle difference
    
    def __init__(self):
        self.bus_ties: Dict[str, BusTieParameters] = {}
        self.buses: Dict[str, BusParameters] = {}
    
    def add_bus_tie(self, params: BusTieParameters):
        """Register a bus tie breaker"""
        self.bus_ties[params.breaker_id] = params
    
    def add_bus(self, params: BusParameters):
        """Register a bus"""
        self.buses[params.bus_id] = params
    
    def check_synchronization(
        self,
        bus_1_id: str,
        bus_2_id: str
    ) -> SynchronizationCheck:
        """
        Check if two buses are synchronized for parallel operation.
        
        Per IEEE 1547-2018:
        - Voltage: Within Â±5%
        - Frequency: Within Â±0.3 Hz
        - Phase angle: Within Â±20Â°
        
        Args:
            bus_1_id: First bus identifier
            bus_2_id: Second bus identifier
        
        Returns:
            SynchronizationCheck with results
        """
        if bus_1_id not in self.buses or bus_2_id not in self.buses:
            return SynchronizationCheck(
                synchronized=False,
                voltage_diff_percent=0.0,
                frequency_diff_hz=0.0,
                phase_diff_deg=0.0,
                issues=["Bus not found"],
                can_parallel=False
            )
        
        bus1 = self.buses[bus_1_id]
        bus2 = self.buses[bus_2_id]
        
        # Calculate differences
        voltage_diff = abs(bus1.voltage_kv - bus2.voltage_kv)
        voltage_diff_percent = (voltage_diff / bus1.voltage_kv) * 100
        
        frequency_diff = abs(bus1.frequency_hz - bus2.frequency_hz)
        
        phase_diff = abs(bus1.phase_angle_deg - bus2.phase_angle_deg)
        # Normalize to 0-180 range
        if phase_diff > 180:
            phase_diff = 360 - phase_diff
        
        # Check limits
        issues = []
        synchronized = True
        
        if voltage_diff_percent > self.VOLTAGE_LIMIT_PERCENT:
            issues.append(
                f"Voltage difference {voltage_diff_percent:.2f}% exceeds "
                f"{self.VOLTAGE_LIMIT_PERCENT}% limit"
            )
            synchronized = False
        
        if frequency_diff > self.FREQUENCY_LIMIT_HZ:
            issues.append(
                f"Frequency difference {frequency_diff:.3f} Hz exceeds "
                f"{self.FREQUENCY_LIMIT_HZ} Hz limit"
            )
            synchronized = False
        
        if phase_diff > self.PHASE_ANGLE_LIMIT_DEG:
            issues.append(
                f"Phase angle difference {phase_diff:.1f}Â° exceeds "
                f"{self.PHASE_ANGLE_LIMIT_DEG}Â° limit"
            )
            synchronized = False
        
        return SynchronizationCheck(
            synchronized=synchronized,
            voltage_diff_percent=voltage_diff_percent,
            frequency_diff_hz=frequency_diff,
            phase_diff_deg=phase_diff,
            issues=issues,
            can_parallel=synchronized
        )
    
    def plan_load_transfer(
        self,
        from_bus_id: str,
        to_bus_id: str,
        load_mw: float,
        transfer_mode: TransferMode = TransferMode.OPEN_TRANSITION
    ) -> Dict:
        """
        Plan load transfer between buses.
        
        Args:
            from_bus_id: Source bus
            to_bus_id: Target bus
            load_mw: Load to transfer in MW
            transfer_mode: Transfer method
        
        Returns:
            Transfer plan with sequence and validation
        """
        if from_bus_id not in self.buses or to_bus_id not in self.buses:
            return {
                'feasible': False,
                'reason': 'Bus not found'
            }
        
        from_bus = self.buses[from_bus_id]
        to_bus = self.buses[to_bus_id]
        
        # Check target bus capacity
        if to_bus.available_capacity_mw < load_mw:
            return {
                'feasible': False,
                'reason': (
                    f"Target bus {to_bus.bus_tag} has only "
                    f"{to_bus.available_capacity_mw:.1f} MW available, "
                    f"need {load_mw:.1f} MW"
                ),
                'available_capacity': to_bus.available_capacity_mw
            }
        
        # Check synchronization for closed transition
        sync_check = None
        if transfer_mode == TransferMode.CLOSED_TRANSITION:
            sync_check = self.check_synchronization(from_bus_id, to_bus_id)
            if not sync_check.synchronized:
                return {
                    'feasible': False,
                    'reason': 'Buses not synchronized for closed transition',
                    'synchronization': sync_check.__dict__,
                    'recommendation': 'Use open transition or synchronize buses first'
                }
        
        # Generate switching sequence
        if transfer_mode == TransferMode.OPEN_TRANSITION:
            sequence = self._plan_open_transition(from_bus, to_bus, load_mw)
        elif transfer_mode == TransferMode.CLOSED_TRANSITION:
            sequence = self._plan_closed_transition(from_bus, to_bus, load_mw)
        else:  # SOFT_TRANSFER
            sequence = self._plan_soft_transfer(from_bus, to_bus, load_mw)
        
        return {
            'feasible': True,
            'transfer_mode': transfer_mode.value,
            'load_mw': load_mw,
            'from_bus': from_bus.bus_tag,
            'to_bus': to_bus.bus_tag,
            'synchronization': sync_check.__dict__ if sync_check else None,
            'sequence': [step.__dict__ for step in sequence],
            'estimated_time_seconds': self._calculate_transfer_time(sequence),
            'safety_notes': self._generate_safety_notes(transfer_mode)
        }
    
    def _plan_open_transition(
        self,
        from_bus: BusParameters,
        to_bus: BusParameters,
        load_mw: float
    ) -> List[TransferSequenceStep]:
        """Break before make - momentary outage acceptable"""
        return [
            TransferSequenceStep(
                step_number=1,
                action=f"Open source breakers on {from_bus.bus_tag}",
                time_ms=0,
                description=f"De-energize {load_mw:.1f} MW load",
                safety_checks=["Verify zero current", "Check breaker status"]
            ),
            TransferSequenceStep(
                step_number=2,
                action="Wait for arc extinction and transients",
                time_ms=100,
                description="Safety delay for complete de-energization",
                safety_checks=["Confirm no voltage on load side"]
            ),
            TransferSequenceStep(
                step_number=3,
                action=f"Close breakers to {to_bus.bus_tag}",
                time_ms=150,
                description=f"Energize load from new source",
                safety_checks=["Verify voltage present", "Check phase sequence"]
            ),
            TransferSequenceStep(
                step_number=4,
                action="Verify stable operation",
                time_ms=200,
                description="Confirm load transfer successful",
                safety_checks=["Check voltage", "Check current", "No alarms"]
            )
        ]
    
    def _plan_closed_transition(
        self,
        from_bus: BusParameters,
        to_bus: BusParameters,
        load_mw: float
    ) -> List[TransferSequenceStep]:
        """Make before break - no interruption"""
        return [
            TransferSequenceStep(
                step_number=1,
                action="Verify synchronization",
                time_ms=0,
                description="Confirm buses are synchronized",
                safety_checks=["Voltage match", "Frequency match", "Phase match"]
            ),
            TransferSequenceStep(
                step_number=2,
                action="Close bus tie breaker",
                time_ms=50,
                description="Parallel both sources",
                safety_checks=["Monitor circulating current", "Check sync-check relay"]
            ),
            TransferSequenceStep(
                step_number=3,
                action="Verify load sharing",
                time_ms=100,
                description=f"Both sources sharing {load_mw:.1f} MW",
                safety_checks=["Check load distribution", "Monitor currents"]
            ),
            TransferSequenceStep(
                step_number=4,
                action=f"Open breakers to {from_bus.bus_tag}",
                time_ms=150,
                description="Transfer complete to new source",
                safety_checks=["Verify load stable", "Check breaker status"]
            ),
            TransferSequenceStep(
                step_number=5,
                action="Open bus tie breaker",
                time_ms=200,
                description="Isolate buses",
                safety_checks=["Confirm isolation", "No reverse power"]
            )
        ]
    
    def _plan_soft_transfer(
        self,
        from_bus: BusParameters,
        to_bus: BusParameters,
        load_mw: float
    ) -> List[TransferSequenceStep]:
        """Gradual load shift - multiple steps"""
        steps_count = 5
        load_per_step = load_mw / steps_count
        
        sequence = [
            TransferSequenceStep(
                step_number=0,
                action="Close bus tie breaker",
                time_ms=0,
                description="Parallel both sources",
                safety_checks=["Verify synchronization"]
            )
        ]
        
        for i in range(steps_count):
            transferred = load_per_step * (i + 1)
            remaining = load_mw - transferred
            
            sequence.append(
                TransferSequenceStep(
                    step_number=i + 1,
                    action=f"Shift {load_per_step:.1f} MW to {to_bus.bus_tag}",
                    time_ms=(i + 1) * 1000,
                    description=f"Transferred: {transferred:.1f} MW, Remaining: {remaining:.1f} MW",
                    safety_checks=["Monitor load sharing", "Check voltages"]
                )
            )
        
        sequence.append(
            TransferSequenceStep(
                step_number=steps_count + 1,
                action=f"Open breakers to {from_bus.bus_tag}",
                time_ms=(steps_count + 1) * 1000,
                description="Complete transfer",
                safety_checks=["Verify all load on new source"]
            )
        )
        
        return sequence
    
    def calculate_load_sharing(
        self,
        bus_1_id: str,
        bus_2_id: str
    ) -> Dict:
        """
        Calculate load sharing between parallel buses.
        
        Load sharing is proportional to available capacity
        (simplified - actual sharing depends on impedances)
        
        Args:
            bus_1_id: First bus
            bus_2_id: Second bus
        
        Returns:
            Load sharing calculation results
        """
        if bus_1_id not in self.buses or bus_2_id not in self.buses:
            return {'error': 'Bus not found'}
        
        bus1 = self.buses[bus_1_id]
        bus2 = self.buses[bus_2_id]
        
        # Total load and capacity
        total_load_mw = bus1.load_mw + bus2.load_mw
        total_capacity = bus1.available_capacity_mw + bus2.available_capacity_mw
        
        # Simplified load sharing (actual would use source impedances)
        if total_capacity > 0:
            share_bus1 = (bus1.available_capacity_mw / total_capacity) * total_load_mw
            share_bus2 = (bus2.available_capacity_mw / total_capacity) * total_load_mw
        else:
            share_bus1 = total_load_mw / 2
            share_bus2 = total_load_mw / 2
        
        return {
            'bus_1_tag': bus1.bus_tag,
            'bus_2_tag': bus2.bus_tag,
            'total_load_mw': total_load_mw,
            'bus_1_load_mw': share_bus1,
            'bus_2_load_mw': share_bus2,
            'bus_1_percent': (share_bus1 / total_load_mw * 100) if total_load_mw > 0 else 50,
            'bus_2_percent': (share_bus2 / total_load_mw * 100) if total_load_mw > 0 else 50,
            'bus_1_utilization': (share_bus1 / bus1.available_capacity_mw * 100) if bus1.available_capacity_mw > 0 else 0,
            'bus_2_utilization': (share_bus2 / bus2.available_capacity_mw * 100) if bus2.available_capacity_mw > 0 else 0
        }
    
    def _calculate_transfer_time(self, sequence: List[TransferSequenceStep]) -> float:
        """Calculate total transfer time in seconds"""
        if not sequence:
            return 0.0
        return max(step.time_ms for step in sequence) / 1000.0
    
    def _generate_safety_notes(self, transfer_mode: TransferMode) -> List[str]:
        """Generate safety notes for transfer mode"""
        notes = {
            TransferMode.OPEN_TRANSITION: [
                "Momentary power interruption will occur",
                "Ensure critical loads can handle brief outage",
                "UPS systems should be operational",
                "Notify affected personnel before transfer"
            ],
            TransferMode.CLOSED_TRANSITION: [
                "Buses must be synchronized within IEEE 1547 limits",
                "Monitor for circulating currents during parallel operation",
                "Sync-check relay must be functional",
                "Verify both sources can handle load"
            ],
            TransferMode.SOFT_TRANSFER: [
                "Transfer will take several seconds",
                "Monitor load sharing throughout process",
                "Be prepared to abort if issues arise",
                "Both sources must remain available during transfer"
            ]
        }
        return notes.get(transfer_mode, ["Follow standard safety procedures"])


# Testing and example usage
if __name__ == "__main__":
    print("âš¡ Bus Tie Synchronization Test")
    print("=" * 70)
    
    controller = BusTieController()
    
    # Add test buses
    bus1 = BusParameters(
        bus_id="bus1",
        bus_tag="MDB-01",
        voltage_kv=11.0,
        frequency_hz=50.0,
        phase_angle_deg=0.0,
        load_mw=500.0,
        load_mvar=150.0,
        available_capacity_mw=1000.0
    )
    
    bus2 = BusParameters(
        bus_id="bus2",
        bus_tag="MDB-02",
        voltage_kv=10.95,  # Slightly different voltage
        frequency_hz=50.05,  # Slightly different frequency
        phase_angle_deg=10.0,  # Phase difference
        load_mw=300.0,
        load_mvar=100.0,
        available_capacity_mw=800.0
    )
    
    controller.add_bus(bus1)
    controller.add_bus(bus2)
    
    print("\nâœ… Added 2 test buses")
    
    # Test synchronization check
    print("\nðŸ“Š Synchronization Check:")
    sync_check = controller.check_synchronization("bus1", "bus2")
    print(f"  Synchronized: {sync_check.synchronized}")
    print(f"  Voltage Diff: {sync_check.voltage_diff_percent:.2f}%")
    print(f"  Frequency Diff: {sync_check.frequency_diff_hz:.3f} Hz")
    print(f"  Phase Diff: {sync_check.phase_diff_deg:.1f}Â°")
    if sync_check.issues:
        print(f"  Issues: {', '.join(sync_check.issues)}")
    
    # Test load transfer planning
    print("\nðŸ”„ Load Transfer Plan (Open Transition):")
    transfer_plan = controller.plan_load_transfer(
        "bus1", "bus2", 200.0, TransferMode.OPEN_TRANSITION
    )
    
    if transfer_plan['feasible']:
        print(f"  Transfer: {transfer_plan['load_mw']} MW")
        print(f"  From: {transfer_plan['from_bus']} â†’ To: {transfer_plan['to_bus']}")
        print(f"  Time: {transfer_plan['estimated_time_seconds']} seconds")
        print(f"\n  Sequence:")
        for step in transfer_plan['sequence']:
            print(f"    Step {step['step_number']}: {step['action']} @ {step['time_ms']}ms")
    
    # Test load sharing
    print("\nâš–ï¸  Load Sharing Calculation:")
    sharing = controller.calculate_load_sharing("bus1", "bus2")
    print(f"  Total Load: {sharing['total_load_mw']} MW")
    print(f"  {sharing['bus_1_tag']}: {sharing['bus_1_load_mw']:.1f} MW ({sharing['bus_1_percent']:.1f}%)")
    print(f"  {sharing['bus_2_tag']}: {sharing['bus_2_load_mw']:.1f} MW ({sharing['bus_2_percent']:.1f}%)")
    
    print("\nâœ… Bus Tie Synchronization test complete!")
