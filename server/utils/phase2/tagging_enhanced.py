"""
PwrSysPro Analysis Suite - Enhanced Auto-Tagging (Phase 2)
Dynamic tag generation based on actual network topology.

Tags now update automatically when:
- Components are connected/disconnected
- Components are moved to different buses
- Network topology changes

Tag Format: [TYPE]-[VOLTAGE]-[FROM_BUS]-[TO_BUS]-[SEQUENCE]
"""

from typing import Optional, Dict, List, Tuple
from utils.tagging import (
    TYPE_CODES, 
    sanitize_bus_name, 
    format_voltage,
    parse_tag as parse_tag_basic
)
from utils.topology import TopologyGraph, TopologyNode


def generate_topology_aware_tag(
    node: TopologyNode,
    graph: TopologyGraph,
    sequence: Optional[int] = None
) -> str:
    """
    Generate tag based on actual network topology.
    
    Args:
        node: The node to generate tag for
        graph: Current topology graph
        sequence: Optional sequence number (auto-assigned if None)
    
    Returns:
        Generated tag string
    """
    # Get type code
    type_code = TYPE_CODES.get(node.type, node.type[:3].upper())
    
    # Format voltage
    voltage_str = format_voltage(node.voltage_level)
    
    # Determine FROM and TO based on topology
    from_bus = None
    to_bus = None
    
    # Get upstream and downstream nodes
    upstream_nodes = node.upstream_nodes
    downstream_nodes = node.downstream_nodes
    
    # FROM bus: First upstream bus or node
    if upstream_nodes:
        upstream_id = upstream_nodes[0]
        if upstream_id in graph.nodes:
            upstream_node = graph.nodes[upstream_id]
            if upstream_node.bus_name:
                from_bus = upstream_node.bus_name
            else:
                from_bus = upstream_node.tag or upstream_node.type
    
    # TO bus: First downstream bus or node (or load name)
    if downstream_nodes:
        downstream_id = downstream_nodes[0]
        if downstream_id in graph.nodes:
            downstream_node = graph.nodes[downstream_id]
            if downstream_node.bus_name:
                to_bus = downstream_node.bus_name
            elif downstream_node.type in ["Motor", "Load"]:
                to_bus = downstream_node.type + str(downstream_id)
            else:
                to_bus = downstream_node.tag or downstream_node.type
    
    # For bus nodes, use the bus name
    if node.type in ["Bus", "Busbar", "Switchgear"]:
        if node.bus_name:
            from_bus = node.bus_name
            to_bus = None
    
    # Determine sequence number
    if sequence is None:
        sequence = _calculate_sequence_number(node, graph)
    
    # Build tag
    tag_parts = [type_code, voltage_str]
    
    if from_bus:
        tag_parts.append(sanitize_bus_name(from_bus))
    
    if to_bus:
        tag_parts.append(sanitize_bus_name(to_bus))
    
    tag_parts.append(f"{sequence:02d}")
    
    return "-".join(tag_parts)


def _calculate_sequence_number(node: TopologyNode, graph: TopologyGraph) -> int:
    """
    Calculate sequence number for parallel components.
    Counts components of same type at same location.
    """
    sequence = 1
    
    # Find similar components
    for other_id, other_node in graph.nodes.items():
        if other_id == node.id:
            continue
        
        if other_node.type == node.type:
            # Check if connected to same buses
            same_upstream = set(node.upstream_nodes) == set(other_node.upstream_nodes)
            same_downstream = set(node.downstream_nodes) == set(other_node.downstream_nodes)
            
            if same_upstream and same_downstream:
                # This is a parallel component
                if other_id < node.id:  # Earlier ID gets lower sequence
                    sequence += 1
    
    return sequence


def update_all_tags(graph: TopologyGraph) -> Dict[str, str]:
    """
    Update tags for all nodes in the topology.
    Returns mapping of node_id -> new_tag.
    
    This should be called after:
    - New connection is created
    - Connection is deleted
    - Node is moved
    - Bus topology changes
    """
    tag_updates = {}
    
    # Ensure topology is analyzed
    graph.calculate_network_levels()
    graph.identify_buses()
    
    # Generate new tags for all nodes
    for node_id, node in graph.nodes.items():
        old_tag = node.tag
        new_tag = generate_topology_aware_tag(node, graph)
        
        if old_tag != new_tag:
            node.tag = new_tag
            tag_updates[node_id] = new_tag
    
    return tag_updates


def get_tag_components(tag: str) -> Dict[str, str]:
    """
    Parse a tag into its components for display.
    
    Returns:
        Dictionary with 'type', 'voltage', 'from_bus', 'to_bus', 'sequence'
    """
    parts = tag.split("-")
    
    result = {
        "type": "",
        "voltage": "",
        "from_bus": "",
        "to_bus": "",
        "sequence": ""
    }
    
    if len(parts) < 3:
        return result
    
    result["type"] = parts[0]
    result["voltage"] = parts[1]
    
    # Last part is sequence if numeric
    if parts[-1].isdigit():
        result["sequence"] = parts[-1]
        remaining = parts[2:-1]
    else:
        remaining = parts[2:]
    
    # Assign bus names
    if len(remaining) >= 1:
        result["from_bus"] = remaining[0]
    if len(remaining) >= 2:
        result["to_bus"] = remaining[1]
    
    return result


def generate_connection_label(
    source_node: TopologyNode,
    target_node: TopologyNode,
    cable_data: Optional[Dict] = None
) -> str:
    """
    Generate a descriptive label for a connection (cable).
    
    Example: "NYY 4x120 - 50m - MDP1 to Motor1"
    """
    label_parts = []
    
    # Cable specification
    if cable_data and "model" in cable_data:
        label_parts.append(cable_data["model"])
    
    # Length
    if cable_data and "length" in cable_data:
        label_parts.append(f"{cable_data['length']:.0f}m")
    
    # Route
    from_name = source_node.bus_name or source_node.tag or source_node.type
    to_name = target_node.bus_name or target_node.tag or target_node.type
    label_parts.append(f"{from_name} â†’ {to_name}")
    
    return " - ".join(label_parts)


def validate_tag_uniqueness(graph: TopologyGraph) -> List[str]:
    """
    Check for duplicate tags in the network.
    Returns list of duplicate tags.
    """
    tag_counts = {}
    duplicates = []
    
    for node in graph.nodes.values():
        if node.tag:
            tag_counts[node.tag] = tag_counts.get(node.tag, 0) + 1
    
    for tag, count in tag_counts.items():
        if count > 1:
            duplicates.append(f"Tag '{tag}' appears {count} times")
    
    return duplicates


def suggest_tag_improvements(node: TopologyNode, graph: TopologyGraph) -> List[str]:
    """
    Suggest improvements to a node's tag based on network context.
    """
    suggestions = []
    
    # Check if node is connected
    if not node.upstream_nodes and not node.downstream_nodes:
        suggestions.append("Node is not connected - tag may need updating after connection")
    
    # Check voltage level consistency
    if node.upstream_nodes:
        upstream_id = node.upstream_nodes[0]
        if upstream_id in graph.nodes:
            upstream_voltage = graph.nodes[upstream_id].voltage_level
            if abs(upstream_voltage - node.voltage_level) > 0.01:
                # Different voltage levels - should have transformer
                has_transformer = False
                for node_check in [node, graph.nodes[upstream_id]]:
                    if node_check.type == "Transformer":
                        has_transformer = True
                
                if not has_transformer:
                    suggestions.append(
                        f"Voltage mismatch: upstream {upstream_voltage}kV vs node {node.voltage_level}kV"
                    )
    
    # Check for missing bus assignment
    if node.type in ["Motor", "Load", "Panel"] and not node.upstream_nodes:
        suggestions.append("Load component should be connected to a bus or panel")
    
    return suggestions


class SmartTagManager:
    """
    Manages intelligent tag generation and updates.
    Tracks history and handles bulk updates.
    """
    
    def __init__(self):
        self.tag_history: Dict[str, List[str]] = {}  # node_id -> list of historical tags
        self.pending_updates: Dict[str, str] = {}    # node_id -> new_tag
    
    def record_tag_change(self, node_id: str, old_tag: str, new_tag: str):
        """Record a tag change for auditing."""
        if node_id not in self.tag_history:
            self.tag_history[node_id] = []
        
        self.tag_history[node_id].append(f"{old_tag} â†’ {new_tag}")
    
    def queue_tag_update(self, node_id: str, new_tag: str):
        """Queue a tag update for batch processing."""
        self.pending_updates[node_id] = new_tag
    
    def get_pending_updates(self) -> Dict[str, str]:
        """Get all queued tag updates."""
        return self.pending_updates.copy()
    
    def clear_pending(self):
        """Clear pending updates after they've been applied."""
        self.pending_updates.clear()
    
    def get_tag_history(self, node_id: str) -> List[str]:
        """Get tag change history for a node."""
        return self.tag_history.get(node_id, [])


def auto_tag_on_connection_change(
    graph: TopologyGraph,
    affected_node_ids: List[str]
) -> Dict[str, str]:
    """
    Automatically update tags for nodes affected by connection changes.
    
    Args:
        graph: Current topology graph
        affected_node_ids: Node IDs that were involved in the change
    
    Returns:
        Dictionary of node_id -> new_tag for nodes that need updating
    """
    # Recalculate topology
    graph.calculate_network_levels()
    graph.identify_buses()
    
    tag_updates = {}
    
    # Update affected nodes and their neighbors
    nodes_to_update = set(affected_node_ids)
    
    for node_id in affected_node_ids:
        if node_id in graph.nodes:
            node = graph.nodes[node_id]
            # Add upstream and downstream neighbors
            nodes_to_update.update(node.upstream_nodes)
            nodes_to_update.update(node.downstream_nodes)
    
    # Generate new tags
    for node_id in nodes_to_update:
        if node_id in graph.nodes:
            node = graph.nodes[node_id]
            new_tag = generate_topology_aware_tag(node, graph)
            
            if new_tag != node.tag:
                tag_updates[node_id] = new_tag
                node.tag = new_tag
    
    return tag_updates


# Example usage
if __name__ == "__main__":
    print("ðŸ·ï¸  Enhanced Auto-Tagging Test (Phase 2)")
    print("=" * 70)
    
    from utils.topology import TopologyGraph, TopologyNode, TopologyEdge
    
    # Create test network
    graph = TopologyGraph()
    
    # Add nodes
    n1 = TopologyNode("1", "Source", "", 11.0)
    n2 = TopologyNode("2", "Transformer", "", 11.0)
    n3 = TopologyNode("3", "Bus", "", 0.4)
    n4 = TopologyNode("4", "Cable", "", 0.4)
    n5 = TopologyNode("5", "Motor", "", 0.4)
    
    for node in [n1, n2, n3, n4, n5]:
        graph.add_node(node)
    
    # Add connections
    graph.add_edge(TopologyEdge("e1", "1", "2", None))
    graph.add_edge(TopologyEdge("e2", "2", "3", None))
    graph.add_edge(TopologyEdge("e3", "3", "4", "cable1", length=50.0))
    graph.add_edge(TopologyEdge("e4", "4", "5", None))
    
    # Test tag generation
    print("\nðŸ” Generating Topology-Aware Tags:")
    print("-" * 70)
    
    tag_updates = update_all_tags(graph)
    
    for node_id, node in graph.nodes.items():
        components = get_tag_components(node.tag)
        print(f"Node {node_id} ({node.type:12}): {node.tag}")
        print(f"  Level: {node.level}, Bus: {node.bus_name or 'N/A'}")
        if node_id in tag_updates:
            print(f"  âœ¨ Tag updated!")
    
    print("\nâœ… Enhanced auto-tagging test complete!")
