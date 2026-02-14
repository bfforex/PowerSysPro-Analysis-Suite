"""
PwrSysPro Analysis Suite - R&X Diagram Generator
Generates Resistance vs. Reactance impedance diagrams for protection coordination.

Standards Reference:
- IEEE C37.113: Guide for Protective Relay Applications to Transmission Lines
- IEEE 242 (Buff Book): Protection and Coordination

Purpose:
- Visualize component impedances on R-X plane
- Aid in protection relay coordination
- Show impedance locus for system components
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import io
import base64


@dataclass
class ImpedancePoint:
    """Single impedance point for R-X diagram"""
    tag: str
    resistance: float  # Ohms or per-unit
    reactance: float   # Ohms or per-unit
    component_type: str
    voltage_level: float = 0.0
    color: str = None
    marker: str = 'o'


class RXDiagramGenerator:
    """
    Generate Resistance vs. Reactance (R-X) impedance diagrams.
    
    Used for:
    - Component impedance visualization
    - Protection relay coordination
    - System impedance analysis
    - Fault location studies
    """
    
    def __init__(self, system_voltage: float, base_mva: float = 100.0):
        """
        Initialize R-X diagram generator.
        
        Args:
            system_voltage: System voltage in kV
            base_mva: Base MVA for per-unit calculations
        """
        self.voltage = system_voltage
        self.base_mva = base_mva
        self.components: List[ImpedancePoint] = []
        
        # Color scheme for different component types
        self.type_colors = {
            'Source': '#ef4444',      # Red
            'Transformer': '#3b82f6', # Blue
            'Cable': '#10b981',       # Green
            'Motor': '#f59e0b',       # Yellow/Orange
            'Generator': '#8b5cf6',   # Purple
            'Bus': '#6b7280',         # Gray
            'Load': '#ec4899'         # Pink
        }
        
        # Marker styles
        self.type_markers = {
            'Source': 's',         # Square
            'Transformer': '^',    # Triangle up
            'Cable': 'o',          # Circle
            'Motor': 'v',          # Triangle down
            'Generator': 'D',      # Diamond
            'Bus': 'p',            # Pentagon
            'Load': '*'            # Star
        }
    
    def add_component(
        self,
        tag: str,
        resistance: float,
        reactance: float,
        component_type: str,
        voltage_level: float = 0.0
    ):
        """
        Add component impedance to diagram.
        
        Args:
            tag: Component identifier
            resistance: R in ohms or pu
            reactance: X in ohms or pu
            component_type: Type of component
            voltage_level: Voltage level in kV
        """
        color = self.type_colors.get(component_type, '#6b7280')
        marker = self.type_markers.get(component_type, 'o')
        
        point = ImpedancePoint(
            tag=tag,
            resistance=resistance,
            reactance=reactance,
            component_type=component_type,
            voltage_level=voltage_level,
            color=color,
            marker=marker
        )
        
        self.components.append(point)
    
    def generate_diagram(
        self,
        title: str = "R-X Impedance Diagram",
        show_grid: bool = True,
        show_impedance_circles: bool = True,
        show_angle_lines: bool = True,
        unit: str = "pu"  # "pu" or "ohms"
    ) -> Tuple[plt.Figure, Dict]:
        """
        Generate R-X diagram with all components.
        
        Args:
            title: Diagram title
            show_grid: Show grid lines
            show_impedance_circles: Show constant impedance circles
            show_angle_lines: Show constant angle lines
            unit: Unit for axes ("pu" or "ohms")
        
        Returns:
            (matplotlib figure, plot data dictionary)
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot each component
        for comp in self.components:
            ax.scatter(
                comp.resistance,
                comp.reactance,
                s=150,
                c=comp.color,
                marker=comp.marker,
                label=f"{comp.tag} ({comp.component_type})",
                edgecolors='black',
                linewidths=1.5,
                alpha=0.8,
                zorder=3
            )
            
            # Add label
            ax.annotate(
                comp.tag,
                (comp.resistance, comp.reactance),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7)
            )
        
        # Add impedance circles if requested
        if show_impedance_circles and self.components:
            self._add_impedance_circles(ax)
        
        # Add angle lines if requested
        if show_angle_lines:
            self._add_angle_lines(ax)
        
        # Formatting
        ax.set_xlabel(f'Resistance ({unit})', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Reactance ({unit})', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Legend
        if self.components:
            ax.legend(
                loc='upper right',
                fontsize=9,
                framealpha=0.9,
                edgecolor='black'
            )
        
        # Equal aspect ratio
        ax.set_aspect('equal', adjustable='box')
        
        # Set limits with padding
        if self.components:
            all_r = [c.resistance for c in self.components]
            all_x = [c.reactance for c in self.components]
            
            r_min, r_max = min(all_r), max(all_r)
            x_min, x_max = min(all_x), max(all_x)
            
            r_range = r_max - r_min
            x_range = x_max - x_min
            
            padding = 0.2
            ax.set_xlim(r_min - padding * r_range, r_max + padding * r_range)
            ax.set_ylim(x_min - padding * x_range, x_max + padding * x_range)
        
        plt.tight_layout()
        
        # Generate plot data for frontend
        plot_data = self._generate_plot_data()
        
        return fig, plot_data
    
    def _add_impedance_circles(self, ax):
        """Add constant impedance magnitude circles"""
        if not self.components:
            return
        
        # Calculate max impedance
        max_z = max(
            np.sqrt(c.resistance**2 + c.reactance**2)
            for c in self.components
        )
        
        # Draw circles at 25%, 50%, 75%, 100% of max
        for percent in [0.25, 0.5, 0.75, 1.0]:
            radius = max_z * percent
            circle = Circle(
                (0, 0),
                radius,
                fill=False,
                edgecolor='gray',
                linestyle=':',
                linewidth=1,
                alpha=0.5,
                zorder=1
            )
            ax.add_patch(circle)
            
            # Label
            ax.text(
                radius * 0.707,  # 45 degrees
                radius * 0.707,
                f'{percent*100:.0f}%',
                fontsize=8,
                color='gray',
                alpha=0.7
            )
    
    def _add_angle_lines(self, ax):
        """Add constant angle lines (X/R ratio)"""
        # Common angles for transmission lines and cables
        angles_deg = [30, 45, 60, 75, 85]  # degrees
        
        if not self.components:
            return
        
        max_r = max(c.resistance for c in self.components) * 1.2
        
        for angle in angles_deg:
            angle_rad = np.deg2rad(angle)
            slope = np.tan(angle_rad)
            
            r_line = np.array([0, max_r])
            x_line = r_line * slope
            
            ax.plot(
                r_line,
                x_line,
                color='lightblue',
                linestyle='--',
                linewidth=0.8,
                alpha=0.6,
                zorder=1
            )
            
            # Label
            ax.text(
                max_r * 0.9,
                max_r * slope * 0.9,
                f'{angle}°',
                fontsize=8,
                color='blue',
                alpha=0.7
            )
    
    def _generate_plot_data(self) -> Dict:
        """Generate data structure for frontend plotting"""
        return {
            'components': [
                {
                    'tag': c.tag,
                    'r': c.resistance,
                    'x': c.reactance,
                    'z': np.sqrt(c.resistance**2 + c.reactance**2),
                    'angle': np.rad2deg(np.arctan2(c.reactance, c.resistance)),
                    'type': c.component_type,
                    'color': c.color,
                    'marker': c.marker
                }
                for c in self.components
            ],
            'axes': {
                'x_label': 'Resistance',
                'y_label': 'Reactance',
                'title': 'R-X Impedance Diagram'
            },
            'statistics': self._calculate_statistics()
        }
    
    def _calculate_statistics(self) -> Dict:
        """Calculate impedance statistics"""
        if not self.components:
            return {}
        
        impedances = [
            np.sqrt(c.resistance**2 + c.reactance**2)
            for c in self.components
        ]
        
        x_r_ratios = [
            c.reactance / c.resistance if c.resistance != 0 else float('inf')
            for c in self.components
        ]
        
        return {
            'total_components': len(self.components),
            'max_impedance': max(impedances),
            'min_impedance': min(impedances),
            'avg_impedance': np.mean(impedances),
            'avg_x_r_ratio': np.mean([r for r in x_r_ratios if r != float('inf')])
        }
    
    def export_to_png(self, filename: str = None) -> bytes:
        """
        Export diagram to PNG image.
        
        Args:
            filename: Optional filename to save to disk
        
        Returns:
            PNG image as bytes
        """
        fig, _ = self.generate_diagram()
        
        # Save to BytesIO
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        
        # Optionally save to file
        if filename:
            with open(filename, 'wb') as f:
                f.write(buf.getvalue())
            buf.seek(0)
        
        plt.close(fig)
        
        return buf.getvalue()
    
    def export_to_svg(self, filename: str = None) -> str:
        """
        Export diagram to SVG.
        
        Args:
            filename: Optional filename to save to disk
        
        Returns:
            SVG as string
        """
        fig, _ = self.generate_diagram()
        
        buf = io.BytesIO()
        fig.savefig(buf, format='svg', bbox_inches='tight')
        buf.seek(0)
        
        svg_str = buf.getvalue().decode('utf-8')
        
        if filename:
            with open(filename, 'w') as f:
                f.write(svg_str)
        
        plt.close(fig)
        
        return svg_str
    
    def export_to_base64(self) -> str:
        """
        Export diagram to base64-encoded PNG for web display.
        
        Returns:
            Base64-encoded PNG string
        """
        png_bytes = self.export_to_png()
        return base64.b64encode(png_bytes).decode('utf-8')
    
    def clear_components(self):
        """Clear all components from diagram"""
        self.components = []


def generate_rx_diagram_from_project(
    project_data: Dict,
    component_data: Dict
) -> Tuple[bytes, Dict]:
    """
    Generate R-X diagram from project data.
    
    Args:
        project_data: Project information
        component_data: Component library data
    
    Returns:
        (PNG bytes, plot data dictionary)
    """
    # Extract system parameters
    base_mva = project_data.get('base_mva', 100.0)
    voltage_kv = 11.0  # Default, should extract from project
    
    # Create generator
    generator = RXDiagramGenerator(voltage_kv, base_mva)
    
    # Add components
    for node in project_data.get('nodes', []):
        node_type = node.get('type', 'Unknown')
        
        # Get impedance from component library
        comp_id = str(node.get('component_library_id', ''))
        comp_data = component_data.get(comp_id, {})
        
        r = comp_data.get('impedance_r', 0.0)
        x = comp_data.get('impedance_x', 0.0)
        
        if r != 0 or x != 0:  # Only add if has impedance
            generator.add_component(
                tag=node.get('custom_tag', f"{node_type}-{node['id']}"),
                resistance=r,
                reactance=x,
                component_type=node_type
            )
    
    # Generate diagram
    fig, plot_data = generator.generate_diagram(
        title=f"R-X Impedance Diagram - {project_data.get('name', 'Project')}"
    )
    
    # Export to PNG
    png_bytes = generator.export_to_png()
    
    plt.close(fig)
    
    return png_bytes, plot_data


# Example usage and testing
if __name__ == "__main__":
    print("📊 R-X Diagram Generator Test")
    print("=" * 70)
    
    # Create test diagram
    generator = RXDiagramGenerator(system_voltage=11.0, base_mva=100.0)
    
    # Add test components
    generator.add_component("SOURCE-01", 0.05, 0.15, "Source")
    generator.add_component("XFMR-01", 0.02, 0.10, "Transformer")
    generator.add_component("CABLE-01", 0.08, 0.06, "Cable")
    generator.add_component("MOTOR-01", 0.12, 0.25, "Motor")
    generator.add_component("GEN-01", 0.03, 0.20, "Generator")
    
    print(f"\n✅ Added {len(generator.components)} components")
    
    # Generate diagram
    fig, plot_data = generator.generate_diagram()
    
    print(f"\n📈 Diagram Statistics:")
    stats = plot_data['statistics']
    print(f"  Total Components: {stats['total_components']}")
    print(f"  Max Impedance: {stats['max_impedance']:.3f} pu")
    print(f"  Min Impedance: {stats['min_impedance']:.3f} pu")
    print(f"  Avg X/R Ratio: {stats['avg_x_r_ratio']:.2f}")
    
    # Test export
    png_bytes = generator.export_to_png('/tmp/test_rx_diagram.png')
    print(f"\n✅ Exported PNG: {len(png_bytes)} bytes")
    
    base64_str = generator.export_to_base64()
    print(f"✅ Base64 encoded: {len(base64_str)} characters")
    
    plt.close(fig)
    
    print("\n✅ R-X Diagram Generator test complete!")
