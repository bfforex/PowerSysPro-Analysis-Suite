"""
PwrSysPro Analysis Suite - Topology Graph Engine
Phase 2: Converts the visual drawing into a Node-Link data structure for analysis.

This module provides:
- Graph representation of the electrical network
- Path finding and connectivity analysis
- Loop detection
- Bus identification
- Upstream/downstream relationships
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class TopologyNode:
    """Represents a node in the electrical network topology."""
    id: str
    type: str
    tag: str
    voltage_level: float
    properties: Dict = field(default_factory=dict)
    
    # Connectivity information
    upstream_nodes: List[str] = field(default_factory=list)
    downstream_nodes: List[str] = field(default_factory=list)
    
    # Network position
    level: int = 0  # Distance from source (0 = source)
    bus_name: Optional[str] = None  # Name of the bus this component is on


@dataclass
class TopologyEdge:
    """Represents a connection between nodes."""
    id: str
    source_id: str
    target_id: str
    cable_id: Optional[str]
    impedance: complex = 0j  # R + jX
    length: float = 0.0


class TopologyGraph:
    """
    Main topology graph engine.
    Maintains the electrical network as a directed graph.
    """
    
    def __init__(self):
        self.nodes: Dict[str, TopologyNode] = {}
        self.edges: Dict[str, TopologyEdge] = {}
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)
        
        # Buses (equipotential points)
        self.buses: Dict[str, Set[str]] = {}  # bus_name -> set of node_ids
        
        # Source nodes (starting points)
        self.sources: List[str] = []
        
    def add_node(self, node: TopologyNode) -> None:
        """Add a node to the topology."""
        self.nodes[node.id] = node
        
        # Track sources
        if node.type == "Source":
            self.sources.append(node.id)
            node.level = 0
    
    def add_edge(self, edge: TopologyEdge) -> None:
        """Add an edge (connection) to the topology."""
        self.edges[edge.id] = edge
        
        # Update adjacency lists
        self.adjacency[edge.source_id].append(edge.target_id)
        self.reverse_adjacency[edge.target_id].append(edge.source_id)
        
        # Update node relationships
        if edge.source_id in self.nodes and edge.target_id in self.nodes:
            self.nodes[edge.source_id].downstream_nodes.append(edge.target_id)
            self.nodes[edge.target_id].upstream_nodes.append(edge.source_id)
    
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from the topology."""
        if edge_id not in self.edges:
            return
        
        edge = self.edges[edge_id]
        
        # Update adjacency lists
        if edge.target_id in self.adjacency[edge.source_id]:
            self.adjacency[edge.source_id].remove(edge.target_id)
        
        if edge.source_id in self.reverse_adjacency[edge.target_id]:
            self.reverse_adjacency[edge.target_id].remove(edge.source_id)
        
        # Update node relationships
        if edge.source_id in self.nodes:
            if edge.target_id in self.nodes[edge.source_id].downstream_nodes:
                self.nodes[edge.source_id].downstream_nodes.remove(edge.target_id)
        
        if edge.target_id in self.nodes:
            if edge.source_id in self.nodes[edge.target_id].upstream_nodes:
                self.nodes[edge.target_id].upstream_nodes.remove(edge.source_id)
        
        del self.edges[edge_id]
    
    def calculate_network_levels(self) -> None:
        """
        Calculate the level (distance from source) for each node.
        Uses BFS from all source nodes.
        """
        # Reset levels
        for node in self.nodes.values():
            if node.type != "Source":
                node.level = -1
        
        # BFS from each source
        for source_id in self.sources:
            queue = deque([(source_id, 0)])
            visited = set([source_id])
            
            while queue:
                node_id, level = queue.popleft()
                
                # Update level if this is a shorter path
                if node_id in self.nodes:
                    if self.nodes[node_id].level == -1 or level < self.nodes[node_id].level:
                        self.nodes[node_id].level = level
                
                # Process downstream nodes
                for downstream_id in self.adjacency.get(node_id, []):
                    if downstream_id not in visited:
                        visited.add(downstream_id)
                        queue.append((downstream_id, level + 1))
    
    def identify_buses(self) -> Dict[str, Set[str]]:
        """
        Identify buses (equipotential points) in the network.
        A bus is a set of directly connected nodes at the same voltage level.
        """
        self.buses.clear()
        bus_counter = 1
        processed = set()
        
        for node_id, node in self.nodes.items():
            if node_id in processed:
                continue
            
            # Components that form buses
            if node.type in ["Bus", "Busbar", "Switchgear"]:
                bus_name = f"BUS-{node.voltage_level}kV-{bus_counter:02d}"
                bus_nodes = self._find_connected_bus_nodes(node_id, node.voltage_level)
                
                self.buses[bus_name] = bus_nodes
                
                # Update node bus names
                for bid in bus_nodes:
                    if bid in self.nodes:
                        self.nodes[bid].bus_name = bus_name
                        processed.add(bid)
                
                bus_counter += 1
        
        return self.buses
    
    def _find_connected_bus_nodes(self, start_id: str, voltage: float) -> Set[str]:
        """Find all nodes connected to a bus at the same voltage level."""
        connected = set([start_id])
        queue = deque([start_id])
        
        while queue:
            node_id = queue.popleft()
            
            # Check all adjacent nodes (both upstream and downstream)
            adjacent = (self.adjacency.get(node_id, []) + 
                       self.reverse_adjacency.get(node_id, []))
            
            for adj_id in adjacent:
                if adj_id in connected:
                    continue
                
                if adj_id in self.nodes:
                    adj_node = self.nodes[adj_id]
                    
                    # Only include if same voltage and bus-type component
                    if (adj_node.voltage_level == voltage and 
                        adj_node.type in ["Bus", "Busbar", "Switchgear"]):
                        connected.add(adj_id)
                        queue.append(adj_id)
        
        return connected
    
    def detect_loops(self) -> List[List[str]]:
        """
        Detect loops (closed paths) in the network.
        Important for identifying parallel paths and bus-tie configurations.
        """
        loops = []
        visited = set()
        path = []
        
        def dfs_cycle(node_id: str, parent: Optional[str] = None):
            visited.add(node_id)
            path.append(node_id)
            
            for neighbor in self.adjacency.get(node_id, []):
                if neighbor not in visited:
                    dfs_cycle(neighbor, node_id)
                elif neighbor != parent and neighbor in path:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    loop = path[cycle_start:] + [neighbor]
                    loops.append(loop)
            
            path.pop()
        
        # Check from each source
        for source_id in self.sources:
            if source_id not in visited:
                dfs_cycle(source_id)
        
        return loops
    
    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """
        Find a path between two nodes using BFS.
        Returns list of node IDs forming the path, or None if no path exists.
        """
        if from_id not in self.nodes or to_id not in self.nodes:
            return None
        
        queue = deque([(from_id, [from_id])])
        visited = set([from_id])
        
        while queue:
            node_id, path = queue.popleft()
            
            if node_id == to_id:
                return path
            
            for neighbor in self.adjacency.get(node_id, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_upstream_nodes(self, node_id: str) -> List[str]:
        """Get all nodes upstream of a given node (towards the source)."""
        if node_id not in self.nodes:
            return []
        
        upstream = []
        queue = deque([node_id])
        visited = set([node_id])
        
        while queue:
            current = queue.popleft()
            
            for parent in self.reverse_adjacency.get(current, []):
                if parent not in visited:
                    visited.add(parent)
                    upstream.append(parent)
                    queue.append(parent)
        
        return upstream
    
    def get_downstream_nodes(self, node_id: str) -> List[str]:
        """Get all nodes downstream of a given node (away from source)."""
        if node_id not in self.nodes:
            return []
        
        downstream = []
        queue = deque([node_id])
        visited = set([node_id])
        
        while queue:
            current = queue.popleft()
            
            for child in self.adjacency.get(current, []):
                if child not in visited:
                    visited.add(child)
                    downstream.append(child)
                    queue.append(child)
        
        return downstream
    
    def calculate_path_impedance(self, path: List[str]) -> complex:
        """
        Calculate total impedance along a path.
        Returns complex impedance (R + jX).
        """
        total_impedance = 0j
        
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Find edge between these nodes
            for edge in self.edges.values():
                if edge.source_id == source and edge.target_id == target:
                    total_impedance += edge.impedance
                    break
        
        return total_impedance
    
    def get_feeder_loads(self, feeder_start_id: str) -> List[str]:
        """
        Get all load nodes fed by a particular feeder.
        Useful for load diversity calculations.
        """
        loads = []
        downstream = self.get_downstream_nodes(feeder_start_id)
        
        for node_id in downstream:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                if node.type in ["Motor", "Load"]:
                    loads.append(node_id)
        
        return loads
    
    def validate_topology(self) -> List[str]:
        """
        Validate the topology for common issues.
        Returns list of warnings/errors.
        """
        issues = []
        
        # Check for dangling nodes (no connections)
        for node_id, node in self.nodes.items():
            if node.type not in ["Source"] and not node.upstream_nodes and not node.downstream_nodes:
                issues.append(f"Warning: Node {node.tag} has no connections")
        
        # Check for unreachable nodes (not connected to any source)
        for node_id, node in self.nodes.items():
            if node.type != "Source" and node.level == -1:
                issues.append(f"Error: Node {node.tag} is not connected to any source")
        
        # Check for multiple sources at different voltage levels without transformers
        if len(self.sources) > 1:
            voltage_levels = [self.nodes[sid].voltage_level for sid in self.sources]
            if len(set(voltage_levels)) > 1:
                issues.append("Warning: Multiple sources at different voltage levels detected")
        
        return issues
    
    def to_dict(self) -> Dict:
        """Export topology to dictionary format for serialization."""
        return {
            "nodes": {
                nid: {
                    "id": node.id,
                    "type": node.type,
                    "tag": node.tag,
                    "voltage_level": node.voltage_level,
                    "level": node.level,
                    "bus_name": node.bus_name,
                    "properties": node.properties
                }
                for nid, node in self.nodes.items()
            },
            "edges": {
                eid: {
                    "id": edge.id,
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "cable_id": edge.cable_id,
                    "impedance_real": edge.impedance.real,
                    "impedance_imag": edge.impedance.imag,
                    "length": edge.length
                }
                for eid, edge in self.edges.items()
            },
            "buses": {
                bus_name: list(nodes)
                for bus_name, nodes in self.buses.items()
            }
        }


def build_topology_from_database(nodes_data: List[Dict], connections_data: List[Dict]) -> TopologyGraph:
    """
    Build topology graph from database query results.
    
    Args:
        nodes_data: List of node records from database
        connections_data: List of connection records from database
    
    Returns:
        TopologyGraph instance
    """
    graph = TopologyGraph()
    
    # Add nodes
    for node_data in nodes_data:
        node = TopologyNode(
            id=str(node_data["id"]),
            type=node_data["type"],
            tag=node_data.get("custom_tag", ""),
            voltage_level=node_data.get("voltage_level", 0.4),
            properties=node_data.get("properties", {})
        )
        graph.add_node(node)
    
    # Add edges
    for conn_data in connections_data:
        edge = TopologyEdge(
            id=str(conn_data["id"]),
            source_id=str(conn_data["source_node_id"]),
            target_id=str(conn_data["target_node_id"]),
            cable_id=str(conn_data.get("cable_library_id", "")),
            length=conn_data.get("length", 0.0)
        )
        
        # Calculate impedance if cable data available
        # This would be populated from the cable library
        
        graph.add_edge(edge)
    
    # Calculate network topology
    graph.calculate_network_levels()
    graph.identify_buses()
    
    return graph


# Example usage and testing
if __name__ == "__main__":
    print("ðŸ”— PwrSysPro Topology Graph Engine Test")
    print("=" * 70)
    
    # Create sample network
    graph = TopologyGraph()
    
    # Add nodes
    nodes = [
        TopologyNode("1", "Source", "SRC-11-01", 11.0),
        TopologyNode("2", "Transformer", "T-11-SRC-MDP-01", 11.0),
        TopologyNode("3", "Bus", "BUS-0.4-MDP-01", 0.4),
        TopologyNode("4", "Cable", "C-0.4-MDP-M1-01", 0.4),
        TopologyNode("5", "Motor", "M-0.4-M1-01", 0.4),
        TopologyNode("6", "Cable", "C-0.4-MDP-M2-01", 0.4),
        TopologyNode("7", "Motor", "M-0.4-M2-01", 0.4),
    ]
    
    for node in nodes:
        graph.add_node(node)
    
    # Add connections
    edges = [
        TopologyEdge("e1", "1", "2", None, 0.05+0.15j),
        TopologyEdge("e2", "2", "3", None, 0.01+0.03j),
        TopologyEdge("e3", "3", "4", "cable1", 0.008+0.004j, 50.0),
        TopologyEdge("e4", "4", "5", None),
        TopologyEdge("e5", "3", "6", "cable2", 0.012+0.006j, 75.0),
        TopologyEdge("e6", "6", "7", None),
    ]
    
    for edge in edges:
        graph.add_edge(edge)
    
    # Test topology analysis
    print("\nðŸ“Š Network Analysis:")
    print("-" * 70)
    
    graph.calculate_network_levels()
    print("Node Levels (distance from source):")
    for nid, node in graph.nodes.items():
        print(f"  {node.tag:30} Level: {node.level}")
    
    print("\nðŸ” Bus Identification:")
    buses = graph.identify_buses()
    for bus_name, node_ids in buses.items():
        print(f"  {bus_name}: {[graph.nodes[nid].tag for nid in node_ids]}")
    
    print("\nðŸ›¤ï¸  Path Finding:")
    path = graph.find_path("1", "5")
    if path:
        path_tags = [graph.nodes[nid].tag for nid in path]
        print(f"  Source to Motor 1: {' â†’ '.join(path_tags)}")
        impedance = graph.calculate_path_impedance(path)
        print(f"  Total Impedance: {impedance.real:.4f} + j{impedance.imag:.4f} Î©")
    
    print("\nâš ï¸  Topology Validation:")
    issues = graph.validate_topology()
    if issues:
        for issue in issues:
            print(f"  â€¢ {issue}")
    else:
        print("  âœ… No issues found")
    
    print("\nâœ… Topology engine test complete!")
