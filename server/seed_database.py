"""
PwrSysPro Analysis Suite - Database Seed Script
Populates the component library with sample manufacturer data.
Data based on: Schneider Electric, ABB, and other manufacturers' specifications.
Standards: IEC 60364-5-52 for cable ampacity ratings.
"""

from models.database import init_db, ComponentLibrary, Project
from sqlalchemy.orm import Session

def seed_component_library(db: Session):
    """
    Seed the component library with standard electrical components.
    Uses real manufacturer specifications where applicable.
    """
    
    # ============================================================================
    # CABLES - IEC 60364-5-52 Compliant Ratings
    # ============================================================================
    cables = [
        {
            "type": "Cable",
            "model": "NYY 4x185",
            "manufacturer": "Nexans",
            "voltage_rating": 0.6,  # 0.6 kV
            "impedance_r": 0.106,  # Ohms/km at 90Â°C (Copper)
            "impedance_x": 0.084,  # Ohms/km (Reactance)
            "ampacity_base": 358,  # Amps (IEC 60364-5-52, Method E)
            "cross_section": 185,  # mmÂ²
            "conductor_material": "Copper",
            "insulation_type": "PVC",
            "thermal_limit_i2t": 34225000,  # IÂ²t for short circuit (AÂ²s)
            "properties": {
                "cores": 4,
                "derating_factors": {
                    "ambient_30C": 1.0,
                    "ambient_40C": 0.91,
                    "ambient_50C": 0.82,
                    "grouping_2_cables": 0.80,
                    "grouping_3_cables": 0.70
                }
            }
        },
        {
            "type": "Cable",
            "model": "NYY 4x120",
            "manufacturer": "Nexans",
            "voltage_rating": 0.6,
            "impedance_r": 0.161,  # Ohms/km
            "impedance_x": 0.086,
            "ampacity_base": 285,  # Amps
            "cross_section": 120,
            "conductor_material": "Copper",
            "insulation_type": "PVC",
            "thermal_limit_i2t": 14400000,
            "properties": {"cores": 4}
        },
        {
            "type": "Cable",
            "model": "N2XSY 3x70/35",
            "manufacturer": "Prysmian",
            "voltage_rating": 0.6,
            "impedance_r": 0.268,  # Ohms/km
            "impedance_x": 0.091,
            "ampacity_base": 210,  # Amps (XLPE insulation)
            "cross_section": 70,
            "conductor_material": "Copper",
            "insulation_type": "XLPE",
            "thermal_limit_i2t": 4900000,
            "properties": {"cores": 3, "armor": "Steel Wire"}
        },
        {
            "type": "Cable",
            "model": "NYY 4x25",
            "manufacturer": "Nexans",
            "voltage_rating": 0.6,
            "impedance_r": 0.780,  # Ohms/km
            "impedance_x": 0.098,
            "ampacity_base": 96,  # Amps
            "cross_section": 25,
            "conductor_material": "Copper",
            "insulation_type": "PVC",
            "thermal_limit_i2t": 625000,
            "properties": {"cores": 4, "typical_use": "Panel Feeders"}
        },
        {
            "type": "Cable",
            "model": "N2XSY 3x240/120",
            "manufacturer": "Prysmian",
            "voltage_rating": 1.0,  # 1 kV
            "impedance_r": 0.0778,  # Ohms/km (Large feeder)
            "impedance_x": 0.082,
            "ampacity_base": 475,  # Amps
            "cross_section": 240,
            "conductor_material": "Copper",
            "insulation_type": "XLPE",
            "thermal_limit_i2t": 57600000,
            "properties": {"cores": 3, "armor": "Steel Wire", "typical_use": "Main Feeders"}
        }
    ]
    
    for cable_data in cables:
        cable = ComponentLibrary(**cable_data)
        db.add(cable)
    
    # ============================================================================
    # CIRCUIT BREAKERS - Schneider Electric Specifications
    # ============================================================================
    breakers = [
        {
            "type": "Breaker",
            "model": "Compact NSX250F",
            "manufacturer": "Schneider Electric",
            "voltage_rating": 0.69,  # Up to 690V AC
            "ampacity_base": 250,  # Frame rating
            "short_circuit_rating": 36,  # kAIC (Icu at 415V)
            "properties": {
                "breaking_capacity_415V": 36,  # kA
                "breaking_capacity_690V": 10,
                "trip_curves": ["TM-D", "MA"],
                "poles": 4,
                "series": "NSX"
            }
        },
        {
            "type": "Breaker",
            "model": "Compact NSX400F",
            "manufacturer": "Schneider Electric",
            "voltage_rating": 0.69,
            "ampacity_base": 400,
            "short_circuit_rating": 50,  # kAIC
            "properties": {
                "breaking_capacity_415V": 50,
                "breaking_capacity_690V": 25,
                "trip_curves": ["TM-D", "MA"],
                "poles": 4
            }
        },
        {
            "type": "Breaker",
            "model": "Compact NSX630F",
            "manufacturer": "Schneider Electric",
            "voltage_rating": 0.69,
            "ampacity_base": 630,
            "short_circuit_rating": 50,
            "properties": {
                "breaking_capacity_415V": 50,
                "breaking_capacity_690V": 25,
                "trip_curves": ["TM-D", "MA"],
                "poles": 4
            }
        },
        {
            "type": "Breaker",
            "model": "Masterpact MTZ1",
            "manufacturer": "Schneider Electric",
            "voltage_rating": 0.69,
            "ampacity_base": 1600,
            "short_circuit_rating": 65,  # kAIC
            "properties": {
                "breaking_capacity_415V": 65,
                "trip_unit": "Micrologic",
                "poles": 4,
                "typical_use": "Main Incomer"
            }
        }
    ]
    
    for breaker_data in breakers:
        breaker = ComponentLibrary(**breaker_data)
        db.add(breaker)
    
    # ============================================================================
    # TRANSFORMERS - Standard Distribution Transformers
    # ============================================================================
    transformers = [
        {
            "type": "Transformer",
            "model": "GEAFOL 1000kVA",
            "manufacturer": "ABB",
            "voltage_rating": 11.0,  # Primary: 11kV
            "impedance_z_percent": 6.0,  # Z% at rated MVA
            "ampacity_base": 1400,  # Secondary current at 0.415kV
            "properties": {
                "rating_kva": 1000,
                "primary_voltage": 11000,  # V
                "secondary_voltage": 415,  # V
                "connection": "Dyn11",
                "cooling": "AN",
                "losses_no_load": 1.8,  # kW
                "losses_load": 12.5  # kW at full load
            }
        },
        {
            "type": "Transformer",
            "model": "TRIHAL 2500kVA",
            "manufacturer": "Schneider Electric",
            "voltage_rating": 11.0,
            "impedance_z_percent": 6.0,
            "ampacity_base": 3470,  # Secondary current
            "properties": {
                "rating_kva": 2500,
                "primary_voltage": 11000,
                "secondary_voltage": 415,
                "connection": "Dyn11",
                "cooling": "AN"
            }
        }
    ]
    
    for transformer_data in transformers:
        transformer = ComponentLibrary(**transformer_data)
        db.add(transformer)
    
    # ============================================================================
    # MOTORS - Induction Motors (for back-feed calculations)
    # ============================================================================
    motors = [
        {
            "type": "Motor",
            "model": "3GAA 75kW IE3",
            "manufacturer": "ABB",
            "voltage_rating": 0.4,  # 400V
            "ampacity_base": 137,  # Full load current
            "impedance_r": 0.015,  # Per-unit R
            "impedance_x": 0.15,  # Per-unit X (subtransient)
            "properties": {
                "power_kw": 75,
                "poles": 4,
                "efficiency": 0.948,
                "power_factor": 0.85,
                "starting_current_ratio": 6.5,
                "locked_rotor_contribution": 4.0  # For fault studies
            }
        },
        {
            "type": "Motor",
            "model": "3GAA 110kW IE3",
            "manufacturer": "ABB",
            "voltage_rating": 0.4,
            "ampacity_base": 196,
            "impedance_r": 0.012,
            "impedance_x": 0.15,
            "properties": {
                "power_kw": 110,
                "poles": 4,
                "efficiency": 0.952,
                "power_factor": 0.86,
                "starting_current_ratio": 6.5
            }
        }
    ]
    
    for motor_data in motors:
        motor = ComponentLibrary(**motor_data)
        db.add(motor)
    
    print(f"âœ… Seeded {len(cables)} cables")
    print(f"âœ… Seeded {len(breakers)} breakers")
    print(f"âœ… Seeded {len(transformers)} transformers")
    print(f"âœ… Seeded {len(motors)} motors")


def create_sample_project(db: Session):
    """Create a sample project for testing."""
    project = Project(
        name="Sample Industrial Facility",
        description="400V distribution system with transformer and motor loads",
        base_mva=100.0,
        system_frequency=50.0,
        standard_short_circuit="IEC 60909",
        standard_cable="IEC 60364-5-52"
    )
    db.add(project)
    print("âœ… Created sample project")
    return project


def seed_database():
    """Main seeding function."""
    print("ðŸ”§ Initializing PwrSysPro Database...")
    engine, SessionLocal = init_db()
    
    db = SessionLocal()
    
    try:
        # Clear existing data (for development)
        print("ðŸ—‘ï¸  Clearing existing data...")
        db.query(ComponentLibrary).delete()
        db.query(Project).delete()
        db.commit()
        
        # Seed component library
        print("ðŸ“š Seeding Component Library...")
        seed_component_library(db)
        
        # Create sample project
        print("ðŸ“‹ Creating Sample Project...")
        create_sample_project(db)
        
        db.commit()
        print("\nâœ¨ Database seeded successfully!")
        print(f"ðŸ“Š Total components in library: {db.query(ComponentLibrary).count()}")
        
    except Exception as e:
        print(f"âŒ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
