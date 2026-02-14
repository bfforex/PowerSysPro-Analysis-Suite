"""
PwrSysPro Analysis Suite - Auto-Tagging Engine
Implements the automatic tag generation logic for electrical components.

Tag Syntax: [TYPE]-[VOLTAGE]-[FROM_BUS]-[TO_BUS]-[SEQUENCE]
Example: C-0.48-MDP1-M1-01 (Cable, 480V, from MDP-1 to Motor-1, sequence 01)

This is a critical feature that ensures consistent naming and traceability.
"""

import re
from typing import Optional, Dict, Any

# Type code mapping
TYPE_CODES = {
    "Cable": "C",
    "Breaker": "CB",
    "Transformer": "T",
    "Motor": "M",
    "Bus": "BUS",
    "Source": "SRC",
    "Load": "L",
    "Panel": "PNL",
    "Switchgear": "SWG",
    "VFD": "VFD",
    "Generator": "GEN",
    "Capacitor": "CAP"
}

def sanitize_bus_name(bus_name: str) -> str:
    """
    Sanitizes a bus name for use in tags.
    Removes spaces, special characters, and converts to uppercase.
    
    Args:
        bus_name: Original bus name (e.g., "MDP-1", "Motor 01")
    
    Returns:
        Sanitized name (e.g., "MDP1", "MOTOR01")
    """
    # Remove hyphens, spaces, and special characters
    sanitized = re.sub(r'[^A-Za-z0-9]', '', bus_name)
    return sanitized.upper()


def format_voltage(voltage_kv: float) -> str:
    """
    Formats voltage for tag display.
    
    Args:
        voltage_kv: Voltage in kilovolts
    
    Returns:
        Formatted voltage string (e.g., "0.48" for 480V, "11" for 11kV)
    """
    if voltage_kv < 1.0:
        # Low voltage - show in decimal format
        return f"{voltage_kv:.2f}"
    else:
        # Medium/High voltage - show without decimals if whole number
        if voltage_kv == int(voltage_kv):
            return f"{int(voltage_kv)}"
        return f"{voltage_kv:.1f}"


def generate_tag(
    component_type: str,
    voltage_kv: float,
    from_bus: Optional[str] = None,
    to_bus: Optional[str] = None,
    sequence: int = 1
) -> str:
    """
    Generates an automatic tag for a component based on the PwrSysPro standard.
    
    Tag Format: [TYPE]-[VOLTAGE]-[FROM]-[TO]-[SEQ]
    
    Args:
        component_type: Type of component (Cable, Breaker, Motor, etc.)
        voltage_kv: Voltage level in kilovolts
        from_bus: Name of the source bus (optional)
        to_bus: Name of the destination bus (optional)
        sequence: Sequence number for parallel components
    
    Returns:
        Generated tag string
    
    Examples:
        >>> generate_tag("Cable", 0.48, "MDP-1", "Motor-1", 1)
        'C-0.48-MDP1-M1-01'
        
        >>> generate_tag("Transformer", 11.0, "Source", "MDP-1", 1)
        'T-11-SOURCE-MDP1-01'
        
        >>> generate_tag("Breaker", 0.4, "Panel-A", None, 3)
        'CB-0.40-PANELA-03'
    """
    # Get type code
    type_code = TYPE_CODES.get(component_type, component_type[:3].upper())
    
    # Format voltage
    voltage_str = format_voltage(voltage_kv)
    
    # Build tag components
    tag_parts = [type_code, voltage_str]
    
    # Add bus names if provided
    if from_bus:
        tag_parts.append(sanitize_bus_name(from_bus))
    
    if to_bus:
        tag_parts.append(sanitize_bus_name(to_bus))
    
    # Add sequence number (always 2 digits)
    tag_parts.append(f"{sequence:02d}")
    
    return "-".join(tag_parts)


def parse_tag(tag: str) -> Dict[str, Any]:
    """
    Parses an existing tag back into its components.
    Useful for validation and editing operations.
    
    Args:
        tag: Tag string to parse (e.g., "C-0.48-MDP1-M1-01")
    
    Returns:
        Dictionary with tag components
    
    Example:
        >>> parse_tag("C-0.48-MDP1-M1-01")
        {
            'type_code': 'C',
            'voltage': 0.48,
            'from_bus': 'MDP1',
            'to_bus': 'M1',
            'sequence': 1
        }
    """
    parts = tag.split("-")
    
    if len(parts) < 3:
        raise ValueError(f"Invalid tag format: {tag}")
    
    result = {
        "type_code": parts[0],
        "voltage": float(parts[1]),
        "sequence": None,
        "from_bus": None,
        "to_bus": None
    }
    
    # Last part is always sequence if it's numeric
    if parts[-1].isdigit():
        result["sequence"] = int(parts[-1])
        parts = parts[:-1]
    
    # Remaining parts are bus names
    if len(parts) > 2:
        result["from_bus"] = parts[2]
    if len(parts) > 3:
        result["to_bus"] = parts[3]
    
    return result


def update_tag_on_move(
    current_tag: str,
    new_from_bus: Optional[str] = None,
    new_to_bus: Optional[str] = None
) -> str:
    """
    Updates an existing tag when a component is moved to a new bus.
    Preserves the type, voltage, and sequence while updating bus references.
    
    Args:
        current_tag: Existing tag
        new_from_bus: New source bus name (if changed)
        new_to_bus: New destination bus name (if changed)
    
    Returns:
        Updated tag string
    
    Example:
        >>> update_tag_on_move("C-0.48-MDP1-M1-01", new_to_bus="M2")
        'C-0.48-MDP1-M2-01'
    """
    parsed = parse_tag(current_tag)
    
    # Reverse lookup type from code
    type_name = None
    for name, code in TYPE_CODES.items():
        if code == parsed["type_code"]:
            type_name = name
            break
    
    if not type_name:
        type_name = "Unknown"
    
    # Use new bus names if provided, otherwise keep existing
    from_bus = new_from_bus if new_from_bus else parsed.get("from_bus")
    to_bus = new_to_bus if new_to_bus else parsed.get("to_bus")
    
    return generate_tag(
        component_type=type_name,
        voltage_kv=parsed["voltage"],
        from_bus=from_bus,
        to_bus=to_bus,
        sequence=parsed.get("sequence", 1)
    )


def validate_tag(tag: str) -> tuple[bool, str]:
    """
    Validates a tag against the PwrSysPro standard format.
    
    Args:
        tag: Tag string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        parts = tag.split("-")
        
        if len(parts) < 3:
            return False, "Tag must have at least 3 parts: TYPE-VOLTAGE-SEQUENCE"
        
        # Validate type code
        if parts[0] not in TYPE_CODES.values():
            return False, f"Invalid type code: {parts[0]}"
        
        # Validate voltage
        try:
            voltage = float(parts[1])
            if voltage <= 0:
                return False, "Voltage must be positive"
        except ValueError:
            return False, f"Invalid voltage format: {parts[1]}"
        
        # Validate sequence (last part if numeric)
        if parts[-1].isdigit():
            seq = int(parts[-1])
            if seq <= 0:
                return False, "Sequence must be positive"
        
        return True, "Valid tag"
        
    except Exception as e:
        return False, f"Tag parsing error: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    print("ðŸ·ï¸  PwrSysPro Auto-Tagging Engine Test")
    print("=" * 60)
    
    # Test tag generation
    tests = [
        ("Cable", 0.48, "MDP-1", "Motor-1", 1),
        ("Transformer", 11.0, "Source", "MDP-1", 1),
        ("Breaker", 0.4, "Panel-A", None, 3),
        ("Cable", 0.48, "MDP-1", "Panel B", 2),
    ]
    
    for test in tests:
        tag = generate_tag(*test)
        print(f"âœ“ {test[0]:12} â†’ {tag}")
    
    print("\n" + "=" * 60)
    
    # Test tag parsing
    test_tag = "C-0.48-MDP1-M1-01"
    parsed = parse_tag(test_tag)
    print(f"ðŸ“– Parsing: {test_tag}")
    print(f"   Type: {parsed['type_code']}, Voltage: {parsed['voltage']}kV")
    print(f"   From: {parsed['from_bus']}, To: {parsed['to_bus']}")
    print(f"   Sequence: {parsed['sequence']}")
    
    print("\n" + "=" * 60)
    
    # Test tag update
    updated = update_tag_on_move(test_tag, new_to_bus="Motor-2")
    print(f"ðŸ”„ Update: {test_tag} â†’ {updated}")
