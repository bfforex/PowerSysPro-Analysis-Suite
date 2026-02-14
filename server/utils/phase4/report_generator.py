"""
PwrSysPro Analysis Suite - PDF Report Generator (Phase 4)
Professional report generation with calculations, diagrams, and tables.

Reports include:
- Project information and design basis
- Single line diagram
- Calculation results (voltage drop, short circuit, load flow)
- Arc flash analysis
- Equipment schedules
- Compliance statements
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, List, Optional
import os


class PwrSysProReportGenerator:
    """
    Professional PDF report generator for electrical engineering analysis.
    """
    
    def __init__(self, output_path: str, pagesize=letter):
        """
        Initialize report generator.
        
        Args:
            output_path: Path for output PDF file
            pagesize: Page size (letter or A4)
        """
        self.output_path = output_path
        self.pagesize = pagesize
        self.width, self.height = pagesize
        
        # Create document
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=pagesize,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1.0*inch,
            bottomMargin=0.75*inch
        )
        
        # Story (content) list
        self.story = []
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceBefore=20,
            spaceAfter=12,
            borderWidth=0,
            borderColor=colors.HexColor('#1e40af'),
            borderPadding=5,
            borderRadius=2
        ))
        
        # Subsection
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceBefore=15,
            spaceAfter=8
        ))
        
        # Table header
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))
    
    def add_cover_page(self, project_data: Dict):
        """
        Add professional cover page.
        
        Args:
            project_data: Dictionary with project information
        """
        # Logo/Title
        title = Paragraph(
            "âš¡ PwrSysPro Analysis Suite",
            self.styles['ReportTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Project name
        project_name = Paragraph(
            f"<b>{project_data.get('name', 'Electrical System Analysis')}</b>",
            ParagraphStyle(
                name='ProjectName',
                parent=self.styles['Heading1'],
                fontSize=20,
                alignment=TA_CENTER,
                spaceAfter=30
            )
        )
        self.story.append(project_name)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Report type
        report_type = Paragraph(
            "Power System Analysis Report",
            ParagraphStyle(
                name='ReportType',
                parent=self.styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#6b7280')
            )
        )
        self.story.append(report_type)
        self.story.append(Spacer(1, 1.0*inch))
        
        # Project details table
        details = [
            ['Project Information', ''],
            ['Project Number:', project_data.get('project_number', 'N/A')],
            ['Location:', project_data.get('location', 'N/A')],
            ['Prepared By:', project_data.get('engineer', 'PwrSysPro User')],
            ['Date:', datetime.now().strftime('%B %d, %Y')],
            ['Revision:', project_data.get('revision', 'Rev 0')],
        ]
        
        t = Table(details, colWidths=[2.5*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        self.story.append(t)
        self.story.append(Spacer(1, 1.0*inch))
        
        # Standards compliance
        standards = Paragraph(
            "<b>Standards Compliance:</b><br/>"
            "â€¢ IEC 60909: Short-Circuit Current Calculation<br/>"
            "â€¢ IEC 60364-5-52: Cable Selection and Installation<br/>"
            "â€¢ IEEE 1584: Arc Flash Hazard Calculation<br/>"
            "â€¢ IEEE Std 399: Power System Analysis<br/>"
            "â€¢ NFPA 70E: Electrical Safety in the Workplace",
            self.styles['Normal']
        )
        self.story.append(standards)
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self, summary_data: Dict):
        """Add executive summary section."""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Overall status
        status = summary_data.get('overall_status', 'UNKNOWN')
        status_color = {
            'PASS': colors.HexColor('#10b981'),
            'WARNING': colors.HexColor('#f59e0b'),
            'FAIL': colors.HexColor('#ef4444')
        }.get(status, colors.grey)
        
        status_text = Paragraph(
            f"<b>Overall System Status:</b> "
            f"<font color='{status_color.hexval()}' size='14'><b>{status}</b></font>",
            self.styles['Normal']
        )
        self.story.append(status_text)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Key findings
        findings = [
            f"<b>Total Components Analyzed:</b> {summary_data.get('total_components', 0)}",
            f"<b>Maximum Fault Current:</b> {summary_data.get('max_fault_current', 0)} kA",
            f"<b>Critical Bus:</b> {summary_data.get('critical_bus', 'N/A')}",
            f"<b>System Losses:</b> {summary_data.get('total_losses', 0)} MW ({summary_data.get('loss_percent', 0)}%)",
            f"<b>Breaker Validation:</b> {summary_data.get('breakers_pass', 0)} Pass, {summary_data.get('breakers_fail', 0)} Fail",
        ]
        
        for finding in findings:
            self.story.append(Paragraph(finding, self.styles['Normal']))
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(PageBreak())
    
    def add_design_basis(self, design_data: Dict):
        """Add design basis and assumptions section."""
        self.story.append(Paragraph("Design Basis", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        basis_text = f"""
        <b>System Parameters:</b><br/>
        â€¢ Base MVA: {design_data.get('base_mva', 100)} MVA<br/>
        â€¢ System Frequency: {design_data.get('frequency', 50)} Hz<br/>
        â€¢ Primary Voltage: {design_data.get('primary_voltage', 11)} kV<br/>
        â€¢ Secondary Voltage: {design_data.get('secondary_voltage', 0.4)} kV<br/>
        <br/>
        <b>Analysis Methods:</b><br/>
        â€¢ Short Circuit: IEC 60909 with motor contribution<br/>
        â€¢ Load Flow: Newton-Raphson iterative method<br/>
        â€¢ Voltage Drop: Per IEC 60364-5-52<br/>
        â€¢ Arc Flash: IEEE 1584-2018<br/>
        <br/>
        <b>Assumptions:</b><br/>
        â€¢ System grounding: Solidly grounded<br/>
        â€¢ Voltage factor (c): 1.1 for maximum fault current<br/>
        â€¢ Ambient temperature: 30Â°C<br/>
        â€¢ Cable installation: As per IEC 60364-5-52 Method E<br/>
        """
        
        self.story.append(Paragraph(basis_text, self.styles['Normal']))
        self.story.append(PageBreak())
    
    def add_short_circuit_results(self, results: Dict):
        """Add short circuit analysis results."""
        self.story.append(Paragraph("Short Circuit Analysis", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Summary text
        summary = Paragraph(
            f"Short circuit analysis performed per IEC 60909-0. "
            f"Maximum fault current of <b>{results.get('max_fault', 0)} kA</b> "
            f"occurs at bus <b>{results.get('max_fault_bus', 'N/A')}</b>.",
            self.styles['Normal']
        )
        self.story.append(summary)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Results table
        if 'bus_results' in results:
            table_data = [['Bus', 'I"k3 (kA)', 'ip (kA)', 'Ib (kA)', 'Sk (MVA)']]
            
            for bus_id, data in results['bus_results'].items():
                table_data.append([
                    data.get('tag', bus_id),
                    f"{data.get('i_k3', 0):.2f}",
                    f"{data.get('ip', 0):.2f}",
                    f"{data.get('ib', 0):.2f}",
                    f"{data.get('sk', 0):.2f}"
                ])
            
            t = Table(table_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            
            self.story.append(t)
        
        self.story.append(PageBreak())
    
    def add_arc_flash_results(self, results: Dict):
        """Add arc flash analysis results."""
        self.story.append(Paragraph("Arc Flash Analysis", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Introduction
        intro = Paragraph(
            "Arc flash analysis performed per IEEE 1584-2018 and NFPA 70E. "
            "Results indicate required Personal Protective Equipment (PPE) for safe work.",
            self.styles['Normal']
        )
        self.story.append(intro)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Results table
        if 'bus_results' in results:
            table_data = [[
                'Bus', 'IE (cal/cmÂ²)', 'AFB (ft)', 
                'PPE Cat', 'Hazard Level'
            ]]
            
            for bus_id, data in results['bus_results'].items():
                table_data.append([
                    data.get('tag', bus_id),
                    f"{data.get('incident_energy', 0):.2f}",
                    f"{data.get('afb_ft', 0):.2f}",
                    data.get('ppe_category', 'N/A'),
                    data.get('hazard_level', 'N/A')
                ])
            
            t = Table(table_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')])
            ]))
            
            self.story.append(t)
        
        self.story.append(Spacer(1, 0.2*inch))
        
        # Safety note
        safety_note = Paragraph(
            "<b>âš ï¸  Safety Notice:</b> All personnel must wear appropriate PPE "
            "as indicated above when working on energized equipment. "
            "Consider de-energizing equipment when incident energy exceeds 40 cal/cmÂ².",
            ParagraphStyle(
                name='SafetyNote',
                parent=self.styles['Normal'],
                backColor=colors.HexColor('#fef2f2'),
                borderColor=colors.HexColor('#dc2626'),
                borderWidth=1,
                borderPadding=10,
                borderRadius=3
            )
        )
        self.story.append(safety_note)
        
        self.story.append(PageBreak())
    
    def add_load_flow_results(self, results: Dict):
        """Add load flow analysis results."""
        self.story.append(Paragraph("Load Flow Analysis", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Summary
        if results.get('converged'):
            summary = Paragraph(
                f"Load flow converged in <b>{results.get('iterations', 0)} iterations</b>. "
                f"Total system losses: <b>{results.get('total_losses', 0)} MW</b> "
                f"({results.get('loss_percent', 0)}%).",
                self.styles['Normal']
            )
        else:
            summary = Paragraph(
                "<font color='red'><b>WARNING:</b> Load flow did not converge. "
                "Review network topology and loading conditions.</font>",
                self.styles['Normal']
            )
        
        self.story.append(summary)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Bus voltage table
        if 'bus_voltages' in results:
            table_data = [['Bus', 'V (pu)', 'Î¸ (deg)', 'P (MW)', 'Q (MVAR)', 'Status']]
            
            for bus_id, data in results['bus_voltages'].items():
                v_pu = data.get('v_magnitude', 1.0)
                status = 'âœ“' if 0.95 <= v_pu <= 1.05 else 'âš '
                
                table_data.append([
                    data.get('tag', bus_id),
                    f"{v_pu:.4f}",
                    f"{data.get('v_angle', 0):.2f}",
                    f"{data.get('p_mw', 0):.3f}",
                    f"{data.get('q_mvar', 0):.3f}",
                    status
                ])
            
            t = Table(table_data, colWidths=[1.8*inch, 1*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')])
            ]))
            
            self.story.append(t)
        
        self.story.append(PageBreak())
    
    def add_equipment_schedule(self, equipment: List[Dict]):
        """Add equipment schedule/list."""
        self.story.append(Paragraph("Equipment Schedule", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Group by type
        breakers = [e for e in equipment if e.get('type') == 'Breaker']
        transformers = [e for e in equipment if e.get('type') == 'Transformer']
        cables = [e for e in equipment if e.get('type') == 'Cable']
        
        # Breakers
        if breakers:
            self.story.append(Paragraph("Circuit Breakers", self.styles['SubsectionHeading']))
            table_data = [['Tag', 'Rating (A)', 'SC Rating (kA)', 'Manufacturer', 'Model']]
            
            for br in breakers:
                table_data.append([
                    br.get('tag', ''),
                    str(br.get('rating', '')),
                    str(br.get('sc_rating', '')),
                    br.get('manufacturer', ''),
                    br.get('model', '')
                ])
            
            t = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.3*inch, 1.5*inch, 1.5*inch])
            self._apply_table_style(t)
            self.story.append(t)
            self.story.append(Spacer(1, 0.2*inch))
        
        # Add similar tables for transformers and cables...
        
        self.story.append(PageBreak())
    
    def _apply_table_style(self, table):
        """Apply standard table styling."""
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
    
    def add_conclusion(self, conclusion_text: str):
        """Add conclusion section."""
        self.story.append(Paragraph("Conclusion", self.styles['SectionHeading']))
        self.story.append(Spacer(1, 0.2*inch))
        
        conclusion = Paragraph(conclusion_text, self.styles['Normal'])
        self.story.append(conclusion)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Signature block
        signature = Paragraph(
            "<br/><br/>_______________________________<br/>"
            "Professional Engineer<br/>"
            f"Date: {datetime.now().strftime('%B %d, %Y')}<br/>",
            self.styles['Normal']
        )
        self.story.append(signature)
    
    def generate(self) -> str:
        """
        Generate the PDF report.
        
        Returns:
            Path to generated PDF file
        """
        # Build PDF
        self.doc.build(self.story)
        return self.output_path


# Simplified function for quick report generation
def generate_analysis_report(
    output_path: str,
    project_data: Dict,
    analysis_results: Dict
) -> str:
    """
    Generate complete analysis report.
    
    Args:
        output_path: Path for output PDF
        project_data: Project information
        analysis_results: All analysis results
    
    Returns:
        Path to generated report
    """
    report = PwrSysProReportGenerator(output_path)
    
    # Add sections
    report.add_cover_page(project_data)
    
    if 'summary' in analysis_results:
        report.add_executive_summary(analysis_results['summary'])
    
    if 'design_basis' in analysis_results:
        report.add_design_basis(analysis_results['design_basis'])
    
    if 'short_circuit' in analysis_results:
        report.add_short_circuit_results(analysis_results['short_circuit'])
    
    if 'arc_flash' in analysis_results:
        report.add_arc_flash_results(analysis_results['arc_flash'])
    
    if 'load_flow' in analysis_results:
        report.add_load_flow_results(analysis_results['load_flow'])
    
    if 'equipment' in analysis_results:
        report.add_equipment_schedule(analysis_results['equipment'])
    
    conclusion = analysis_results.get('conclusion', 
        "The electrical system analysis has been completed per applicable standards. "
        "All results are documented in this report for design verification and safety compliance.")
    report.add_conclusion(conclusion)
    
    # Generate
    return report.generate()


# Test
if __name__ == "__main__":
    print("ðŸ“„ PDF Report Generator Test")
    print("=" * 70)
    
    test_data = {
        'project': {
            'name': 'Industrial Facility Electrical Distribution',
            'project_number': 'PWR-2026-001',
            'location': 'Sample Location',
            'engineer': 'Test Engineer',
            'revision': 'Rev 0'
        },
        'summary': {
            'overall_status': 'PASS',
            'total_components': 25,
            'max_fault_current': 18.45,
            'critical_bus': 'BUS-MDP-01',
            'total_losses': 4.2,
            'loss_percent': 4.7,
            'breakers_pass': 11,
            'breakers_fail': 1
        },
        'design_basis': {
            'base_mva': 100,
            'frequency': 50,
            'primary_voltage': 11,
            'secondary_voltage': 0.4
        }
    }
    
    output = "/tmp/test_report.pdf"
    result = generate_analysis_report(output, test_data['project'], test_data)
    print(f"\nâœ… Report generated: {result}")
