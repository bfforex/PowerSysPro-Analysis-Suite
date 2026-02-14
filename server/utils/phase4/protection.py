"""
PwrSysPro Analysis Suite - Protection Coordination (Phase 4)
Time-Current Characteristic (TCC) curves and selectivity analysis.

Protection coordination ensures that the protective device closest to
a fault operates first, minimizing the affected area and system disruption.

Features:
- TCC curve generation for breakers, fuses, relays
- Selectivity analysis
- Coordination time intervals (CTI)
- Discrimination studies
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np


class DeviceType(Enum):
    """Types of protective devices."""
    MOLDED_CASE_BREAKER = "MCB"
    LOW_VOLTAGE_BREAKER = "MCCB"
    POWER_BREAKER = "ACB"
    FUSE = "Fuse"
    RELAY_OVERCURRENT = "OCR"
    RELAY_INSTANTANEOUS = "IOC"


class CurveType(Enum):
    """Standard inverse time curves."""
    STANDARD_INVERSE = "SI"
    VERY_INVERSE = "VI"
    EXTREMELY_INVERSE = "EI"
    LONG_TIME_INVERSE = "LTI"
    DEFINITE_TIME = "DT"


@dataclass
class ProtectiveDeviceSettings:
    """Settings for a protective device."""
    device_id: str
    device_type: DeviceType
    curve_type: CurveType
    
    # Current settings
    pickup_current: float          # Amperes
    time_multiplier: float = 1.0   # TMS (Time Multiplier Setting)
    
    # Instantaneous settings
    instantaneous_enabled: bool = True
    instantaneous_multiple: float = 10.0  # Multiple of pickup
    
    # Additional parameters
    ct_ratio: float = 1.0          # Current transformer ratio
    rated_current: float = 100.0   # Device rated current


@dataclass
class TCCPoint:
    """Single point on Time-Current Curve."""
    current: float  # Amperes
    time: float     # Seconds


@dataclass
class CoordinationResult:
    """Result of coordination analysis between two devices."""
    upstream_device: str
    downstream_device: str
    is_coordinated: bool
    min_cti: float              # Minimum coordination time interval (seconds)
    critical_current: float     # Current at minimum CTI
    margin: str                 # "Adequate", "Marginal", "None"


class ProtectionCoordinator:
    """
    Protection coordination and TCC curve generator.
    """
    
    def __init__(self):
        """Initialize coordinator."""
        self.devices: Dict[str, ProtectiveDeviceSettings] = {}
        self.curves: Dict[str, List[TCCPoint]] = {}
    
    def add_device(self, settings: ProtectiveDeviceSettings):
        """Add a protective device."""
        self.devices[settings.device_id] = settings
        
        # Generate TCC curve
        self.curves[settings.device_id] = self._generate_tcc_curve(settings)
    
    def _generate_tcc_curve(
        self,
        settings: ProtectiveDeviceSettings
    ) -> List[TCCPoint]:
        """
        Generate Time-Current Characteristic curve.
        
        Uses IEC 60255 / IEEE C37.112 standard inverse curves.
        """
        points = []
        
        # Current range: 1x to 20x pickup
        i_pickup = settings.pickup_current
        current_multiples = np.logspace(0, 1.5, 50)  # 1x to ~30x
        
        for m in current_multiples:
            i = i_pickup * m
            
            # Calculate operating time
            t = self._calculate_operating_time(
                current=i,
                pickup=i_pickup,
                tms=settings.time_multiplier,
                curve_type=settings.curve_type
            )
            
            if t is not None and t > 0:
                points.append(TCCPoint(current=i, time=t))
        
        # Add instantaneous point if enabled
        if settings.instantaneous_enabled:
            i_inst = i_pickup * settings.instantaneous_multiple
            points.append(TCCPoint(current=i_inst, time=0.01))  # ~10ms
        
        return points
    
    def _calculate_operating_time(
        self,
        current: float,
        pickup: float,
        tms: float,
        curve_type: CurveType
    ) -> Optional[float]:
        """
        Calculate operating time for given current.
        
        Uses IEC 60255 standard equations:
        t = TMS Ã— k / ((I/I_p)^Î± - 1)
        
        Where:
        - TMS: Time multiplier setting
        - I: Fault current
        - I_p: Pickup current
        - k, Î±: Constants depending on curve type
        """
        if current < pickup:
            return None  # Below pickup, won't operate
        
        m = current / pickup  # Current multiple
        
        # IEC 60255 constants
        if curve_type == CurveType.STANDARD_INVERSE:
            k = 0.14
            alpha = 0.02
        elif curve_type == CurveType.VERY_INVERSE:
            k = 13.5
            alpha = 1.0
        elif curve_type == CurveType.EXTREMELY_INVERSE:
            k = 80.0
            alpha = 2.0
        elif curve_type == CurveType.LONG_TIME_INVERSE:
            k = 120.0
            alpha = 1.0
        else:  # Definite time
            return tms
        
        try:
            t = tms * (k / (m**alpha - 1))
            return t
        except:
            return None
    
    def analyze_coordination(
        self,
        upstream_id: str,
        downstream_id: str,
        required_cti: float = 0.3
    ) -> CoordinationResult:
        """
        Analyze coordination between two devices.
        
        Coordination is achieved if upstream device operates at least
        CTI (Coordination Time Interval) after downstream device.
        
        Typical CTI: 0.2-0.4 seconds
        
        Args:
            upstream_id: ID of upstream (backup) device
            downstream_id: ID of downstream (primary) device
            required_cti: Required coordination time interval (seconds)
        
        Returns:
            CoordinationResult
        """
        if upstream_id not in self.curves or downstream_id not in self.curves:
            raise ValueError("Device not found")
        
        upstream_curve = self.curves[upstream_id]
        downstream_curve = self.curves[downstream_id]
        
        # Find minimum CTI across all current levels
        min_cti = float('inf')
        critical_current = 0
        
        for down_point in downstream_curve:
            i = down_point.current
            t_down = down_point.time
            
            # Find upstream time at same current
            t_up = self._interpolate_time(upstream_curve, i)
            
            if t_up is not None:
                cti = t_up - t_down
                
                if cti < min_cti:
                    min_cti = cti
                    critical_current = i
        
        # Determine coordination status
        is_coordinated = min_cti >= required_cti
        
        if min_cti >= required_cti * 1.5:
            margin = "Adequate"
        elif min_cti >= required_cti:
            margin = "Marginal"
        else:
            margin = "None"
        
        return CoordinationResult(
            upstream_device=upstream_id,
            downstream_device=downstream_id,
            is_coordinated=is_coordinated,
            min_cti=round(min_cti, 3),
            critical_current=round(critical_current, 1),
            margin=margin
        )
    
    def _interpolate_time(
        self,
        curve: List[TCCPoint],
        current: float
    ) -> Optional[float]:
        """Interpolate operating time at given current."""
        if not curve:
            return None
        
        # Find bracketing points
        for i in range(len(curve) - 1):
            if curve[i].current <= current <= curve[i+1].current:
                # Linear interpolation in log-log space
                i1, i2 = curve[i].current, curve[i+1].current
                t1, t2 = curve[i].time, curve[i+1].time
                
                if i1 == i2:
                    return t1
                
                # Log interpolation
                log_i = math.log10(current)
                log_i1 = math.log10(i1)
                log_i2 = math.log10(i2)
                log_t1 = math.log10(max(t1, 0.001))
                log_t2 = math.log10(max(t2, 0.001))
                
                log_t_result = log_t1 + (log_i - log_i1) * (log_t2 - log_t1) / (log_i2 - log_i1)
                
                return 10 ** log_t_result
        
        # Extrapolate if beyond curve
        if current > curve[-1].current:
            return curve[-1].time
        elif current < curve[0].current:
            return None
        
        return None
    
    def generate_coordination_study(
        self,
        device_pairs: List[Tuple[str, str]],
        required_cti: float = 0.3
    ) -> Dict:
        """
        Generate complete coordination study.
        
        Args:
            device_pairs: List of (upstream, downstream) pairs
            required_cti: Required CTI in seconds
        
        Returns:
            Study results dictionary
        """
        results = {
            'pairs_analyzed': len(device_pairs),
            'coordinated_pairs': 0,
            'uncoordinated_pairs': 0,
            'details': []
        }
        
        for upstream, downstream in device_pairs:
            coord = self.analyze_coordination(upstream, downstream, required_cti)
            
            if coord.is_coordinated:
                results['coordinated_pairs'] += 1
            else:
                results['uncoordinated_pairs'] += 1
            
            results['details'].append({
                'upstream': upstream,
                'downstream': downstream,
                'coordinated': coord.is_coordinated,
                'min_cti': coord.min_cti,
                'critical_current': coord.critical_current,
                'margin': coord.margin
            })
        
        results['overall_status'] = "PASS" if results['uncoordinated_pairs'] == 0 else "FAIL"
        
        return results
    
    def export_tcc_data(self, device_id: str) -> Dict:
        """Export TCC curve data for plotting."""
        if device_id not in self.curves:
            return None
        
        curve = self.curves[device_id]
        settings = self.devices[device_id]
        
        return {
            'device_id': device_id,
            'device_type': settings.device_type.value,
            'curve_type': settings.curve_type.value,
            'pickup_current': settings.pickup_current,
            'points': [
                {'current': p.current, 'time': p.time}
                for p in curve
            ]
        }


def recommend_relay_settings(
    load_current: float,
    fault_current: float,
    upstream_device_time: float,
    required_cti: float = 0.3
) -> Dict:
    """
    Recommend relay settings for coordination.
    
    Args:
        load_current: Normal load current (A)
        fault_current: Maximum fault current (A)
        upstream_device_time: Operating time of upstream device (s)
        required_cti: Required coordination time interval (s)
    
    Returns:
        Recommended settings
    """
    # Pickup: 1.2-1.5Ã— load current
    recommended_pickup = load_current * 1.3
    
    # Time multiplier: Calculate to coordinate with upstream
    target_time = upstream_device_time - required_cti - 0.1  # 0.1s margin
    
    # Use standard inverse curve
    m = fault_current / recommended_pickup
    k = 0.14
    alpha = 0.02
    
    # Solve for TMS: t = TMS Ã— k / (m^Î± - 1)
    recommended_tms = target_time * (m**alpha - 1) / k
    recommended_tms = max(0.05, min(recommended_tms, 1.0))  # Limit 0.05-1.0
    
    # Instantaneous: 8-12Ã— pickup, beyond fault current
    recommended_inst = recommended_pickup * 10.0
    if recommended_inst <= fault_current * 1.2:
        recommended_inst = fault_current * 1.3
    
    return {
        'pickup_current': round(recommended_pickup, 1),
        'time_multiplier': round(recommended_tms, 3),
        'instantaneous_multiple': round(recommended_inst / recommended_pickup, 1),
        'curve_type': 'STANDARD_INVERSE',
        'notes': [
            f"Pickup set at {(recommended_pickup/load_current):.1f}Ã— load current",
            f"TMS coordinated with upstream device",
            f"Instantaneous set above maximum fault current"
        ]
    }


# Example usage
if __name__ == "__main__":
    print("ðŸ”’ Protection Coordination Test")
    print("=" * 70)
    
    # Create coordinator
    coord = ProtectionCoordinator()
    
    # Add devices
    # Upstream: Utility breaker
    coord.add_device(ProtectiveDeviceSettings(
        device_id="CB-MAIN",
        device_type=DeviceType.POWER_BREAKER,
        curve_type=CurveType.STANDARD_INVERSE,
        pickup_current=1000.0,
        time_multiplier=0.5,
        instantaneous_multiple=12.0
    ))
    
    # Downstream: Feeder breaker
    coord.add_device(ProtectiveDeviceSettings(
        device_id="CB-FEEDER-1",
        device_type=DeviceType.LOW_VOLTAGE_BREAKER,
        curve_type=CurveType.STANDARD_INVERSE,
        pickup_current=200.0,
        time_multiplier=0.1,
        instantaneous_multiple=10.0
    ))
    
    # Analyze coordination
    print("\nðŸ” Coordination Analysis:")
    print("-" * 70)
    
    result = coord.analyze_coordination("CB-MAIN", "CB-FEEDER-1", required_cti=0.3)
    
    print(f"Upstream:         {result.upstream_device}")
    print(f"Downstream:       {result.downstream_device}")
    print(f"Coordinated:      {'âœ… YES' if result.is_coordinated else 'âŒ NO'}")
    print(f"Min CTI:          {result.min_cti} seconds")
    print(f"Critical Current: {result.critical_current} A")
    print(f"Margin:           {result.margin}")
    
    # Recommend settings
    print("\nâš™ï¸  Recommended Settings for New Relay:")
    print("-" * 70)
    
    recommendations = recommend_relay_settings(
        load_current=150.0,
        fault_current=5000.0,
        upstream_device_time=1.5
    )
    
    print(f"Pickup Current:   {recommendations['pickup_current']} A")
    print(f"Time Multiplier:  {recommendations['time_multiplier']}")
    print(f"Inst Multiple:    {recommendations['instantaneous_multiple']}Ã—")
    print(f"Curve Type:       {recommendations['curve_type']}")
    print("\nNotes:")
    for note in recommendations['notes']:
        print(f"  â€¢ {note}")
    
    print("\nâœ… Protection coordination test complete!")
