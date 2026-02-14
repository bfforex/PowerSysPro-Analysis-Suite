"""
PwrSysPro Analysis Suite - Project Serialization (.psp format)
Phase 2: Save and load complete projects with 100% data retention.

The .psp (PwrSysPro Project) file format is a JSON-based format that contains:
- Project metadata
- Component library references
- Canvas layout (node positions)
- Network topology (connections)
- Calculation results
- Design basis and standards

File Structure:
{
    "format_version": "2.0",
    "project": {...},
    "nodes": [...],
    "connections": [...],
    "topology": {...},
    "calculations": {...},
    "metadata": {...}
}
"""

import json
import gzip
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class PSPFileFormat:
    """
    Handles serialization and deserialization of .psp project files.
    """
    
    FORMAT_VERSION = "2.0"
    FILE_EXTENSION = ".psp"
    
    def __init__(self):
        self.compress = True  # Use gzip compression by default
    
    def serialize_project(
        self,
        project_data: Dict,
        nodes_data: List[Dict],
        connections_data: List[Dict],
        topology_data: Optional[Dict] = None,
        calculations_data: Optional[Dict] = None
    ) -> Dict:
        """
        Serialize project data into .psp format.
        
        Args:
            project_data: Project metadata (name, description, standards, etc.)
            nodes_data: List of node dictionaries
            connections_data: List of connection dictionaries
            topology_data: Optional topology graph data
            calculations_data: Optional calculation results
        
        Returns:
            Complete project data as dictionary
        """
        psp_data = {
            "format_version": self.FORMAT_VERSION,
            "created_at": datetime.utcnow().isoformat(),
            "application": "PwrSysPro Analysis Suite",
            
            "project": {
                "id": project_data.get("id"),
                "name": project_data.get("name", "Untitled Project"),
                "description": project_data.get("description", ""),
                "base_mva": project_data.get("base_mva", 100.0),
                "system_frequency": project_data.get("system_frequency", 50.0),
                "standard_short_circuit": project_data.get("standard_short_circuit", "IEC 60909"),
                "standard_cable": project_data.get("standard_cable", "IEC 60364-5-52"),
                "created_at": project_data.get("created_at"),
                "updated_at": datetime.utcnow().isoformat()
            },
            
            "nodes": self._serialize_nodes(nodes_data),
            "connections": self._serialize_connections(connections_data),
            
            "metadata": {
                "node_count": len(nodes_data),
                "connection_count": len(connections_data),
                "saved_by": "PwrSysPro v2.0",
                "schema_version": "2.0"
            }
        }
        
        # Add optional data
        if topology_data:
            psp_data["topology"] = topology_data
        
        if calculations_data:
            psp_data["calculations"] = calculations_data
        
        return psp_data
    
    def _serialize_nodes(self, nodes_data: List[Dict]) -> List[Dict]:
        """Serialize node data with proper formatting."""
        serialized_nodes = []
        
        for node in nodes_data:
            serialized_node = {
                "id": node.get("id"),
                "type": node.get("type"),
                "position": {
                    "x": node.get("position_x", 0),
                    "y": node.get("position_y", 0)
                },
                "tag": node.get("custom_tag", ""),
                "component_library_id": node.get("component_library_id"),
                "properties": node.get("properties", {}),
                "location": {
                    "site": node.get("location_site"),
                    "building": node.get("location_building"),
                    "room": node.get("location_room")
                },
                "results": node.get("results", {})
            }
            serialized_nodes.append(serialized_node)
        
        return serialized_nodes
    
    def _serialize_connections(self, connections_data: List[Dict]) -> List[Dict]:
        """Serialize connection data."""
        serialized_connections = []
        
        for conn in connections_data:
            serialized_conn = {
                "id": conn.get("id"),
                "source_node_id": conn.get("source_node_id"),
                "target_node_id": conn.get("target_node_id"),
                "cable_library_id": conn.get("cable_library_id"),
                "length": conn.get("length", 0),
                "installation": {
                    "method": conn.get("installation_method", "E"),
                    "grouping_factor": conn.get("grouping_factor", 1.0),
                    "ambient_temp": conn.get("ambient_temp", 30.0)
                },
                "properties": conn.get("properties", {})
            }
            serialized_connections.append(serialized_conn)
        
        return serialized_connections
    
    def save_to_file(self, psp_data: Dict, file_path: str) -> bool:
        """
        Save project data to .psp file.
        
        Args:
            psp_data: Serialized project data
            file_path: Path to save file (will add .psp if missing)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure .psp extension
            path = Path(file_path)
            if path.suffix != self.FILE_EXTENSION:
                path = path.with_suffix(self.FILE_EXTENSION)
            
            # Convert to JSON
            json_str = json.dumps(psp_data, indent=2, ensure_ascii=False)
            
            # Save with or without compression
            if self.compress:
                with gzip.open(path, 'wt', encoding='utf-8') as f:
                    f.write(json_str)
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            
            return True
            
        except Exception as e:
            print(f"Error saving .psp file: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> Optional[Dict]:
        """
        Load project data from .psp file.
        
        Args:
            file_path: Path to .psp file
        
        Returns:
            Project data dictionary or None if error
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                print(f"File not found: {file_path}")
                return None
            
            # Try to load as compressed first
            try:
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    psp_data = json.load(f)
            except (gzip.BadGzipFile, OSError):
                # Not compressed, load as regular JSON
                with open(path, 'r', encoding='utf-8') as f:
                    psp_data = json.load(f)
            
            # Validate format version
            if not self._validate_format(psp_data):
                print("Invalid or unsupported .psp format")
                return None
            
            return psp_data
            
        except Exception as e:
            print(f"Error loading .psp file: {e}")
            return None
    
    def _validate_format(self, psp_data: Dict) -> bool:
        """Validate .psp file format."""
        required_keys = ["format_version", "project", "nodes", "connections"]
        
        for key in required_keys:
            if key not in psp_data:
                print(f"Missing required key: {key}")
                return False
        
        # Check version compatibility
        version = psp_data.get("format_version", "")
        major_version = version.split(".")[0] if "." in version else version
        
        if major_version != "2":
            print(f"Unsupported format version: {version}")
            return False
        
        return True
    
    def deserialize_project(self, psp_data: Dict) -> Dict:
        """
        Deserialize .psp data back into database format.
        
        Returns:
            Dictionary with 'project', 'nodes', and 'connections' keys
        """
        return {
            "project": psp_data["project"],
            "nodes": self._deserialize_nodes(psp_data["nodes"]),
            "connections": self._deserialize_connections(psp_data["connections"]),
            "topology": psp_data.get("topology"),
            "calculations": psp_data.get("calculations"),
            "metadata": psp_data.get("metadata", {})
        }
    
    def _deserialize_nodes(self, nodes_data: List[Dict]) -> List[Dict]:
        """Convert .psp node format back to database format."""
        db_nodes = []
        
        for node in nodes_data:
            db_node = {
                "id": node.get("id"),
                "type": node.get("type"),
                "position_x": node.get("position", {}).get("x", 0),
                "position_y": node.get("position", {}).get("y", 0),
                "custom_tag": node.get("tag", ""),
                "component_library_id": node.get("component_library_id"),
                "properties": node.get("properties", {}),
                "location_site": node.get("location", {}).get("site"),
                "location_building": node.get("location", {}).get("building"),
                "location_room": node.get("location", {}).get("room"),
                "results": node.get("results", {})
            }
            db_nodes.append(db_node)
        
        return db_nodes
    
    def _deserialize_connections(self, connections_data: List[Dict]) -> List[Dict]:
        """Convert .psp connection format back to database format."""
        db_connections = []
        
        for conn in connections_data:
            db_conn = {
                "id": conn.get("id"),
                "source_node_id": conn.get("source_node_id"),
                "target_node_id": conn.get("target_node_id"),
                "cable_library_id": conn.get("cable_library_id"),
                "length": conn.get("length", 0),
                "installation_method": conn.get("installation", {}).get("method", "E"),
                "grouping_factor": conn.get("installation", {}).get("grouping_factor", 1.0),
                "ambient_temp": conn.get("installation", {}).get("ambient_temp", 30.0),
                "properties": conn.get("properties", {})
            }
            db_connections.append(db_conn)
        
        return db_connections
    
    def export_summary(self, psp_data: Dict) -> str:
        """
        Generate a human-readable summary of the .psp file.
        """
        project = psp_data.get("project", {})
        metadata = psp_data.get("metadata", {})
        
        summary = f"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘         PwrSysPro Project Summary                              â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘                                                                â•‘
â•‘  Project: {project.get('name', 'Unknown'):<48} â•‘
â•‘  Format Version: {psp_data.get('format_version', 'Unknown'):<43} â•‘
â•‘  Components: {metadata.get('node_count', 0):<48} â•‘
â•‘  Connections: {metadata.get('connection_count', 0):<47} â•‘
â•‘  Standards: {project.get('standard_short_circuit', 'Unknown'):<48} â•‘
â•‘  Base MVA: {project.get('base_mva', 0):<49} â•‘
â•‘  Frequency: {project.get('system_frequency', 0)} Hz{' ' * 43} â•‘
â•‘                                                                â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        """
        
        return summary.strip()


def create_backup(file_path: str) -> Optional[str]:
    """
    Create a backup copy of a .psp file.
    
    Args:
        file_path: Path to original file
    
    Returns:
        Path to backup file or None if failed
    """
    try:
        path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_name(f"{path.stem}_backup_{timestamp}{path.suffix}")
        
        # Copy file
        with open(path, 'rb') as src:
            with open(backup_path, 'wb') as dst:
                dst.write(src.read())
        
        return str(backup_path)
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        return None


def merge_projects(file1: str, file2: str, output_file: str) -> bool:
    """
    Merge two .psp project files into one.
    Useful for combining subsystems.
    
    Args:
        file1: First project file
        file2: Second project file
        output_file: Output merged file
    
    Returns:
        True if successful
    """
    try:
        psp = PSPFileFormat()
        
        # Load both files
        data1 = psp.load_from_file(file1)
        data2 = psp.load_from_file(file2)
        
        if not data1 or not data2:
            return False
        
        # Offset node IDs in second project to avoid conflicts
        max_id1 = max([n["id"] for n in data1["nodes"]] + [0])
        id_offset = max_id1 + 1
        
        # Merge nodes
        merged_nodes = data1["nodes"].copy()
        for node in data2["nodes"]:
            node["id"] = node["id"] + id_offset
            merged_nodes.append(node)
        
        # Merge connections (update IDs)
        merged_connections = data1["connections"].copy()
        for conn in data2["connections"]:
            conn["id"] = conn["id"] + id_offset
            conn["source_node_id"] = conn["source_node_id"] + id_offset
            conn["target_node_id"] = conn["target_node_id"] + id_offset
            merged_connections.append(conn)
        
        # Create merged project
        merged_project = data1["project"].copy()
        merged_project["name"] = f"{data1['project']['name']} + {data2['project']['name']}"
        merged_project["description"] = "Merged project"
        
        # Serialize and save
        merged_data = psp.serialize_project(
            merged_project,
            merged_nodes,
            merged_connections
        )
        
        return psp.save_to_file(merged_data, output_file)
        
    except Exception as e:
        print(f"Error merging projects: {e}")
        return False


# Example usage
if __name__ == "__main__":
    print("ðŸ’¾ PwrSysPro File Serialization Test")
    print("=" * 70)
    
    # Create test data
    project_data = {
        "id": 1,
        "name": "Sample Industrial Facility",
        "description": "400V distribution with motor loads",
        "base_mva": 100.0,
        "system_frequency": 50.0,
        "standard_short_circuit": "IEC 60909",
        "standard_cable": "IEC 60364-5-52"
    }
    
    nodes_data = [
        {
            "id": 1,
            "type": "Source",
            "position_x": 100.0,
            "position_y": 50.0,
            "custom_tag": "SRC-11-01",
            "component_library_id": None,
            "properties": {"voltage": 11000}
        },
        {
            "id": 2,
            "type": "Transformer",
            "position_x": 100.0,
            "position_y": 150.0,
            "custom_tag": "T-11-SRC-MDP-01",
            "component_library_id": 1,
            "properties": {"rating_kva": 1000}
        }
    ]
    
    connections_data = [
        {
            "id": 1,
            "source_node_id": 1,
            "target_node_id": 2,
            "cable_library_id": None,
            "length": 25.0,
            "installation_method": "E"
        }
    ]
    
    # Test serialization
    psp = PSPFileFormat()
    psp_data = psp.serialize_project(project_data, nodes_data, connections_data)
    
    print("\nðŸ“Š Serialized Data:")
    print("-" * 70)
    print(f"Format Version: {psp_data['format_version']}")
    print(f"Project: {psp_data['project']['name']}")
    print(f"Nodes: {len(psp_data['nodes'])}")
    print(f"Connections: {len(psp_data['connections'])}")
    
    # Test file save/load
    test_file = "/tmp/test_project.psp"
    
    print(f"\nðŸ’¾ Saving to: {test_file}")
    success = psp.save_to_file(psp_data, test_file)
    print(f"   {'âœ… Success' if success else 'âŒ Failed'}")
    
    print(f"\nðŸ“‚ Loading from: {test_file}")
    loaded_data = psp.load_from_file(test_file)
    if loaded_data:
        print("   âœ… Success")
        print(psp.export_summary(loaded_data))
    else:
        print("   âŒ Failed")
    
    print("\nâœ… Serialization test complete!")
