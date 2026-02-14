"""
PwrSysPro Analysis Suite - Database Models
Defines the SQLAlchemy models for the component library, project nodes, and connections.
Standards Reference: IEC 60364-5-52 (Cable Ampacity), IEC 60909 (Short Circuit)
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class ComponentLibrary(Base):
    """
    Stores manufacturer data for electrical components.
    This is the 'Source of Truth' for all component specifications.
    """
    __tablename__ = 'component_library'
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # Cable, Breaker, Motor, Transformer, Bus
    model = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    voltage_rating = Column(Float, nullable=False)  # Voltage in kV
    
    # Electrical Parameters
    impedance_r = Column(Float)  # Resistance in ohms/km or ohms
    impedance_x = Column(Float)  # Reactance in ohms/km or ohms
    impedance_z_percent = Column(Float)  # For transformers (Z%)
    
    # Thermal & Protection Parameters
    ampacity_base = Column(Float)  # Base current rating in Amps
    short_circuit_rating = Column(Float)  # kAIC rating for breakers
    thermal_limit_i2t = Column(Float)  # IÂ²t withstand for cables
    
    # Physical & Installation Data
    cross_section = Column(Float)  # Cable CSA in mmÂ²
    conductor_material = Column(String)  # Copper, Aluminum
    insulation_type = Column(String)  # XLPE, PVC, EPR
    
    # Additional properties stored as JSON
    properties = Column(JSON)  # Trip curves, dimensions, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Component {self.manufacturer} {self.model} - {self.type}>"


class Project(Base):
    """
    Stores project metadata and settings.
    """
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    
    # Design Basis
    base_mva = Column(Float, default=100.0)  # Base MVA for per-unit calculations
    system_frequency = Column(Float, default=50.0)  # 50 Hz or 60 Hz
    
    # Standards Selection
    standard_short_circuit = Column(String, default='IEC 60909')  # IEC 60909 or ANSI C37
    standard_cable = Column(String, default='IEC 60364-5-52')
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    nodes = relationship("ProjectNode", back_populates="project", cascade="all, delete-orphan")
    connections = relationship("ProjectConnection", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.name}>"


class ProjectNode(Base):
    """
    Represents individual components placed on the canvas (Digital Twin elements).
    Each node has a position, type, and auto-generated tag.
    """
    __tablename__ = 'project_nodes'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Canvas Position
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    
    # Component Type and Identity
    type = Column(String, nullable=False)  # Source, Transformer, Bus, Breaker, Motor, Cable
    custom_tag = Column(String)  # Auto-generated tag: [TYPE]-[V]-[FROM]-[TO]-[SEQ]
    
    # Link to Component Library
    component_library_id = Column(Integer, ForeignKey('component_library.id'))
    component_library = relationship("ComponentLibrary")
    
    # Node-specific properties (JSON blob for flexibility)
    properties = Column(JSON)  # Length, trip settings, load details, etc.
    
    # Location Hierarchy (for cable routing and derating)
    location_site = Column(String)
    location_building = Column(String)
    location_room = Column(String)
    
    # Calculation Results (cached)
    results = Column(JSON)  # Voltage drop, fault current, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="nodes")
    outgoing_connections = relationship(
        "ProjectConnection", 
        foreign_keys="ProjectConnection.source_node_id",
        back_populates="source_node"
    )
    incoming_connections = relationship(
        "ProjectConnection", 
        foreign_keys="ProjectConnection.target_node_id",
        back_populates="target_node"
    )
    
    def __repr__(self):
        return f"<Node {self.custom_tag} - {self.type}>"


class ProjectConnection(Base):
    """
    Represents connections (cables/wires) between nodes.
    The 'edge' in the graph representation of the power system.
    """
    __tablename__ = 'project_connections'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    # Source and Target Nodes
    source_node_id = Column(Integer, ForeignKey('project_nodes.id'), nullable=False)
    target_node_id = Column(Integer, ForeignKey('project_nodes.id'), nullable=False)
    
    # Cable/Connection Properties
    cable_library_id = Column(Integer, ForeignKey('component_library.id'))
    cable_library = relationship("ComponentLibrary")
    
    # Physical Parameters
    length = Column(Float)  # Cable length in meters
    
    # Installation Conditions (for derating per IEC 60364-5-52)
    installation_method = Column(String)  # Tray, Conduit, Underground
    grouping_factor = Column(Float, default=1.0)
    ambient_temp = Column(Float, default=30.0)  # Â°C
    
    # Connection Properties
    properties = Column(JSON)  # Additional settings
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="connections")
    source_node = relationship("ProjectNode", foreign_keys=[source_node_id], back_populates="outgoing_connections")
    target_node = relationship("ProjectNode", foreign_keys=[target_node_id], back_populates="incoming_connections")
    
    def __repr__(self):
        return f"<Connection {self.source_node_id} â†’ {self.target_node_id}>"


class CalculationHistory(Base):
    """
    Audit trail for calculations.
    Ensures users can't export invalid results after modifications.
    """
    __tablename__ = 'calculation_history'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    calculation_type = Column(String, nullable=False)  # ShortCircuit, LoadFlow, VoltageDrop
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Snapshot of system state when calculation was performed
    system_snapshot = Column(JSON)
    
    # Results
    results = Column(JSON)
    is_valid = Column(Integer, default=1)  # 1 = Valid, 0 = Invalidated by changes
    
    def __repr__(self):
        return f"<Calculation {self.calculation_type} at {self.timestamp}>"


# Database initialization
def init_db(db_path='sqlite:///pwrsyspro.db'):
    """Initialize the database with tables."""
    engine = create_engine(db_path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def get_db_session(SessionLocal):
    """Dependency for FastAPI to get database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
