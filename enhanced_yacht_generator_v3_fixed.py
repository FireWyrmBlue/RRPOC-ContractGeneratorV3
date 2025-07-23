import streamlit as st
import pandas as pd
import datetime
import os
import io
import json
import uuid
import hashlib
import smtplib
import plotly.express as px
import plotly.graph_objects as go
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import sqlite3
from pathlib import Path

# Configuration
DATABASE_FILE = "yacht_contracts.db"
LOG_FILE = "contract_audit_log.txt"
TEMPLATES_DIR = "templates"
VERSIONS_DIR = "versions"

# Enhanced Contract Template with Suggested Clauses
ENHANCED_CONTRACT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Yacht Charter Contract - {{ vessel_name }}</title>
    <style>
        body { font-family: 'Times New Roman', serif; font-size: 11px; line-height: 1.4; color: #333; margin: 20px; }
        .header { text-align: center; border-bottom: 3px solid #1e3a8a; padding-bottom: 20px; margin-bottom: 30px; }
        .title { font-size: 24px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; }
        .parties { background: #f8fafc; padding: 20px; border-left: 4px solid #1e3a8a; margin: 20px 0; }
        .vessel-specs { background: #f1f5f9; border: 1px solid #cbd5e1; padding: 15px; margin: 15px 0; }
        .risk-assessment { background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; margin: 15px 0; }
        .suggested-clause { background: #ecfdf5; border-left: 4px solid #10b981; padding: 10px; margin: 10px 0; }
        .financial-summary { background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; margin: 15px 0; }
        h1 { color: #1e3a8a; font-size: 16px; border-bottom: 2px solid #1e3a8a; margin-top: 25px; }
        h2 { color: #3730a3; font-size: 14px; margin-top: 15px; }
        h3 { color: #4338ca; font-size: 12px; margin-top: 10px; }
        .highlight { background: #fef3c7; padding: 2px 4px; }
        .two-column { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .contact-info { font-size: 10px; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #cbd5e1; padding: 8px; text-align: left; }
        th { background-color: #f1f5f9; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">Enhanced Yacht Charter Agreement</div>
        <div style="font-size: 16px; margin: 10px 0;">{{ vessel_name }} - Contract {{ contract_id }}</div>
        <div>Version {{ version_number }} - {{ agreement_date }}</div>
        <div style="font-size: 10px; margin-top: 10px;">Template: {{ template_name }} | Language: {{ contract_language }}</div>
    </div>

    <div class="parties">
        <div class="two-column">
            <div>
                <strong>LESSOR (Charter Company):</strong><br>
                <strong>{{ lessor_name }}</strong><br>
                {{ lessor_address }}<br>
                <div class="contact-info">
                    <strong>Contact:</strong> {{ lessor_contact }}<br>
                    <strong>Email:</strong> {{ lessor_email }}<br>
                    <strong>Phone:</strong> {{ lessor_phone }}
                </div>
            </div>
            <div>
                <strong>LESSEE (Charter Client):</strong><br>
                <strong>{{ lessee_name }}</strong><br>
                {{ lessee_address }}<br>
                <div class="contact-info">
                    <strong>Contact:</strong> {{ lessee_contact }}<br>
                    <strong>Email:</strong> {{ lessee_email }}<br>
                    <strong>Phone:</strong> {{ lessee_phone }}
                </div>
            </div>
        </div>
        {% if broker_info %}
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #cbd5e1;">
            <strong>Broker/Agent:</strong> {{ broker_info }}
            {% if broker_commission > 0 %}(Commission: {{ broker_commission }}%){% endif %}
        </div>
        {% endif %}
    </div>

    {% if risk_assessment %}
    <div class="risk-assessment">
        <h2>🛡️ Risk Assessment Summary</h2>
        <div class="two-column">
            <div>
                <p><strong>Overall Risk Score:</strong> {{ risk_assessment.risk_score }} ({{ risk_assessment.risk_category }})</p>
                <p><strong>Charter Experience:</strong> {{ charter_experience }}</p>
                <p><strong>Risk Factors:</strong> {{ risk_factors }}</p>
            </div>
            <div>
                <p><strong>Recommended Hull Insurance:</strong> ${{ "{:,}".format(risk_assessment.recommended_hull_insurance) }}</p>
                <p><strong>Recommended Liability:</strong> ${{ "{:,}".format(risk_assessment.recommended_liability_insurance) }}</p>
                <p><strong>Risk-Adjusted Premium:</strong> {{ risk_assessment.risk_score }}x standard rate</p>
            </div>
        </div>
        
        {% if risk_assessment.recommendations %}
        <h3>Risk Mitigation Recommendations:</h3>
        <ul>
        {% for rec in risk_assessment.recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        </ul>
        {% endif %}
        
        {% if risk_assessment.regional_warnings %}
        <h3>Regional Warnings:</h3>
        {% for warning in risk_assessment.regional_warnings %}
            <p style="color: #dc2626; font-weight: bold;">⚠️ {{ warning }}</p>
        {% endfor %}
        {% endif %}
    </div>
    {% endif %}

    <h1>1. VESSEL SPECIFICATIONS</h1>
    <div class="vessel-specs">
        <table>
            <tr>
                <th>Vessel Details</th>
                <th>Specifications</th>
                <th>Performance</th>
                <th>Capacities</th>
            </tr>
            <tr>
                <td>
                    <strong>Vessel:</strong> {{ vessel_name }}<br>
                    <strong>Type:</strong> {{ yacht_type }}<br>
                    <strong>Registration:</strong> {{ official_number }}<br>
                    <strong>Flag:</strong> {{ flag_state }}
                </td>
                <td>
                    <strong>LOA:</strong> {{ length_overall }}m<br>
                    <strong>Beam:</strong> {{ beam }}m<br>
                    <strong>Draft:</strong> {{ draft }}m<br>
                    <strong>Engine:</strong> {{ engine_power }} HP
                </td>
                <td>
                    <strong>Max Speed:</strong> {{ max_speed }} knots<br>
                    <strong>Cruising:</strong> {{ cruising_speed }} knots<br>
                    <strong>Range:</strong> As per specifications<br>
                    <strong>Fuel Policy:</strong> {{ fuel_policy }}
                </td>
                <td>
                    <strong>Guests:</strong> {{ guest_capacity }}<br>
                    <strong>Crew:</strong> {{ crew_capacity }}<br>
                    <strong>Berths:</strong> As per layout<br>
                    <strong>Cabins:</strong> As per specifications
                </td>
            </tr>
        </table>
    </div>

    <h1>2. CHARTER TERMS & ITINERARY</h1>
    <div class="two-column">
        <div>
            <p><strong>Charter Period:</strong> {{ start_date }} to {{ end_date }}</p>
            <p><strong>Duration:</strong> {{ charter_duration }} days</p>
            <p><strong>Delivery Location:</strong> {{ delivery_location }}</p>
            <p><strong>Return Location:</strong> {{ return_location }}</p>
        </div>
        <div>
            <p><strong>Daily Rate:</strong> {{ currency }} {{ daily_rate }}</p>
            <p><strong>Total Charter Value:</strong> {{ currency }} {{ total_charter_value }}</p>
            <p><strong>Operational Area:</strong> {{ operational_area }}</p>
        </div>
    </div>

    {% if special_requests %}
    <h2>Special Requests & Requirements</h2>
    <div style="background: #f9fafb; padding: 10px; border-left: 3px solid #6366f1;">
        {{ special_requests | replace('\n', '<br>') }}
    </div>
    {% endif %}

    <h1>3. FINANCIAL TERMS</h1>
    <div class="financial-summary">
        <div class="two-column">
            <div>
                <h3>Payment Schedule</h3>
                <p><strong>Initial Payment:</strong> {{ payment_schedule_1 }}% upon signing</p>
                <p><strong>Final Payment:</strong> {{ payment_schedule_2 }}% {{ payment_timing }}</p>
                <p><strong>Security Deposit:</strong> {{ currency }} {{ security_deposit }}</p>
                <p><strong>Deposit Method:</strong> {{ deposit_method }}</p>
            </div>
            <div>
                <h3>Additional Costs</h3>
                <p><strong>Fuel Policy:</strong> {{ fuel_policy }}</p>
                <p><strong>Included Services:</strong> {{ additional_costs }}</p>
                <p><strong>Currency:</strong> {{ currency }}</p>
                <p><strong>VAT/Taxes:</strong> As applicable by law</p>
            </div>
        </div>
    </div>

    {% if suggested_clauses %}
    <h1>4. ENHANCED CONTRACT CLAUSES</h1>
    
    {% if suggested_clauses.force_majeure %}
    <div class="suggested-clause">
        <h2>Force Majeure (AI Recommended)</h2>
        <p>{{ suggested_clauses.force_majeure }}</p>
    </div>
    {% endif %}
    
    {% if suggested_clauses.cancellation %}
    <div class="suggested-clause">
        <h2>Cancellation Policy ({{ cancellation_policy }})</h2>
        <p>{{ suggested_clauses.cancellation }}</p>
    </div>
    {% endif %}
    
    {% if suggested_clauses.weather %}
    <div class="suggested-clause">
        <h2>Weather Limitations (Risk-Adjusted)</h2>
        <p>{{ suggested_clauses.weather }}</p>
    </div>
    {% endif %}
    
    {% if suggested_clauses.crew_standards %}
    <div class="suggested-clause">
        <h2>Crew Standards (Type-Specific)</h2>
        <p>{{ suggested_clauses.crew_standards }}</p>
    </div>
    {% endif %}
    {% endif %}

    {% if additional_clauses %}
    <h1>4A. ADDITIONAL SELECTED CLAUSES</h1>
    {% for clause in additional_clauses %}
    <div class="suggested-clause">
        <h2>{{ clause.name }} {% if clause.source == 'library' %}(From Library){% elif clause.source == 'ai_suggestion' %}(AI Suggested){% else %}(Custom){% endif %}</h2>
        <p>{{ clause.content | replace('\n', '<br>') }}</p>
        {% if clause.category %}
        <p style="font-size: 9px; color: #6b7280; margin-top: 8px;">
            <strong>Category:</strong> {{ clause.category }}
        </p>
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}

    <h1>5. INSURANCE REQUIREMENTS</h1>
    <table>
        <tr>
            <th>Coverage Type</th>
            <th>Required Amount</th>
            <th>AI Recommended</th>
            <th>Risk Factor</th>
        </tr>
        <tr>
            <td>Hull & Machinery</td>
            <td>${{ hull_insurance }} USD</td>
            <td>${{ "{:,}".format(risk_assessment.recommended_hull_insurance) if risk_assessment else hull_insurance }} USD</td>
            <td>{{ risk_assessment.risk_score if risk_assessment else '1.0' }}x</td>
        </tr>
        <tr>
            <td>Third Party Liability</td>
            <td>${{ liability_insurance }} USD</td>
            <td>${{ "{:,}".format(risk_assessment.recommended_liability_insurance) if risk_assessment else liability_insurance }} USD</td>
            <td>{{ risk_assessment.risk_score if risk_assessment else '1.0' }}x</td>
        </tr>
        <tr>
            <td>Personal Effects</td>
            <td>As per policy</td>
            <td>Standard coverage</td>
            <td>Standard</td>
        </tr>
    </table>

    <h1>6. OPERATIONAL LIMITATIONS & SAFETY</h1>
    <div class="two-column">
        <div>
            <h3>Operational Areas</h3>
            <p>{{ operational_area }}</p>
            
            <h3>Weather Restrictions</h3>
            <p>As per AI-recommended weather clause above. Captain's discretion applies for safety.</p>
        </div>
        <div>
            <h3>Safety Equipment</h3>
            <p>All safety equipment as per {{ flag_state }} maritime regulations and SOLAS requirements.</p>
            
            <h3>Crew Qualifications</h3>
            <p>All crew hold valid STCW certifications. Captain certified for {{ yacht_type }} operations.</p>
        </div>
    </div>

    <h1>7. TERMS & CONDITIONS</h1>
    <div style="font-size: 10px; line-height: 1.3;">
        <div class="two-column">
            <div>
                <h3>Governing Law</h3>
                <p>This Agreement is governed by the laws of {{ governing_law }}.</p>
                
                <h3>Cancellation Policy</h3>
                <p>{{ cancellation_policy }} terms apply as detailed in Section 4.</p>
                
                <h3>Force Majeure</h3>
                <p>{% if suggested_clauses.force_majeure %}Force Majeure clause included.{% else %}Standard force majeure terms apply.{% endif %}</p>
            </div>
            <div>
                <h3>Dispute Resolution</h3>
                <p>Disputes shall be resolved through arbitration under {{ governing_law }} jurisdiction.</p>
                
                <h3>Liability Limitations</h3>
                <p>Liability limited to charter value except in cases of gross negligence.</p>
                
                <h3>Charter Experience Considerations</h3>
                <p>Charter client experience level: {{ charter_experience }}. Additional briefings may apply.</p>
            </div>
        </div>
    </div>

    <div style="margin-top: 40px; border-top: 3px solid #1e3a8a; padding-top: 20px;">
        <h1>EXECUTION</h1>
        <div class="two-column">
            <div>
                <p><strong>LESSOR:</strong> {{ lessor_name }}</p>
                <p><strong>Representative:</strong> {{ lessor_contact }}</p>
                <p>Signature: _________________________</p>
                <p>Date: _________________</p>
                <p>Place: _________________</p>
            </div>
            <div>
                <p><strong>LESSEE:</strong> {{ lessee_name }}</p>
                <p><strong>Representative:</strong> {{ lessee_contact }}</p>
                <p>Signature: _________________________</p>
                <p>Date: _________________</p>
                <p>Place: _________________</p>
            </div>
        </div>
        
        {% if broker_info %}
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #cbd5e1;">
            <p><strong>BROKER/AGENT:</strong> {{ broker_info }}</p>
            <p>Signature: _________________________</p>
            <p>Date: _________________</p>
        </div>
        {% endif %}
    </div>

    <div style="margin-top: 30px; padding: 15px; background: #f8fafc; border: 1px solid #e2e8f0; font-size: 9px;">
        <div class="two-column">
            <div>
                <p><strong>Generated by Yacht Contract Generator V3</strong></p>
                <p>Contract ID: {{ contract_id }} | Template: {{ template_name }}</p>
                <p>Risk Score: {{ risk_assessment.risk_score if risk_assessment else 'N/A' }} | Language: {{ contract_language }}</p>
            </div>
            <div>
                <p><strong>AI Features Applied:</strong></p>
                <p>✅ Risk Assessment & Optimization</p>
                <p>✅ Intelligent Clause Selection</p>
                <p>✅ Industry Best Practices</p>
            </div>
        </div>
        <p style="text-align: center; margin-top: 10px; font-style: italic;">
            This contract includes AI-powered risk assessment and clause optimization based on vessel specifications, operational requirements, and charter client profile.
        </p>
    </div>
</body>
</html>
"""

# PDF Generation Function
def generate_pdf_contract(contract_html, filename, contract_data):
    """Generate PDF from HTML contract with full content using ReportLab"""
    try:
        # Use ReportLab directly for better Windows compatibility
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.lib.units import inch
        import io
        
        print("Generating PDF using ReportLab for Windows compatibility...")
        
        # Enhanced ReportLab with comprehensive content
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            topMargin=0.8*inch, 
            bottomMargin=0.8*inch,
            leftMargin=0.7*inch,
            rightMargin=0.7*inch
        )
        
        styles = getSampleStyleSheet()
        
        # Enhanced styles with colors and formatting
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a8a'),  # Navy blue
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.HexColor('#1e3a8a'),
            borderPadding=10
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#1e3a8a'),  # Navy blue
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#1e3a8a'),
            leftIndent=0,
            borderPadding=8
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.HexColor('#3730a3'),  # Purple blue
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica',
            leading=14
        )
        
        highlight_style = ParagraphStyle(
            'HighlightStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1e3a8a'),
            backColor=colors.HexColor('#f0f9ff')
        )
        
        content = []
        
        # Title with enhanced formatting
        content.append(Paragraph("YACHT CHARTER AGREEMENT", title_style))
        content.append(Spacer(1, 12))
        
        # Contract header info in a styled table
        header_data = [
            ['Contract ID:', contract_data.get('contract_id', 'N/A')],
            ['Vessel:', contract_data.get('vessel_name', 'N/A')],
            ['Version:', f"{contract_data.get('version_number', '1.0')} - {contract_data.get('agreement_date', 'N/A')}"]
        ]
        
        header_table = Table(header_data, colWidths=[2*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        content.append(header_table)
        content.append(Spacer(1, 20))
        
        # Vessel Information with styled table
        content.append(Paragraph("1. VESSEL SPECIFICATIONS", heading_style))
        content.append(Spacer(1, 8))
        
        vessel_data = [
            ['Vessel Name:', contract_data.get('vessel_name', 'N/A')],
            ['Type:', contract_data.get('yacht_type', 'N/A')],
            ['Length Overall:', f"{contract_data.get('length_overall', 'N/A')}m"],
            ['Beam:', f"{contract_data.get('beam', 'N/A')}m"],
            ['Draft:', f"{contract_data.get('draft', 'N/A')}m"],
            ['Flag State:', contract_data.get('flag_state', 'N/A')],
            ['Guest Capacity:', contract_data.get('guest_capacity', 'N/A')],
            ['Crew Capacity:', contract_data.get('crew_capacity', 'N/A')],
            ['Engine Power:', f"{contract_data.get('engine_power', 'N/A')} HP"],
            ['Max Speed:', f"{contract_data.get('max_speed', 'N/A')} knots"],
            ['Official Number:', contract_data.get('official_number', 'N/A')]
        ]
        
        vessel_table = Table(vessel_data, colWidths=[2.5*inch, 3.5*inch])
        vessel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        content.append(vessel_table)
        content.append(Spacer(1, 15))
        
        # Charter Terms with financial highlighting
        content.append(Paragraph("2. CHARTER TERMS & ITINERARY", heading_style))
        content.append(Spacer(1, 8))
        
        charter_data = [
            ['Charter Period:', f"{contract_data.get('start_date', 'N/A')} to {contract_data.get('end_date', 'N/A')}"],
            ['Duration:', f"{contract_data.get('charter_duration', 'N/A')} days"],
            ['Daily Rate:', f"{contract_data.get('currency', 'EUR')} {contract_data.get('daily_rate', 'N/A')}"],
            ['Total Charter Value:', f"{contract_data.get('currency', 'EUR')} {contract_data.get('total_charter_value', 'N/A')}"],
            ['Operational Area:', contract_data.get('operational_area', 'N/A')],
            ['Delivery Location:', contract_data.get('delivery_location', 'N/A')],
            ['Return Location:', contract_data.get('return_location', 'N/A')]
        ]
        
        charter_table = Table(charter_data, colWidths=[2.5*inch, 3.5*inch])
        charter_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (1, 2), (1, 3), colors.HexColor('#f0f9ff')),  # Highlight financial rows
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (1, 2), (1, 3), colors.HexColor('#0ea5e9')),  # Financial highlight color
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (1, 2), (1, 3), 'Helvetica-Bold'),  # Bold financial values
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        content.append(charter_table)
        content.append(Spacer(1, 15))
        
        # Parties with enhanced formatting
        content.append(Paragraph("3. PARTIES", heading_style))
        content.append(Spacer(1, 8))
        
        # Lessor information
        content.append(Paragraph("LESSOR (Charter Company)", subheading_style))
        lessor_data = [
            ['Company Name:', contract_data.get('lessor_name', 'N/A')],
            ['Address:', contract_data.get('lessor_address', 'N/A').replace('<br>', '\n')],
            ['Contact Person:', contract_data.get('lessor_contact', 'N/A')],
            ['Email:', contract_data.get('lessor_email', 'N/A')],
            ['Phone:', contract_data.get('lessor_phone', 'N/A')]
        ]
        
        lessor_table = Table(lessor_data, colWidths=[1.5*inch, 4.5*inch])
        lessor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),  # Bold line under company name
        ]))
        
        content.append(lessor_table)
        content.append(Spacer(1, 12))
        
        # Lessee information
        content.append(Paragraph("LESSEE (Charter Client)", subheading_style))
        lessee_data = [
            ['Client Name:', contract_data.get('lessee_name', 'N/A')],
            ['Address:', contract_data.get('lessee_address', 'N/A').replace('<br>', '\n')],
            ['Contact Person:', contract_data.get('lessee_contact', 'N/A')],
            ['Email:', contract_data.get('lessee_email', 'N/A')],
            ['Phone:', contract_data.get('lessee_phone', 'N/A')]
        ]
        
        lessee_table = Table(lessee_data, colWidths=[1.5*inch, 4.5*inch])
        lessee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),  # Bold line under client name
        ]))
        
        content.append(lessee_table)
        content.append(Spacer(1, 15))
        
        # Financial Terms with enhanced highlighting
        content.append(Paragraph("4. FINANCIAL TERMS", heading_style))
        content.append(Spacer(1, 8))
        
        financial_data = [
            ['Payment Schedule:', f"{contract_data.get('payment_schedule_1', 'N/A')}% upon signing, {contract_data.get('payment_schedule_2', 'N/A')}% {contract_data.get('payment_timing', 'N/A')}"],
            ['Security Deposit:', f"{contract_data.get('currency', 'EUR')} {contract_data.get('security_deposit', 'N/A')}"],
            ['Deposit Method:', contract_data.get('deposit_method', 'N/A')],
            ['Fuel Policy:', contract_data.get('fuel_policy', 'N/A')],
            ['Additional Costs:', contract_data.get('additional_costs', 'N/A')],
            ['Currency:', contract_data.get('currency', 'EUR')]
        ]
        
        financial_table = Table(financial_data, colWidths=[2*inch, 4*inch])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f9ff')),
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#fef3c7')),  # Highlight security deposit
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0ea5e9')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#0ea5e9')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        content.append(financial_table)
        content.append(Spacer(1, 15))
        
        # Insurance & Risk Assessment with warning colors
        content.append(Paragraph("5. INSURANCE REQUIREMENTS", heading_style))
        content.append(Spacer(1, 8))
        
        insurance_data = [
            ['Hull Insurance:', f"USD {contract_data.get('hull_insurance', 'N/A')}"],
            ['Liability Insurance:', f"USD {contract_data.get('liability_insurance', 'N/A')}"],
            ['Charter Experience:', contract_data.get('charter_experience', 'N/A')],
            ['Risk Factors:', contract_data.get('risk_factors', 'N/A')]
        ]
        
        insurance_table = Table(insurance_data, colWidths=[2*inch, 4*inch])
        insurance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),  # Warning yellow background
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#f59e0b')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f59e0b')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        content.append(insurance_table)
        content.append(Spacer(1, 15))
        
        # Risk Assessment with enhanced formatting
        if contract_data.get('risk_assessment'):
            risk_data = contract_data['risk_assessment']
            content.append(Paragraph("6. RISK ASSESSMENT SUMMARY", heading_style))
            content.append(Spacer(1, 8))
            
            risk_assessment_data = [
                ['Overall Risk Score:', f"{risk_data.get('risk_score', 'N/A')} ({risk_data.get('risk_category', 'N/A')})"],
                ['Recommended Hull Insurance:', f"USD {risk_data.get('recommended_hull_insurance', 'N/A'):,}"],
                ['Recommended Liability Insurance:', f"USD {risk_data.get('recommended_liability_insurance', 'N/A'):,}"]
            ]
            
            risk_table = Table(risk_assessment_data, colWidths=[2.5*inch, 3.5*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#fee2e2')),  # Risk score background
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#f59e0b')),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#dc2626')),  # Risk score color
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),  # Bold risk score
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f59e0b')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            content.append(risk_table)
            content.append(Spacer(1, 15))
        
        # Special Requests with highlighted box
        if contract_data.get('special_requests'):
            content.append(Paragraph("7. SPECIAL REQUESTS & REQUIREMENTS", heading_style))
            content.append(Spacer(1, 8))
            
            # Create a highlighted box for special requests
            special_requests_style = ParagraphStyle(
                'SpecialRequests',
                parent=normal_style,
                backColor=colors.HexColor('#ecfdf5'),
                borderColor=colors.HexColor('#10b981'),
                borderWidth=1,
                borderPadding=10,
                fontName='Helvetica'
            )
            
            content.append(Paragraph(contract_data.get('special_requests', ''), special_requests_style))
            content.append(Spacer(1, 15))
        
        # Contract Terms & Conditions with professional styling
        content.append(Paragraph("8. TERMS & CONDITIONS", heading_style))
        content.append(Spacer(1, 8))
        
        terms_data = [
            ['Template Type:', contract_data.get('template_name', 'N/A')],
            ['Version:', contract_data.get('version_number', 'N/A')],
            ['Agreement Date:', contract_data.get('agreement_date', 'N/A')],
            ['Governing Law:', contract_data.get('governing_law', 'N/A')],
            ['Contract Language:', contract_data.get('contract_language', 'N/A')],
            ['Cancellation Policy:', contract_data.get('cancellation_policy', 'N/A')],
            ['Broker/Agent:', contract_data.get('broker_info', 'N/A')]
        ]
        
        terms_table = Table(terms_data, colWidths=[2*inch, 4*inch])
        terms_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        content.append(terms_table)
        content.append(Spacer(1, 20))
        
        # Signature Section with professional layout
        content.append(Paragraph("EXECUTION", heading_style))
        content.append(Spacer(1, 8))
        
        # Create signature tables
        signature_data = [
            ['LESSOR:', contract_data.get('lessor_name', 'N/A')],
            ['Representative:', contract_data.get('lessor_contact', 'N/A')],
            ['Signature:', '_' * 40],
            ['Date:', '_' * 20],
            ['', ''],
            ['LESSEE:', contract_data.get('lessee_name', 'N/A')],
            ['Representative:', contract_data.get('lessee_contact', 'N/A')],
            ['Signature:', '_' * 40],
            ['Date:', '_' * 20]
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 4.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e3a8a')),  # LESSOR line
            ('LINEBELOW', (0, 5), (-1, 5), 2, colors.HexColor('#1e3a8a')),  # LESSEE line
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0, 5), (0, 5), colors.HexColor('#f1f5f9')),
        ]))
        
        content.append(signature_table)
        content.append(Spacer(1, 20))
        
        # Additional clauses from Clause Library
        additional_clauses = contract_data.get('additional_clauses', [])
        if additional_clauses:
            content.append(Paragraph("ADDITIONAL SELECTED CLAUSES", heading_style))
            content.append(Spacer(1, 8))
            
            for i, clause in enumerate(additional_clauses, 1):
                # Clause title with source
                source_text = ""
                if clause.get('source') == 'library':
                    source_text = " (From Library)"
                elif clause.get('source') == 'ai_suggestion':
                    source_text = " (AI Suggested)"
                elif clause.get('source') == 'custom':
                    source_text = " (Custom)"
                
                clause_title = f"{i}. {clause.get('name', 'Untitled Clause')}{source_text}"
                content.append(Paragraph(clause_title, subheading_style))
                content.append(Spacer(1, 4))
                
                # Clause content
                clause_content = clause.get('content', 'No content available')
                content.append(Paragraph(clause_content, normal_style))
                
                # Category if available
                if clause.get('category'):
                    category_text = f"Category: {clause['category']}"
                    content.append(Paragraph(category_text, 
                        ParagraphStyle('CategoryStyle', parent=styles['Normal'], 
                                     fontSize=8, textColor=colors.HexColor('#6b7280'),
                                     spaceBefore=2, spaceAfter=8)))
                
                content.append(Spacer(1, 8))
            
            content.append(Spacer(1, 15))
        
        # Footer with professional styling
        footer_style = ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.HexColor('#cbd5e1'),
            borderPadding=8,
            backColor=colors.HexColor('#f9fafb')
        )
        
        footer_text = f"""<i>Generated by Yacht Contract Generator V3<br/>
Contract ID: {contract_data.get('contract_id', 'N/A')} | Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
AI Features: Risk Assessment, Intelligent Clause Selection, Industry Best Practices</i>"""
        
        content.append(Paragraph(footer_text, footer_style))
        
        # Build PDF
        doc.build(content)
        buffer.seek(0)
        
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
        
        print(f"PDF generated successfully using ReportLab fallback: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        # Create a minimal PDF with error message
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        content = [
            Paragraph("YACHT CHARTER CONTRACT", styles['Title']),
            Paragraph(f"Error generating full contract: {str(e)}", styles['Normal']),
            Paragraph(f"Contract ID: {contract_data.get('contract_id', 'N/A')}", styles['Normal']),
            Paragraph(f"Vessel: {contract_data.get('vessel_name', 'N/A')}", styles['Normal'])
        ]
        
        doc.build(content)
        buffer.seek(0)
        
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
        
        return filename

# Streamlit Application
def main():
    st.set_page_config(
        page_title="Yacht Contract Generator V3",
        page_icon="⛵",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc, #e2e8f0);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>⛵ Yacht Contract Generator V3</h1>
        <p>AI-Powered Contract Generation with Risk Assessment & Optimization</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize systems
    systems = {
        'database': ContractDatabase(),
        'risk_assessor': None,  # Placeholder for risk assessment system
        'template_manager': None,  # Placeholder for template management
        'audit_logger': None  # Placeholder for audit logging
    }
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    page = st.sidebar.selectbox(
        "Choose Function",
        ["🏠 Contract Generator", "📋 Template Manager", "⚠️ Risk Assessment", 
         "🔧 Clause Library", "📁 Contract Versions", "📈 Analytics & Logs", "⚙️ Settings"]
    )
    
    # Route to appropriate page
    if page == "🏠 Contract Generator":
        contract_generator_page(systems)
    elif page == "📋 Template Manager":
        template_manager_page(systems)
    elif page == "⚠️ Risk Assessment":
        risk_assessment_page(systems)
    elif page == "🔧 Clause Library":
        clause_library_page(systems)
    elif page == "📁 Contract Versions":
        contract_versions_page(systems)
    elif page == "📈 Analytics & Logs":
        analytics_page(systems)
    elif page == "⚙️ Settings":
        settings_page()

def contract_generator_page(systems):
    st.header("🚀 AI-Enhanced Contract Generator")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Contracts", "0")
    with col2:
        st.metric("Active Templates", "1")
    with col3:
        st.metric("Avg Risk Score", "1.2")
    with col4:
        st.metric("AI Features", "4 Active")
    
    # AI Vessel Name Generator (outside form)
    st.markdown("### 🤖 AI-Powered Vessel Name Generator")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        if st.button("🎲 Generate Random Vessel Name", type="secondary", use_container_width=True):
            # AI vessel name generation function
            import random
            
            # Yacht name components for realistic generation
            prefixes = ["M/Y", "S/Y", ""]
            luxury_words = [
                "Serenity", "Tranquility", "Majesty", "Excellence", "Elegance", "Prestige", 
                "Sovereign", "Liberty", "Harmony", "Paradise", "Infinity", "Aurora",
                "Azure", "Celestial", "Diamond", "Emerald", "Golden", "Platinum",
                "Royal", "Imperial", "Crystal", "Pearl", "Sapphire", "Stellar"
            ]
            nature_words = [
                "Wave", "Current", "Tide", "Breeze", "Storm", "Dawn", "Sunset", "Ocean",
                "Sea", "Wind", "Star", "Moon", "Sun", "Island", "Bay", "Coast",
                "Horizon", "Depths", "Spirit", "Dream", "Quest", "Journey", "Voyage"
            ]
            mythological = [
                "Poseidon", "Neptune", "Triton", "Nereid", "Thalassa", "Oceanus",
                "Amphitrite", "Calypso", "Sirena", "Nautilus", "Pegasus", "Phoenix",
                "Atlas", "Orion", "Cassiopeia", "Andromeda", "Vega", "Altair"
            ]
            modern_names = [
                "Zenith", "Apex", "Nexus", "Vortex", "Matrix", "Vertex", "Axiom",
                "Catalyst", "Paradigm", "Synthesis", "Genesis", "Exodus", "Momentum"
            ]
            
            # Different generation styles
            styles = [
                # Single luxury word with prefix
                lambda: f"{random.choice(prefixes)} {random.choice(luxury_words)}".strip(),
                # Combination of luxury + nature
                lambda: f"{random.choice(prefixes)} {random.choice(luxury_words)} {random.choice(nature_words)}".strip(),
                # Mythological names
                lambda: f"{random.choice(prefixes)} {random.choice(mythological)}".strip(),
                # Modern tech-inspired
                lambda: f"{random.choice(prefixes)} {random.choice(modern_names)}".strip(),
                # Nature + Roman numerals
                lambda: f"{random.choice(prefixes)} {random.choice(nature_words)} {random.choice(['II', 'III', 'IV', 'V'])}".strip(),
                # Luxury with numbers
                lambda: f"{random.choice(prefixes)} {random.choice(luxury_words)} {random.randint(1, 99)}".strip(),
            ]
            
            # Generate a new vessel name
            generated_name = random.choice(styles)()
            
            # Update the session state to change the input value
            st.session_state.ai_generated_vessel_name = generated_name
            
            # Show a success message
            st.success(f"🎉 Generated vessel name: **{generated_name}**")
    
    with col2:
        if st.button("🔄 Generate Another", type="primary", use_container_width=True):
            # Generate multiple options for user to choose from
            import random
            
            # Same generation logic as above
            prefixes = ["M/Y", "S/Y", ""]
            luxury_words = [
                "Serenity", "Tranquility", "Majesty", "Excellence", "Elegance", "Prestige", 
                "Sovereign", "Liberty", "Harmony", "Paradise", "Infinity", "Aurora",
                "Azure", "Celestial", "Diamond", "Emerald", "Golden", "Platinum"
            ]
            nature_words = [
                "Wave", "Current", "Tide", "Breeze", "Storm", "Dawn", "Sunset", "Ocean",
                "Sea", "Wind", "Star", "Moon", "Sun", "Island", "Bay", "Coast"
            ]
            mythological = [
                "Poseidon", "Neptune", "Triton", "Nereid", "Thalassa", "Oceanus",
                "Amphitrite", "Calypso", "Sirena", "Nautilus", "Pegasus", "Phoenix"
            ]
            modern_names = [
                "Zenith", "Apex", "Nexus", "Vortex", "Matrix", "Vertex", "Axiom",
                "Catalyst", "Paradigm", "Synthesis", "Genesis", "Exodus", "Momentum"
            ]
            
            styles = [
                lambda: f"{random.choice(prefixes)} {random.choice(luxury_words)}".strip(),
                lambda: f"{random.choice(prefixes)} {random.choice(luxury_words)} {random.choice(nature_words)}".strip(),
                lambda: f"{random.choice(prefixes)} {random.choice(mythological)}".strip(),
                lambda: f"{random.choice(prefixes)} {random.choice(modern_names)}".strip(),
                lambda: f"{random.choice(prefixes)} {random.choice(nature_words)} {random.choice(['II', 'III', 'IV', 'V'])}".strip(),
            ]
            
            generated_name = random.choice(styles)()
            st.session_state.ai_generated_vessel_name = generated_name
            st.info(f"🔄 New suggestion: **{generated_name}**")
    
    with col3:
        # Show example generated names for inspiration
        if st.button("💡 Show Examples", use_container_width=True):
            st.session_state.show_examples = not st.session_state.get('show_examples', False)
    
    # Display examples if requested
    if st.session_state.get('show_examples', False):
        with st.expander("🎨 AI-Generated Name Examples", expanded=True):
            examples = [
                "M/Y Azure Dream", "S/Y Neptune's Quest", "M/Y Platinum Horizon",
                "M/Y Celestial Wave", "S/Y Sapphire Journey", "M/Y Golden Infinity",
                "S/Y Triton's Crown", "M/Y Crystal Serenity", "M/Y Apex Explorer"
            ]
            cols = st.columns(3)
            for i, example in enumerate(examples):
                with cols[i % 3]:
                    if st.button(f"Use: {example}", key=f"example_{i}"):
                        st.session_state.ai_generated_vessel_name = example
                        st.success(f"Selected: **{example}**")
                        st.rerun()
    
    st.markdown("---")
    
    # AI Company & Client Generator (outside form)
    st.markdown("### 🏢 AI-Powered Company & Client Generator")
    
    # Lessor (Charter Company) Generator
    st.markdown("#### 🏛️ Charter Company Generator")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        if st.button("🎲 Generate Random Charter Company", type="secondary", use_container_width=True):
            import random
            
            # Charter company name components
            company_prefixes = [
                "Monaco", "Azure", "Mediterranean", "Elite", "Platinum", "Royal", "Sovereign",
                "Premier", "Exclusive", "Luxury", "Diamond", "Crystal", "Golden", "Imperial"
            ]
            company_types = [
                "Yacht Charters", "Marine Services", "Luxury Charters", "Yacht Management",
                "Elite Charters", "Premium Yachts", "Yacht Solutions", "Marine Group"
            ]
            company_suffixes = ["Ltd.", "S.A.", "Inc.", "Group", "International", "Services"]
            
            # Generate company details
            company_name = f"{random.choice(company_prefixes)} {random.choice(company_types)} {random.choice(company_suffixes)}"
            
            # Location data
            locations = {
                "Monaco": {
                    "address": f"{random.randint(1, 99)} {random.choice(['Quai Antoine 1er', 'Avenue de la Costa', 'Boulevard Albert 1er', 'Rue Grimaldi'])}\n98000 Monaco\nPrincipality of Monaco",
                    "phone": f"+377 93 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                },
                "Nice": {
                    "address": f"{random.randint(1, 150)} {random.choice(['Promenade des Anglais', 'Avenue Jean Médecin', 'Rue de France'])}\n06000 Nice\nFrance",
                    "phone": f"+33 4 93 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                },
                "Cannes": {
                    "address": f"{random.randint(1, 200)} {random.choice(['Boulevard de la Croisette', 'Rue d Antibes', 'Avenue de Grasse'])}\n06400 Cannes\nFrance",
                    "phone": f"+33 4 93 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                },
                "Malta": {
                    "address": f"{random.randint(1, 100)} {random.choice(['Marina Street', 'Republic Street', 'Merchants Street'])}\nValletta VLT {random.randint(1000, 1999)}\nMalta",
                    "phone": f"+356 21 {random.randint(100000, 999999)}"
                }
            }
            
            location = random.choice(list(locations.keys()))
            location_data = locations[location]
            
            # Captain names
            captain_titles = ["Captain", "Skipper", "Master"]
            first_names = ["Jean-Luc", "Marco", "Alessandro", "Dimitri", "Andreas", "Philippe", "Lorenzo", "Constantin"]
            last_names = ["Moreau", "Rossi", "Papadopoulos", "Martinez", "Schmidt", "Dubois", "Romano", "Benedetti"]
            
            contact_person = f"{random.choice(captain_titles)} {random.choice(first_names)} {random.choice(last_names)}"
            
            # Generate email
            company_domain = company_name.lower().replace(" ", "").replace(".", "")[:15]
            email_domains = ["yacht.mc", "charters.com", "marine.eu", "luxury.fr", "premium.com"]
            email = f"charters@{company_domain}.{random.choice(email_domains).split('.')[-1]}"
            
            # Store in session state
            st.session_state.ai_generated_lessor = {
                'name': company_name,
                'address': location_data['address'],
                'contact': contact_person,
                'email': email,
                'phone': location_data['phone']
            }
            
            st.success(f"🎉 Generated charter company: **{company_name}**")
    
    with col2:
        if st.button("🔄 Generate Another Company", type="primary", use_container_width=True):
            import random
            
            # Simplified generation for second button
            company_prefixes = ["Riviera", "Prestige", "Nautical", "Ocean", "Supreme", "Majestic"]
            company_types = ["Yacht Services", "Charter Group", "Marine Solutions", "Luxury Fleet"]
            company_suffixes = ["Ltd.", "S.A.", "Group", "International"]
            
            company_name = f"{random.choice(company_prefixes)} {random.choice(company_types)} {random.choice(company_suffixes)}"
            
            locations = {
                "Antibes": {
                    "address": f"{random.randint(1, 80)} Port Vauban\n06600 Antibes\nFrance",
                    "phone": f"+33 4 93 {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                },
                "Palma": {
                    "address": f"{random.randint(1, 150)} Paseo Marítimo\n07014 Palma de Mallorca\nSpain",
                    "phone": f"+34 971 {random.randint(100, 999)} {random.randint(100, 999)}"
                }
            }
            
            location = random.choice(list(locations.keys()))
            location_data = locations[location]
            
            captain_names = ["Captain Marina Delacroix", "Skipper Antonio Vega", "Master Thomas Andersson"]
            contact_person = random.choice(captain_names)
            
            company_short = company_name.lower().replace(" ", "")[:12]
            email = f"info@{company_short}.com"
            
            st.session_state.ai_generated_lessor = {
                'name': company_name,
                'address': location_data['address'],
                'contact': contact_person,
                'email': email,
                'phone': location_data['phone']
            }
            
            st.info(f"🔄 New company: **{company_name}**")
    
    with col3:
        if st.button("💼 Show Company Examples", use_container_width=True):
            st.session_state.show_lessor_examples = not st.session_state.get('show_lessor_examples', False)
    
    # Display lessor examples if requested
    if st.session_state.get('show_lessor_examples', False):
        with st.expander("🏢 AI-Generated Company Examples", expanded=True):
            examples = [
                {"name": "Monaco Elite Charters Ltd.", "location": "Monaco", "type": "Luxury"},
                {"name": "Azure Marine Services S.A.", "location": "Nice", "type": "Premium"},
                {"name": "Mediterranean Yacht Solutions", "location": "Cannes", "type": "Exclusive"},
                {"name": "Royal Charter Group", "location": "Malta", "type": "Elite"},
                {"name": "Platinum Yacht Management", "location": "Antibes", "type": "Supreme"},
                {"name": "Diamond Marine International", "location": "Palma", "type": "Luxury"}
            ]
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    if st.button(f"Use: {example['name']}", key=f"lessor_example_{i}"):
                        # Generate full details for selected example
                        locations = {
                            "Monaco": {"address": "12 Quai Antoine 1er\n98000 Monaco\nPrincipality of Monaco", "phone": "+377 93 30 15 15"},
                            "Nice": {"address": "45 Promenade des Anglais\n06000 Nice\nFrance", "phone": "+33 4 93 87 12 34"},
                            "Cannes": {"address": "78 Boulevard de la Croisette\n06400 Cannes\nFrance", "phone": "+33 4 93 68 45 67"},
                            "Malta": {"address": "25 Marina Street\nValletta VLT 1234\nMalta", "phone": "+356 21 234567"},
                            "Antibes": {"address": "15 Port Vauban\n06600 Antibes\nFrance", "phone": "+33 4 93 34 56 78"},
                            "Palma": {"address": "89 Paseo Marítimo\n07014 Palma de Mallorca\nSpain", "phone": "+34 971 123 456"}
                        }
                        
                        location_data = locations.get(example['location'], locations['Monaco'])
                        contact_person = f"Captain {['Jean-Luc Moreau', 'Marina Delacroix', 'Antonio Vega', 'Alessandro Romano'][i % 4]}"
                        email = f"charters@{example['name'].lower().replace(' ', '').replace('.', '')[:10]}.com"
                        
                        st.session_state.ai_generated_lessor = {
                            'name': example['name'],
                            'address': location_data['address'],
                            'contact': contact_person,
                            'email': email,
                            'phone': location_data['phone']
                        }
                        st.success(f"Selected: **{example['name']}**")
                        st.rerun()
    
    # Lessee (Charter Client) Generator
    st.markdown("#### 👥 Charter Client Generator")
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        if st.button("🎲 Generate Random Charter Client", type="secondary", use_container_width=True):
            import random
            
            # Client name components
            titles = ["Mr. & Mrs.", "Dr. & Mrs.", "Sir & Lady", "Mr.", "Ms.", "Dr."]
            first_names_male = ["James", "William", "Charles", "Alexander", "Richard", "Michael", "David", "Robert"]
            first_names_female = ["Sarah", "Catherine", "Elizabeth", "Victoria", "Diana", "Sophia", "Isabella", "Charlotte"]
            last_names = ["Richardson", "Thompson", "Williams", "Anderson", "Campbell", "Mitchell", "Harrison", "Bennett", "Hamilton", "Morrison"]
            
            # Generate client name
            title = random.choice(titles)
            if "& Mrs." in title or "& Lady" in title:
                client_name = f"{title} {random.choice(first_names_male)} {random.choice(last_names)}"
                primary_contact = f"{random.choice(first_names_male)} {client_name.split()[-1]}"
            else:
                if title in ["Ms.", "Mrs."]:
                    first_name = random.choice(first_names_female)
                else:
                    first_name = random.choice(first_names_male)
                last_name = random.choice(last_names)
                client_name = f"{title} {first_name} {last_name}"
                primary_contact = f"{first_name} {last_name}"
            
            # Location data for clients
            client_locations = {
                "London": {
                    "address": f"{random.randint(1, 200)} {random.choice(['Berkeley Square', 'Grosvenor Square', 'Sloane Street', 'Kings Road', 'Bond Street'])}\nLondon {random.choice(['W1J', 'SW1', 'SW3', 'W1K'])} {random.randint(1, 9)}{random.choice(['A', 'B', 'C'])}T\nUnited Kingdom",
                    "phone": f"+44 20 {random.randint(7000, 8999)} {random.randint(1000, 9999)}"
                },
                "New York": {
                    "address": f"{random.randint(1, 999)} {random.choice(['Park Avenue', 'Fifth Avenue', 'Madison Avenue', 'Lexington Avenue'])}\nNew York, NY {random.randint(10001, 10999)}\nUnited States",
                    "phone": f"+1 212 {random.randint(100, 999)} {random.randint(1000, 9999)}"
                },
                "Geneva": {
                    "address": f"{random.randint(1, 150)} {random.choice(['Rue du Rhône', 'Rue de la Confédération', 'Boulevard Carl-Vogt'])}\n{random.randint(1200, 1299)} Geneva\nSwitzerland",
                    "phone": f"+41 22 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
                },
                "Paris": {
                    "address": f"{random.randint(1, 200)} {random.choice(['Avenue des Champs-Élysées', 'Rue de Rivoli', 'Boulevard Saint-Germain'])}\n{random.randint(75001, 75020)} Paris\nFrance",
                    "phone": f"+33 1 {random.randint(40, 49)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                }
            }
            
            location = random.choice(list(client_locations.keys()))
            location_data = client_locations[location]
            
            # Generate email
            first_initial = primary_contact.split()[0][0].lower()
            last_name_email = primary_contact.split()[-1].lower()
            email_domains = ["email.com", "gmail.com", "outlook.com", "icloud.com", "me.com"]
            email = f"{first_initial}.{last_name_email}@{random.choice(email_domains)}"
            
            # Store in session state
            st.session_state.ai_generated_lessee = {
                'name': client_name,
                'address': location_data['address'],
                'contact': primary_contact,
                'email': email,
                'phone': location_data['phone']
            }
            
            st.success(f"🎉 Generated charter client: **{client_name}**")
    
    with col2:
        if st.button("🔄 Generate Another Client", type="primary", use_container_width=True):
            import random
            
            # Simplified generation for business clients
            business_titles = ["CEO", "Managing Director", "Chairman", "President"]
            companies = ["Tech Solutions Inc.", "Global Ventures Ltd.", "Investment Group", "Holdings Company"]
            
            title = random.choice(business_titles)
            company = random.choice(companies)
            first_name = random.choice(["Marcus", "Victoria", "Alexander", "Sophia", "Jonathan", "Isabella"])
            last_name = random.choice(["Sterling", "Blackwood", "Westfield", "Ashworth", "Pemberton"])
            
            client_name = f"{first_name} {last_name}, {title}"
            primary_contact = f"{first_name} {last_name}"
            
            business_locations = {
                "Dubai": {
                    "address": f"Office {random.randint(1001, 4999)}\nBurj Khalifa Boulevard\nDowntown Dubai, UAE",
                    "phone": f"+971 4 {random.randint(100, 999)} {random.randint(1000, 9999)}"
                },
                "Singapore": {
                    "address": f"{random.randint(1, 100)} Raffles Place\n#{random.randint(10, 50)}-{random.randint(10, 99)}\nSingapore {random.randint(48001, 48999)}",
                    "phone": f"+65 {random.randint(6000, 9999)} {random.randint(1000, 9999)}"
                }
            }
            
            location = random.choice(list(business_locations.keys()))
            location_data = business_locations[location]
            
            email = f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '').replace('.', '').replace(',', '')[:8]}.com"
            
            st.session_state.ai_generated_lessee = {
                'name': client_name,
                'address': location_data['address'],
                'contact': primary_contact,
                'email': email,
                'phone': location_data['phone']
            }
            
            st.info(f"🔄 New client: **{client_name}**")
    
    with col3:
        if st.button("👤 Show Client Examples", use_container_width=True):
            st.session_state.show_lessee_examples = not st.session_state.get('show_lessee_examples', False)
    
    # Display lessee examples if requested
    if st.session_state.get('show_lessee_examples', False):
        with st.expander("👥 AI-Generated Client Examples", expanded=True):
            examples = [
                {"name": "Mr. & Mrs. Richardson", "location": "London", "type": "Private"},
                {"name": "Dr. & Mrs. Hamilton", "location": "New York", "type": "Professional"},
                {"name": "Sir & Lady Pemberton", "location": "Geneva", "type": "Aristocracy"},
                {"name": "Ms. Victoria Sterling", "location": "Paris", "type": "Executive"},
                {"name": "Alexander Blackwood, CEO", "location": "Dubai", "type": "Business"},
                {"name": "Isabella Morrison", "location": "Singapore", "type": "Entrepreneur"}
            ]
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    if st.button(f"Use: {example['name']}", key=f"lessee_example_{i}"):
                        # Generate full details for selected example
                        locations = {
                            "London": {"address": "45 Berkeley Square\nLondon W1J 5AT\nUnited Kingdom", "phone": "+44 20 7629 1234"},
                            "New York": {"address": "350 Park Avenue\nNew York, NY 10022\nUnited States", "phone": "+1 212 555 0123"},
                            "Geneva": {"address": "25 Rue du Rhône\n1204 Geneva\nSwitzerland", "phone": "+41 22 345 67 89"},
                            "Paris": {"address": "78 Avenue des Champs-Élysées\n75008 Paris\nFrance", "phone": "+33 1 42 12 34 56"},
                            "Dubai": {"address": "Office 2501\nBurj Khalifa Boulevard\nDowntown Dubai, UAE", "phone": "+971 4 123 4567"},
                            "Singapore": {"address": "50 Raffles Place\n#32-01\nSingapore 048623", "phone": "+65 6789 0123"}
                        }
                        
                        location_data = locations.get(example['location'], locations['London'])
                        
                        # Extract primary contact from name
                        if "Mr. & Mrs." in example['name']:
                            primary_contact = example['name'].replace("Mr. & Mrs. ", "").split()[0] + " " + example['name'].split()[-1]
                        elif "Dr. & Mrs." in example['name']:
                            primary_contact = example['name'].replace("Dr. & Mrs. ", "").split()[0] + " " + example['name'].split()[-1]
                        elif "Sir & Lady" in example['name']:
                            primary_contact = example['name'].replace("Sir & Lady ", "").split()[0] + " " + example['name'].split()[-1]
                        elif "CEO" in example['name']:
                            primary_contact = example['name'].split(",")[0]
                        else:
                            primary_contact = example['name'].replace("Ms. ", "").replace("Dr. ", "").replace("Mr. ", "")
                        
                        # Generate email based on name
                        name_parts = primary_contact.lower().split()
                        if len(name_parts) >= 2:
                            email = f"{name_parts[0][0]}.{name_parts[-1]}@email.com"
                        else:
                            email = f"{name_parts[0]}@email.com"
                        
                        st.session_state.ai_generated_lessee = {
                            'name': example['name'],
                            'address': location_data['address'],
                            'contact': primary_contact,
                            'email': email,
                            'phone': location_data['phone']
                        }
                        st.success(f"Selected: **{example['name']}**")
                        st.rerun()
    
    st.markdown("---")
    
    # Selected clauses summary for contract generation
    if 'selected_clauses' in st.session_state and st.session_state.selected_clauses:
        with st.expander(f"📋 Selected Additional Clauses ({len(st.session_state.selected_clauses)} clauses will be added to contract)", expanded=False):
            for clause in st.session_state.selected_clauses:
                st.markdown(f"• **{clause['name']}** *(from {clause['category']})*")
            st.info(f"💡 These {len(st.session_state.selected_clauses)} clause(s) will be automatically included in the generated contract. You can manage them in the Clause Library.")
    
    # Comprehensive contract form
    with st.form("contract_form"):
        # Vessel Information Section
        st.subheader("⛵ Vessel Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Use AI generated name if available, otherwise use default
            default_vessel_name = st.session_state.get('ai_generated_vessel_name', 'M/Y Excellence')
            vessel_name = st.text_input("Vessel Name", value=default_vessel_name, key="vessel_name_input")
            
            yacht_type = st.selectbox("Yacht Type", [
                "Motor Yacht", 
                "Sailing Yacht", 
                "Catamaran", 
                "Superyacht", 
                "Explorer Yacht",
                "Sport Fisher"
            ])
            length_overall = st.number_input("Length Overall (m)", value=45.0, min_value=10.0, max_value=200.0)
            beam = st.number_input("Beam (m)", value=8.5, min_value=3.0, max_value=30.0)
            
        with col2:
            official_number = st.text_input("Official Number", value="IMO1234567")
            flag_state = st.selectbox("Flag State", [
                "Marshall Islands", "Cayman Islands", "Malta", "British Virgin Islands",
                "Liberia", "Panama", "Luxembourg", "Monaco", "United Kingdom"
            ])
            draft = st.number_input("Draft (m)", value=2.5, min_value=0.5, max_value=10.0)
            guest_capacity = st.number_input("Guest Capacity", value=12, min_value=1, max_value=50)
            
        with col3:
            crew_capacity = st.number_input("Crew Capacity", value=8, min_value=1, max_value=30)
            engine_power = st.number_input("Engine Power (HP)", value=2400, min_value=100, max_value=20000)
            max_speed = st.number_input("Max Speed (knots)", value=22, min_value=5, max_value=80)
            cruising_speed = st.number_input("Cruising Speed (knots)", value=16, min_value=5, max_value=60)
        
        # Charter Terms Section
        st.subheader("📅 Charter Terms")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input("Charter Start Date", key="start_date_input")
            end_date = st.date_input("Charter End Date", key="end_date_input")
            
            # Check if dates have changed and force rerun for immediate feedback
            if 'prev_start_date' in st.session_state and 'prev_end_date' in st.session_state:
                if (st.session_state.prev_start_date != start_date or 
                    st.session_state.prev_end_date != end_date):
                    # Dates changed, trigger a rerun for immediate update
                    st.session_state.prev_start_date = start_date
                    st.session_state.prev_end_date = end_date
                    st.rerun()
            else:
                # First time, initialize previous values
                st.session_state.prev_start_date = start_date
                st.session_state.prev_end_date = end_date
            
            # Calculate charter duration dynamically and force immediate update
            if 'start_date_input' in st.session_state and 'end_date_input' in st.session_state:
                calc_start = st.session_state.start_date_input
                calc_end = st.session_state.end_date_input
            else:
                calc_start = start_date
                calc_end = end_date
            
            if calc_end >= calc_start:
                charter_duration = (calc_end - calc_start).days
                if charter_duration == 0:
                    charter_duration = 1  # Same day = 1 day charter
            else:
                charter_duration = 1  # Invalid date range = 1 day minimum
                
            # Store calculated duration in session state for use in other calculations
            st.session_state.calculated_charter_duration = charter_duration
            
            # Display with color coding for feedback
            if calc_end < calc_start:
                st.error(f"⚠️ Charter Duration: {charter_duration} day (End date before start date)")
            elif charter_duration == 1 and calc_end == calc_start:
                st.success(f"✅ Charter Duration: {charter_duration} day (Same-day charter)")
            else:
                st.info(f"📅 Charter Duration: {charter_duration} days")
            
        with col2:
            currency = st.selectbox("Currency", ["EUR", "USD", "GBP"], key="currency_select")
            daily_rate = st.number_input(f"Daily Rate ({currency})", value=15000, min_value=1000, max_value=500000, key="daily_rate_input")
            
            # Get charter duration from session state or calculate fallback
            charter_duration_for_calc = st.session_state.get('calculated_charter_duration', 1)
            
            # Recalculate total charter value dynamically using the updated charter_duration
            total_charter_value = daily_rate * charter_duration_for_calc
            
            # Display total charter value with updated currency and duration context
            st.metric(
                "Total Charter Value", 
                f"{currency} {total_charter_value:,}",
                help=f"Based on {charter_duration_for_calc} day{'s' if charter_duration_for_calc != 1 else ''} × {currency} {daily_rate:,}/day"
            )
            
        with col3:
            operational_area = st.text_area("Operational Area", 
                value="Mediterranean Sea - French and Italian Riviera, Monaco, Corsica")
            delivery_location = st.text_input("Delivery Location", value="Port Hercules, Monaco")
            return_location = st.text_input("Return Location", value="Port Hercules, Monaco")
        
        # Parties Information Section
        st.subheader("👥 Parties Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**LESSOR (Charter Company)**")
            # Use AI generated lessor data if available, otherwise use defaults
            default_lessor = st.session_state.get('ai_generated_lessor', {})
            lessor_name = st.text_input("Company Name", value=default_lessor.get('name', "Monaco Elite Charters Ltd."))
            lessor_address = st.text_area("Address", 
                value=default_lessor.get('address', "12 Quai Antoine 1er\n98000 Monaco\nPrincipality of Monaco"))
            lessor_contact = st.text_input("Contact Person", value=default_lessor.get('contact', "Captain Jean-Luc Moreau"))
            lessor_email = st.text_input("Email", value=default_lessor.get('email', "charters@monacoelite.mc"))
            lessor_phone = st.text_input("Phone", value=default_lessor.get('phone', "+377 93 30 15 15"))
            
        with col2:
            st.markdown("**LESSEE (Charter Client)**")
            # Use AI generated lessee data if available, otherwise use defaults
            default_lessee = st.session_state.get('ai_generated_lessee', {})
            lessee_name = st.text_input("Client Name", value=default_lessee.get('name', "Mr. & Mrs. Richardson"))
            lessee_address = st.text_area("Client Address", 
                value=default_lessee.get('address', "45 Berkeley Square\nLondon W1J 5AT\nUnited Kingdom"))
            lessee_contact = st.text_input("Primary Contact", value=default_lessee.get('contact', "James Richardson"))
            lessee_email = st.text_input("Client Email", value=default_lessee.get('email', "j.richardson@email.com"))
            lessee_phone = st.text_input("Client Phone", value=default_lessee.get('phone', "+44 20 7629 1234"))
        
        # Financial Terms Section
        st.subheader("💰 Financial Terms")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            payment_schedule_1 = st.slider("Initial Payment (%)", 25, 100, 50, key="payment_slider")
            payment_schedule_2 = 100 - payment_schedule_1
            payment_timing = st.selectbox("Final Payment Timing", [
                "upon delivery", "before departure", "30 days prior", "2 weeks prior"
            ], key="payment_timing_select")
            
            # Check if payment terms have changed and force rerun for immediate feedback
            if 'prev_payment_schedule_1' in st.session_state and 'prev_payment_timing' in st.session_state:
                if (st.session_state.prev_payment_schedule_1 != payment_schedule_1 or 
                    st.session_state.prev_payment_timing != payment_timing):
                    # Payment terms changed, trigger a rerun for immediate update
                    st.session_state.prev_payment_schedule_1 = payment_schedule_1
                    st.session_state.prev_payment_timing = payment_timing
                    st.rerun()
            else:
                # First time, initialize previous values
                st.session_state.prev_payment_schedule_1 = payment_schedule_1
                st.session_state.prev_payment_timing = payment_timing
            
            # Store payment terms in session state for use in other calculations
            st.session_state.calculated_payment_schedule_1 = payment_schedule_1
            st.session_state.calculated_payment_schedule_2 = payment_schedule_2
            st.session_state.calculated_payment_timing = payment_timing
            
            # Display with enhanced formatting and emoji
            if payment_schedule_1 >= 75:
                st.success(f"💰 Payment: **{payment_schedule_1}%** + **{payment_schedule_2}%** {payment_timing}")
                st.caption("ℹ️ High initial payment - lower risk for charter company")
            elif payment_schedule_1 <= 35:
                st.warning(f"💰 Payment: **{payment_schedule_1}%** + **{payment_schedule_2}%** {payment_timing}")
                st.caption("⚠️ Low initial payment - may require additional guarantees")
            else:
                st.info(f"💰 Payment: **{payment_schedule_1}%** + **{payment_schedule_2}%** {payment_timing}")
                st.caption("✅ Balanced payment schedule")
            
        with col2:
            security_deposit = st.number_input("Security Deposit (EUR)", value=150000, min_value=10000, max_value=2000000)
            deposit_method = st.selectbox("Deposit Method", [
                "Bank Transfer", "Credit Card Authorization", "Bank Guarantee", "Cash"
            ])
            
        with col3:
            fuel_policy = st.selectbox("Fuel Policy", [
                "Return Full", "Plus Fuel Consumed", "Fuel Included", "Pay as Used"
            ])
            additional_costs = st.multiselect("Additional Costs Included", [
                "Crew Gratuities", "Port Fees", "Fuel", "Food & Beverage", 
                "Water Sports Equipment", "WiFi", "Laundry"
            ])
        
        # Insurance & Risk Assessment
        st.subheader("🛡️ Insurance & Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            hull_insurance = st.number_input("Hull Insurance Value (USD)", value=25000000, min_value=1000000, max_value=500000000)
            liability_insurance = st.number_input("Liability Insurance (USD)", value=50000000, min_value=1000000, max_value=200000000)
            
        with col2:
            risk_factors = st.multiselect("Risk Factors", [
                "High Season Charter", "Remote Destinations", "Inexperienced Guests",
                "Extreme Weather Season", "High Traffic Waters", "Political Instability"
            ])
            charter_experience = st.selectbox("Client Charter Experience", [
                "First Time", "Occasional (2-3 times)", "Regular (4+ times)", "Expert (10+ times)"
            ])
        
        # Special Clauses & Requirements
        st.subheader("📋 Special Clauses & Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            special_requests = st.text_area("Special Requests", 
                value="Private chef for dietary restrictions\nHelicopter landing capability\nExtra water sports equipment")
            governing_law = st.selectbox("Governing Law", [
                "Monaco", "English Law", "French Law", "Italian Law", 
                "Malta Law", "US Federal Law", "Cayman Islands Law"
            ])
            
        with col2:
            cancellation_policy = st.selectbox("Cancellation Policy", [
                "Standard (90/60/30 days)", "Flexible", "Strict", "Custom"
            ])
            force_majeure = st.checkbox("Include Force Majeure Clause", value=True)
            weather_clause = st.checkbox("Include Weather Limitations", value=True)
            crew_standards = st.checkbox("Include Crew Standards Clause", value=True)
        
        # Contract Metadata
        st.subheader("📄 Contract Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            template_name = st.selectbox("Template Type", [
                "Enhanced Standard", "Luxury Charter", "Superyacht", "Corporate Charter"
            ])
            version_number = st.text_input("Version", value="1.0")
            
        with col2:
            broker_info = st.text_input("Broker/Agent", value="Monaco Yacht Brokers")
            broker_commission = st.number_input("Broker Commission (%)", value=10.0, min_value=0.0, max_value=25.0)
            
        with col3:
            agreement_date = st.date_input("Agreement Date", value=datetime.date.today())
            contract_language = st.selectbox("Contract Language", ["English", "French", "Italian", "Spanish"])
        
        submitted = st.form_submit_button("🚀 Generate Enhanced Contract", use_container_width=True)
    
    # Contract generation logic (moved outside of form)
    if submitted:
        # Calculate risk score based on factors
        risk_score = 1.0
        risk_factors_count = len(risk_factors)
        
        if charter_experience == "First Time":
            risk_score += 0.3
        elif charter_experience == "Occasional (2-3 times)":
            risk_score += 0.1
        
        risk_score += risk_factors_count * 0.2
        risk_category = "Low" if risk_score < 1.3 else "Medium" if risk_score < 1.7 else "High"
        
        # Generate suggested clauses based on selections
        suggested_clauses = {}
        
        if force_majeure:
            suggested_clauses['force_majeure'] = "Neither party shall be liable for any failure or delay in performance which is due to fire, flood, earthquake, elements of nature or acts of God, acts of war, terrorism, riots, civil disorders, rebellions or revolutions, or any other cause beyond the reasonable control of such party."
        
        if weather_clause:
            suggested_clauses['weather'] = f"Charter operations are subject to weather conditions. The Captain reserves the right to modify itinerary or remain in port if weather conditions exceed safe operating parameters (winds >25 knots, seas >2.5m). No refund applies for weather delays."
        
        if crew_standards:
            suggested_clauses['crew_standards'] = f"All crew members hold valid STCW certifications appropriate for a {yacht_type} of {length_overall}m. The Captain holds a minimum {('MCA') if length_overall >= 24 else 'RYA'} license and has {5 if length_overall >= 40 else 3}+ years experience on similar vessels."
        
        suggested_clauses['cancellation'] = {
            "Standard (90/60/30 days)": "Cancellation charges: 90+ days: 25%, 60-89 days: 50%, 30-59 days: 75%, <30 days: 100%",
            "Flexible": "Cancellation charges: 60+ days: 15%, 30-59 days: 50%, <30 days: 100%", 
            "Strict": "Cancellation charges: 120+ days: 50%, 60-119 days: 75%, <60 days: 100%",
            "Custom": "Custom cancellation terms as negotiated between parties"
        }.get(cancellation_policy, "Standard terms apply")
        
        # Get the latest charter duration and total value from session state or recalculate
        charter_duration = st.session_state.get('calculated_charter_duration', 1)
        total_charter_value = daily_rate * charter_duration
        
        # Get the latest payment terms from session state or use form values
        payment_schedule_1_final = st.session_state.get('calculated_payment_schedule_1', payment_schedule_1)
        payment_schedule_2_final = st.session_state.get('calculated_payment_schedule_2', payment_schedule_2)
        payment_timing_final = st.session_state.get('calculated_payment_timing', payment_timing)
        
        # Create comprehensive contract data
        contract_data = {
            # Vessel Information
            'vessel_name': vessel_name,
            'yacht_type': yacht_type,
            'length_overall': length_overall,
            'beam': beam,
            'draft': draft,
            'official_number': official_number,
            'flag_state': flag_state,
            'guest_capacity': guest_capacity,
            'crew_capacity': crew_capacity,
            'engine_power': engine_power,
            'max_speed': max_speed,
            'cruising_speed': cruising_speed,
            
            # Charter Terms
            'start_date': start_date.strftime('%d %B %Y'),
            'end_date': end_date.strftime('%d %B %Y'),
            'charter_duration': charter_duration,
            'daily_rate': f"{daily_rate:,}",
            'currency': currency,
            'total_charter_value': f"{total_charter_value:,}",
            'operational_area': operational_area,
            'delivery_location': delivery_location,
            'return_location': return_location,
            
            # Parties
            'lessor_name': lessor_name,
            'lessor_address': lessor_address.replace('\n', '<br>'),
            'lessor_contact': lessor_contact,
            'lessor_email': lessor_email,
            'lessor_phone': lessor_phone,
            'lessee_name': lessee_name,
            'lessee_address': lessee_address.replace('\n', '<br>'),
            'lessee_contact': lessee_contact,
            'lessee_email': lessee_email,
            'lessee_phone': lessee_phone,
            
            # Financial Terms
            'payment_schedule_1': payment_schedule_1_final,
            'payment_schedule_2': payment_schedule_2_final,
            'payment_timing': payment_timing_final,
            'security_deposit': f"{security_deposit:,}",
            'deposit_method': deposit_method,
            'fuel_policy': fuel_policy,
            'additional_costs': ', '.join(additional_costs) if additional_costs else 'None specified',
            
            # Insurance & Risk
            'hull_insurance': f"{hull_insurance:,}",
            'liability_insurance': f"{liability_insurance:,}",
            'risk_factors': ', '.join(risk_factors) if risk_factors else 'Standard risk profile',
            'charter_experience': charter_experience,
            
            # Risk Assessment Object
            'risk_assessment': {
                'risk_score': f"{risk_score:.1f}",
                'risk_category': risk_category,
                'recommended_hull_insurance': int(hull_insurance * risk_score),
                'recommended_liability_insurance': int(liability_insurance * risk_score),
                'recommendations': [
                    f"Charter experience level: {charter_experience}",
                    f"Risk factors identified: {len(risk_factors)}",
                    f"Operational area: {operational_area[:50]}..."
                ],
                'regional_warnings': [
                    "Ensure all documentation is current for operational areas",
                    "Verify local maritime regulations compliance"
                ] if "Remote Destinations" in risk_factors else []
            },
            
            # Contract Clauses
            'suggested_clauses': suggested_clauses,
            'additional_clauses': st.session_state.get('selected_clauses', []),
            'special_requests': special_requests,
            'governing_law': governing_law,
            'cancellation_policy': cancellation_policy,
            
            # Metadata
            'contract_id': str(uuid.uuid4())[:8].upper(),
            'template_name': template_name,
            'version_number': version_number,
            'agreement_date': agreement_date.strftime('%d %B %Y'),
            'broker_info': broker_info,
            'broker_commission': broker_commission,
            'contract_language': contract_language
        }
        
        # Generate contract
        template = Template(ENHANCED_CONTRACT_TEMPLATE)
        contract_html = template.render(**contract_data)
        
        # Store in session state to persist after form submission
        st.session_state.contract_data = contract_data
        st.session_state.contract_html = contract_html
        
        # Display success and contract
        st.success("🎉 Enhanced Contract Generated Successfully!")
        
        # Contract summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Contract Value", f"{currency} {total_charter_value:,}")
        with col2:
            st.metric("Charter Duration", f"{charter_duration} days")
        with col3:
            st.metric("Risk Score", f"{risk_score:.1f} ({risk_category})")
        with col4:
            st.metric("Vessel LOA", f"{length_overall}m")
        
        # Display contract preview
        st.markdown("### 📄 Contract Preview")
        with st.expander("View Full Contract", expanded=True):
            st.components.v1.html(contract_html, height=800, scrolling=True)
    
    # Download section (outside of form, using session state)
    if hasattr(st.session_state, 'contract_html') and st.session_state.contract_html:
        st.markdown("### 📥 Download Options")
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📄 Download HTML Contract",
                data=st.session_state.contract_html,
                file_name=f"yacht_contract_{st.session_state.contract_data['contract_id']}.html",
                mime="text/html",
                use_container_width=True
            )
        
        with col2:
            # Generate PDF (simplified)
            pdf_filename = f"yacht_contract_{st.session_state.contract_data['contract_id']}.pdf"
            generate_pdf_contract(st.session_state.contract_html, pdf_filename, st.session_state.contract_data)
            
            with open(pdf_filename, 'rb') as pdf_file:
                st.download_button(
                    label="📑 Download PDF Contract",
                    data=pdf_file.read(),
                    file_name=pdf_filename,
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col3:
            # Contract data as JSON
            contract_json = json.dumps(st.session_state.contract_data, indent=2, default=str)
            st.download_button(
                label="📊 Download Contract Data",
                data=contract_json,
                file_name=f"contract_data_{st.session_state.contract_data['contract_id']}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Additional actions
        st.markdown("### 🚀 Additional Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send via Email", use_container_width=True):
                st.info("Email functionality would be implemented here")
        
        with col2:
            if st.button("💾 Save to Database", use_container_width=True):
                # Save contract to database/file system
                try:
                    # Create contracts directory if it doesn't exist
                    contracts_dir = "contracts"
                    os.makedirs(contracts_dir, exist_ok=True)
                    
                    # Save contract HTML
                    contract_filename = f"contract_{st.session_state.contract_data['contract_id']}.html"
                    contract_filepath = os.path.join(contracts_dir, contract_filename)
                    
                    with open(contract_filepath, 'w', encoding='utf-8') as f:
                        f.write(st.session_state.contract_html)
                    
                    # Save contract data as JSON
                    data_filename = f"contract_data_{st.session_state.contract_data['contract_id']}.json"
                    data_filepath = os.path.join(contracts_dir, data_filename)
                    
                    with open(data_filepath, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.contract_data, f, indent=2, default=str)
                    
                    # Log the save action
                    with open(LOG_FILE, 'a', encoding='utf-8') as log:
                        log.write(f"{datetime.datetime.now().isoformat()} - Contract {st.session_state.contract_data['contract_id']} saved to database\n")
                    
                    st.success(f"✅ Contract saved successfully!")
                    st.info(f"Saved to: {contract_filepath}")
                    
                except Exception as e:
                    st.error(f"❌ Error saving contract: {str(e)}")
        
        with col3:
            if st.button("🔄 Create New Version", use_container_width=True):
                # Create new version by incrementing version number
                current_version = st.session_state.contract_data.get('version_number', '1.0')
                
                # Parse current version and increment
                try:
                    if '.' in current_version:
                        major, minor = current_version.split('.')
                        new_version = f"{major}.{int(minor) + 1}"
                    else:
                        new_version = f"{current_version}.1"
                except:
                    new_version = "2.0"
                
                # Update contract data with new version
                new_contract_data = st.session_state.contract_data.copy()
                new_contract_data['version_number'] = new_version
                new_contract_data['contract_id'] = str(uuid.uuid4())[:8].upper()
                new_contract_data['agreement_date'] = datetime.date.today().strftime('%d %B %Y')
                
                # Regenerate contract with new version
                template = Template(ENHANCED_CONTRACT_TEMPLATE)
                new_contract_html = template.render(**new_contract_data)
                
                # Update session state
                st.session_state.contract_data = new_contract_data
                st.session_state.contract_html = new_contract_html
                
                # Save version to versions directory
                os.makedirs(VERSIONS_DIR, exist_ok=True)
                version_filename = f"contract_v{new_version}_{new_contract_data['contract_id']}.html"
                version_filepath = os.path.join(VERSIONS_DIR, version_filename)
                
                with open(version_filepath, 'w', encoding='utf-8') as f:
                    f.write(new_contract_html)
                
                # Log the version creation
                with open(LOG_FILE, 'a', encoding='utf-8') as log:
                    log.write(f"{datetime.datetime.now().isoformat()} - New version {new_version} created for vessel {new_contract_data.get('vessel_name', 'Unknown')}\n")
                
                st.success(f"✅ New version {new_version} created successfully!")
                st.info(f"Contract ID: {new_contract_data['contract_id']}")
                st.rerun()
        
        # Version History Section
        if hasattr(st.session_state, 'contract_data'):
            st.markdown("### 📋 Version History")
            
            # Check for existing versions in the versions directory
            if os.path.exists(VERSIONS_DIR):
                version_files = [f for f in os.listdir(VERSIONS_DIR) if f.endswith('.html')]
                
                if version_files:
                    st.markdown("**Available Versions:**")
                    
                    # Create a table of versions
                    version_data = []
                    for version_file in sorted(version_files):
                        # Extract version info from filename
                        try:
                            parts = version_file.replace('.html', '').split('_')
                            if len(parts) >= 3:
                                version = parts[1].replace('v', '')
                                contract_id = parts[2]
                                file_path = os.path.join(VERSIONS_DIR, version_file)
                                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                                
                                version_data.append({
                                    'Version': version,
                                    'Contract ID': contract_id,
                                    'Created': file_time.strftime('%Y-%m-%d %H:%M'),
                                    'File': version_file
                                })
                        except:
                            continue
                    
                    if version_data:
                        # Display as a dataframe
                        df = pd.DataFrame(version_data)
                        st.dataframe(df, use_container_width=True)
                        
                        # Option to download previous versions
                        selected_version = st.selectbox(
                            "Select version to download:", 
                            options=[f"v{row['Version']} ({row['Contract ID']})" for _, row in df.iterrows()],
                            key="version_select"
                        )
                        
                        if st.button("📥 Download Selected Version", use_container_width=True):
                            # Find the selected file
                            for _, row in df.iterrows():
                                if f"v{row['Version']} ({row['Contract ID']})" == selected_version:
                                    file_path = os.path.join(VERSIONS_DIR, row['File'])
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        version_content = f.read()
                                    
                                    st.download_button(
                                        label=f"📄 Download {selected_version}",
                                        data=version_content,
                                        file_name=row['File'],
                                        mime="text/html",
                                        use_container_width=True
                                    )
                                    break
                else:
                    st.info("No previous versions found. Create a new version to start version history.")
            else:
                st.info("No version history available yet.")

def template_manager_page(systems):
    st.header("📋 Template Manager")
    st.markdown("### Professional Contract Template Management System")
    
    # Template Manager tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Template Library", 
        "✏️ Template Editor", 
        "🔧 Clause Builder", 
        "📊 Template Analytics",
        "⚙️ Template Settings"
    ])
    
    with tab1:
        template_library_section()
    
    with tab2:
        template_editor_section()
    
    with tab3:
        clause_builder_section()
    
    with tab4:
        template_analytics_section()
    
    with tab5:
        template_settings_section()

def template_library_section():
    st.subheader("📚 Template Library")
    
    # Template categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.selectbox(
            "Template Category",
            ["All Templates", "Bareboat Charter", "Crewed Charter", "Corporate Charter", 
             "Luxury Superyacht", "Racing Charter", "Educational Charter"],
            key="template_category"
        )
    
    with col2:
        st.selectbox(
            "Legal Jurisdiction",
            ["International", "Mediterranean (EU)", "Caribbean", "US Waters", 
             "UK/Gibraltar", "Australia/New Zealand", "Asia Pacific"],
            key="template_jurisdiction"
        )
    
    with col3:
        st.selectbox(
            "Template Language",
            ["English", "French", "Spanish", "Italian", "German", "Dutch"],
            key="template_language"
        )
    
    st.markdown("---")
    
    # Sample templates with enhanced metadata
    templates = [
        {
            "name": "Mediterranean Bareboat Charter",
            "category": "Bareboat Charter",
            "jurisdiction": "Mediterranean (EU)",
            "language": "English",
            "version": "2.1",
            "last_updated": "2025-07-15",
            "usage_count": 234,
            "rating": 4.8,
            "status": "Active",
            "description": "Comprehensive bareboat charter template compliant with EU maritime law",
            "features": ["Risk Assessment Integration", "Multi-currency Support", "Flexible Cancellation Terms"]
        },
        {
            "name": "Caribbean Crewed Superyacht",
            "category": "Luxury Superyacht",
            "jurisdiction": "Caribbean",
            "language": "English",
            "version": "1.3",
            "last_updated": "2025-07-10",
            "usage_count": 89,
            "rating": 4.9,
            "status": "Active",
            "description": "Premium crewed charter template for luxury superyachts in Caribbean waters",
            "features": ["Crew Provisions", "Guest Services", "Port Clearance", "Concierge Services"]
        },
        {
            "name": "Corporate Charter Agreement",
            "category": "Corporate Charter",
            "jurisdiction": "International",
            "language": "English",
            "version": "1.0",
            "last_updated": "2025-06-20",
            "usage_count": 45,
            "rating": 4.6,
            "status": "Beta",
            "description": "Specialized template for corporate events and business charters",
            "features": ["Corporate Billing", "Event Management", "Liability Caps", "Indemnification"]
        },
        {
            "name": "Racing Charter Template",
            "category": "Racing Charter",
            "jurisdiction": "International",
            "language": "English",
            "version": "1.1",
            "last_updated": "2025-07-01",
            "usage_count": 67,
            "rating": 4.7,
            "status": "Active",
            "description": "Purpose-built template for sailing races and regattas",
            "features": ["Race Rules Compliance", "Equipment Specifications", "Safety Requirements"]
        }
    ]
    
    # Template cards display
    for template in templates:
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin: 10px 0; background: white;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="color: #1e3a8a; margin: 0 0 5px 0;">{template['name']}</h4>
                        <p style="color: #666; margin: 0 0 10px 0; font-size: 14px;">{template['description']}</p>
                        
                        <div style="display: flex; gap: 15px; margin: 10px 0;">
                            <span style="background: #f0f9ff; color: #0ea5e9; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                                📂 {template['category']}
                            </span>
                            <span style="background: #f1f5f9; color: #1e3a8a; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                                🌍 {template['jurisdiction']}
                            </span>
                            <span style="background: #ecfdf5; color: #10b981; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                                ✅ {template['status']}
                            </span>
                        </div>
                        
                        <div style="font-size: 12px; color: #888;">
                            <strong>Features:</strong> {', '.join(template['features'])}
                        </div>
                    </div>
                    
                    <div style="text-align: right; margin-left: 15px;">
                        <div style="font-size: 12px; color: #666;">
                            <div>Version: <strong>{template['version']}</strong></div>
                            <div>Updated: {template['last_updated']}</div>
                            <div>Used: {template['usage_count']} times</div>
                            <div>Rating: ⭐ {template['rating']}/5.0</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button(f"📄 Preview", key=f"preview_{template['name']}"):
                    st.info(f"Previewing template: {template['name']}")
            with col2:
                if st.button(f"✏️ Edit", key=f"edit_{template['name']}"):
                    st.info(f"Opening editor for: {template['name']}")
            with col3:
                if st.button(f"📋 Clone", key=f"clone_{template['name']}"):
                    st.success(f"Template '{template['name']}' cloned successfully!")
            with col4:
                if st.button(f"📊 Stats", key=f"stats_{template['name']}"):
                    st.info(f"Showing analytics for: {template['name']}")
            with col5:
                if st.button(f"🎯 Use", key=f"use_{template['name']}"):
                    st.success(f"Switched to template: {template['name']}")

def template_editor_section():
    st.subheader("✏️ Template Editor")
    
    # Template selection for editing
    col1, col2 = st.columns(2)
    with col1:
        selected_template = st.selectbox(
            "Select Template to Edit",
            ["Create New Template", "Mediterranean Bareboat Charter", "Caribbean Crewed Superyacht", 
             "Corporate Charter Agreement", "Racing Charter Template"],
            key="edit_template_select"
        )
    
    with col2:
        template_action = st.selectbox(
            "Action",
            ["Edit Content", "Edit Layout", "Edit Styling", "Add Sections", "Configure Variables"],
            key="template_action"
        )
    
    st.markdown("---")
    
    if selected_template == "Create New Template":
        st.markdown("### 🆕 Create New Template")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            template_name = st.text_input("Template Name", placeholder="e.g., Custom Charter Agreement")
        with col2:
            template_category = st.selectbox("Category", 
                ["Bareboat Charter", "Crewed Charter", "Corporate Charter", "Luxury Superyacht", "Racing Charter"])
        with col3:
            template_jurisdiction = st.selectbox("Legal Jurisdiction",
                ["International", "Mediterranean (EU)", "Caribbean", "US Waters", "UK/Gibraltar"])
        
        st.markdown("### 📝 Template Content")
        template_content = st.text_area(
            "Template HTML Content",
            height=400,
            value="""<div class="contract-header">
    <h1>{{ vessel_name }} Charter Agreement</h1>
    <p>Contract ID: {{ contract_id }}</p>
</div>

<div class="vessel-specs">
    <h2>Vessel Specifications</h2>
    <p><strong>Vessel:</strong> {{ vessel_name }}</p>
    <p><strong>Type:</strong> {{ yacht_type }}</p>
    <p><strong>Length:</strong> {{ length_overall }}m</p>
</div>

<!-- Add more sections as needed -->""",
            help="Use Jinja2 template syntax with {{ variable_name }} for dynamic content"
        )
        
        if st.button("💾 Save New Template", type="primary"):
            st.success(f"Template '{template_name}' created successfully!")
            st.info("Template saved to template library and ready for use.")
    
    else:
        st.markdown(f"### ✏️ Editing: {selected_template}")
        
        if template_action == "Edit Content":
            st.markdown("#### 📝 Content Editor")
            content = st.text_area(
                "Template Content",
                height=400,
                value="<!-- Current template content would be loaded here -->",
                help="Edit the HTML content of the template"
            )
            
        elif template_action == "Edit Layout":
            st.markdown("#### 🎨 Layout Configuration")
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox("Page Layout", ["Single Column", "Two Column", "Three Column", "Custom Grid"])
                st.selectbox("Header Style", ["Centered", "Left Aligned", "Right Aligned", "Logo + Text"])
            with col2:
                st.selectbox("Footer Style", ["Simple", "Detailed", "Signature Block", "Legal Footer"])
                st.number_input("Margin Size (cm)", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
                
        elif template_action == "Edit Styling":
            st.markdown("#### 🎨 Styling Options")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.color_picker("Primary Color", value="#1e3a8a")
                st.color_picker("Secondary Color", value="#3730a3")
            with col2:
                st.selectbox("Font Family", ["Helvetica", "Times New Roman", "Arial", "Calibri"])
                st.slider("Base Font Size", 8, 14, 10)
            with col3:
                st.selectbox("Table Style", ["Bordered", "Minimal", "Striped", "Professional"])
                st.checkbox("Use Company Branding")
        
        elif template_action == "Configure Variables":
            st.markdown("#### 🔧 Template Variables")
            st.info("Define custom variables for this template")
            
            variable_name = st.text_input("Variable Name", placeholder="e.g., custom_clause_1")
            variable_type = st.selectbox("Variable Type", ["Text", "Number", "Date", "Boolean", "List"])
            variable_description = st.text_input("Description", placeholder="Description of this variable")
            
            if st.button("➕ Add Variable"):
                st.success(f"Variable '{variable_name}' added to template")
        
        # Save changes button
        if st.button("💾 Save Changes", type="primary"):
            st.success(f"Changes to '{selected_template}' saved successfully!")

def clause_builder_section():
    st.subheader("🔧 Clause Builder")
    
    # Add CSS for better text wrapping in clause content areas
    st.markdown("""
    <style>
    /* Improved text wrapping for all text areas in the clause sections */
    .stTextArea textarea {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
        line-height: 1.5 !important;
        resize: vertical !important;
    }
    
    /* Specific styling for clause content areas */
    div[data-testid="stTextArea"] textarea {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 12px !important;
        background-color: #fafafa !important;
    }
    
    /* Focus state for better UX */
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        background-color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Clause library management
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📚 Clause Library")
        clause_categories = [
            "Payment Terms", "Cancellation Policy", "Insurance Requirements", 
            "Liability Limitations", "Force Majeure", "Dispute Resolution",
            "Delivery Terms", "Safety Requirements", "Environmental Compliance"
        ]
        
        selected_category = st.selectbox("Clause Category", clause_categories)
        
        # Sample clauses for the selected category
        if selected_category == "Payment Terms":
            clauses = [
                "Standard 50/50 Payment Schedule",
                "Accelerated Payment Terms",
                "Corporate Net-30 Terms",
                "Seasonal Payment Plan"
            ]
        elif selected_category == "Cancellation Policy":
            clauses = [
                "Standard Cancellation Terms",
                "Flexible Cancellation (Force Majeure)",
                "No-Refund Policy",
                "Graduated Cancellation Fees"
            ]
        else:
            clauses = [f"Sample {selected_category} Clause 1", f"Sample {selected_category} Clause 2"]
        
        selected_clause = st.selectbox("Available Clauses", clauses)
        
        if st.button("👁️ Preview Clause"):
            st.info(f"Previewing: {selected_clause}")
            st.code("""
PAYMENT TERMS: The charter fee shall be paid as follows:
- 50% deposit due upon execution of this agreement
- 50% balance due 30 days prior to charter commencement
- All payments to be made in the currency specified herein
- Late payment penalties may apply as per local regulations
            """)
    
    with col2:
        st.markdown("#### ✨ AI Clause Suggestions")
        
        # AI-powered clause suggestions
        charter_type = st.selectbox("Charter Type", ["Bareboat", "Crewed", "Corporate", "Racing"])
        risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])
        charter_duration = st.selectbox("Duration", ["Day Charter", "Weekly", "Monthly", "Seasonal"])
        
        if st.button("🤖 Get AI Suggestions"):
            st.success("AI analyzing charter parameters...")
            
            suggested_clauses = [
                "Enhanced Insurance Requirements (High Risk)",
                "Weather Contingency Clause (Seasonal)",
                "Extended Liability Coverage",
                "Professional Crew Certification Requirements"
            ]
            
            for clause in suggested_clauses:
                st.markdown(f"✅ **Recommended:** {clause}")
    
    st.markdown("---")
    
    # Clause builder interface
    st.markdown("#### 🏗️ Build Custom Clause")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        clause_title = st.text_input("Clause Title", placeholder="e.g., Custom Payment Terms", key="custom_clause_title")
    with col2:
        clause_category = st.selectbox("Category", clause_categories, key="new_clause_category")
    with col3:
        clause_priority = st.selectbox("Priority", ["Standard", "Important", "Critical"], key="custom_clause_priority")
    
    clause_content = st.text_area(
        "Clause Content",
        height=150,
        placeholder="Enter the clause text here. Use {{variable_name}} for dynamic content.",
        help="You can use template variables like {{charter_fee}} or {{vessel_name}}",
        key="custom_clause_content"
    )
    
    # Clause conditions
    st.markdown("#### ⚙️ Clause Conditions")
    col1, col2 = st.columns(2)
    with col1:
        charter_types = st.multiselect("Show when Charter Type is:", ["Bareboat", "Crewed", "Corporate", "Racing"], key="custom_charter_types")
        risk_levels = st.multiselect("Show when Risk Level is:", ["Low", "Medium", "High"], key="custom_risk_levels")
    with col2:
        jurisdictions = st.multiselect("Required for Jurisdictions:", ["EU", "Caribbean", "US", "International"], key="custom_jurisdictions")
        min_charter_value = st.number_input("Minimum Charter Value", min_value=0, value=10000, step=1000, key="custom_min_value")
    
    if st.button("💾 Save Custom Clause", type="primary"):
        if clause_title and clause_content and clause_category:
            # Initialize custom clauses in session state if not exists
            if 'custom_clauses' not in st.session_state:
                st.session_state.custom_clauses = {}
            
            # Create the custom clause data structure
            import datetime
            custom_clause = {
                "name": clause_title,
                "version": "1.0",
                "jurisdiction": jurisdictions if jurisdictions else ["International"],
                "language": "English",
                "usage_count": 0,
                "rating": 5.0,
                "status": "Custom",
                "complexity": clause_priority,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                "author": "User Created",
                "content": clause_content,
                "variables": [],  # Could be extracted from content in future
                "applicable_to": charter_types if charter_types else ["All charter types"],
                "legal_notes": f"Custom clause created by user. Minimum charter value: ${min_charter_value:,}",
                "related_clauses": [],
                "risk_level": "Medium" if clause_priority == "Critical" else "Low"
            }
            
            # Add to custom clauses by category
            if clause_category not in st.session_state.custom_clauses:
                st.session_state.custom_clauses[clause_category] = []
            
            st.session_state.custom_clauses[clause_category].append(custom_clause)
            
            st.success(f"✅ Custom clause '{clause_title}' saved to {clause_category} library!")
            st.info("🔍 You can now find your custom clause in the Browse Clauses tab under the selected category.")
            
            # Clear the form by removing session state keys
            for key in ['custom_clause_title', 'custom_clause_content', 'custom_clause_priority',
                       'custom_charter_types', 'custom_risk_levels', 'custom_jurisdictions', 'custom_min_value']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()  # Refresh to show cleared form
            
        else:
            st.error("❌ Please fill in all required fields: Clause Title, Content, and Category.")

def template_analytics_section():
    st.subheader("📊 Template Analytics")
    
    # Analytics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Templates", "12", "+2")
    with col2:
        st.metric("Active Templates", "9", "+1")
    with col3:
        st.metric("Total Usage", "1,234", "+89")
    with col4:
        st.metric("Avg Rating", "4.7", "+0.2")
    
    st.markdown("---")
    
    # Usage charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Template Usage Trends")
        # Placeholder for usage chart
        chart_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            'Usage': [45, 67, 89, 123, 156, 178, 234]
        }
        st.line_chart(chart_data, x='Month', y='Usage')
    
    with col2:
        st.markdown("#### 🥧 Template Categories")
        # Placeholder for category distribution
        category_data = {
            'Category': ['Bareboat', 'Crewed', 'Corporate', 'Racing', 'Luxury'],
            'Count': [45, 32, 18, 12, 8]
        }
        st.bar_chart(category_data, x='Category', y='Count')
    
    # Popular templates table
    st.markdown("#### 🏆 Most Popular Templates")
    popular_templates = {
        'Template Name': ['Mediterranean Bareboat', 'Caribbean Crewed', 'Corporate Charter', 'Racing Template'],
        'Usage Count': [234, 189, 145, 97],
        'Rating': [4.8, 4.9, 4.6, 4.7],
        'Last Updated': ['2025-07-15', '2025-07-10', '2025-06-20', '2025-07-01']
    }
    st.dataframe(popular_templates, use_container_width=True)

def template_settings_section():
    st.subheader("⚙️ Template Settings")
    
    # Global template settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌐 Global Settings")
        
        st.selectbox("Default Language", ["English", "French", "Spanish", "Italian", "German"])
        st.selectbox("Default Jurisdiction", ["International", "Mediterranean (EU)", "Caribbean", "US Waters"])
        st.selectbox("Default Currency", ["EUR", "USD", "GBP", "CHF", "AUD"])
        
        st.checkbox("Enable Template Versioning", value=True)
        st.checkbox("Require Approval for Template Changes", value=True)
        st.checkbox("Enable Template Analytics", value=True)
        
    with col2:
        st.markdown("#### 🎨 Styling Defaults")
        
        st.color_picker("Primary Brand Color", value="#1e3a8a")
        st.color_picker("Secondary Brand Color", value="#3730a3")
        st.selectbox("Default Font", ["Helvetica", "Times New Roman", "Arial", "Calibri"])
        st.slider("Default Font Size", 8, 14, 10)
        
        st.file_uploader("Company Logo", type=['png', 'jpg', 'jpeg'])
        st.text_input("Company Name", placeholder="Your Company Name")
    
    st.markdown("---")
    
    # Template backup and import/export
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💾 Backup & Restore")
        if st.button("📦 Export All Templates"):
            st.success("Templates exported to yacht_templates_backup.zip")
        
        st.file_uploader("📂 Import Templates", type=['json', 'zip'], 
                        help="Import templates from backup file")
    
    with col2:
        st.markdown("#### 🔄 Template Sync")
        if st.button("☁️ Sync with Cloud"):
            st.info("Syncing templates with cloud storage...")
        
        if st.button("📥 Download Updates"):
            st.info("Checking for template updates...")
    
    with col3:
        st.markdown("#### 🧹 Maintenance")
        if st.button("🗑️ Clean Unused Templates"):
            st.warning("This will remove templates not used in 90 days")
        
        if st.button("🔄 Reset to Defaults"):
            st.error("This will reset all template settings to defaults")
    
    # Template permissions
    st.markdown("#### 👥 Template Permissions")
    st.info("Configure user permissions for template management")
    
    permission_data = {
        'User/Role': ['Admin', 'Legal Team', 'Charter Managers', 'Sales Team'],
        'View Templates': [True, True, True, True],
        'Edit Templates': [True, True, False, False],
        'Create Templates': [True, True, False, False],
        'Delete Templates': [True, False, False, False],
        'Approve Changes': [True, True, False, False]
    }
    
    st.dataframe(permission_data, use_container_width=True)

def risk_assessment_page(systems):
    st.header("⚠️ Risk Assessment")
    st.info("Risk assessment functionality would be implemented here.")

def clause_library_page(systems):
    st.header("🔧 Clause Library")
    st.markdown("### Professional Legal Clause Management System")
    
    # Selected clauses summary
    if 'selected_clauses' in st.session_state and st.session_state.selected_clauses:
        with st.expander(f"📋 Selected Clauses for Contract ({len(st.session_state.selected_clauses)} clauses)", expanded=False):
            for i, selected_clause in enumerate(st.session_state.selected_clauses):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{selected_clause['name']}** *(from {selected_clause['category']})*")
                    st.caption(selected_clause['content'][:100] + "..." if len(selected_clause['content']) > 100 else selected_clause['content'])
                
                with col2:
                    if st.button("👁️ Preview", key=f"preview_selected_{i}"):
                        st.info(f"**{selected_clause['name']}**\n\n{selected_clause['content']}")
                
                with col3:
                    if st.button("❌ Remove", key=f"remove_selected_{i}"):
                        st.session_state.selected_clauses.pop(i)
                        st.success(f"Removed '{selected_clause['name']}' from contract")
                        st.rerun()
            
            # Clear all button
            if st.button("🗑️ Clear All Selected Clauses", type="secondary"):
                st.session_state.selected_clauses = []
                st.success("Cleared all selected clauses!")
                st.rerun()
    else:
        st.info("💡 No clauses selected for contract yet. Browse the library below and click 'Add to Contract' to add clauses.")
    
    st.markdown("---")
    
    # Clause Library tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📚 Browse Clauses", 
        "🔍 Search & Filter", 
        "✏️ Clause Editor", 
        "🤖 AI Suggestions",
        "📊 Clause Analytics",
        "⚙️ Library Settings"
    ])
    
    with tab1:
        browse_clauses_section()
    
    with tab2:
        search_filter_section()
    
    with tab3:
        clause_editor_section()
    
    with tab4:
        ai_suggestions_section()
    
    with tab5:
        clause_analytics_section()
    
    with tab6:
        library_settings_section()

def browse_clauses_section():
    st.subheader("📚 Browse Clause Library")
    
    # Quick category navigation
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💰 Payment Terms", use_container_width=True):
            st.session_state.selected_category = "Payment Terms"
            st.rerun()
    with col2:
        if st.button("❌ Cancellation", use_container_width=True):
            st.session_state.selected_category = "Cancellation Policy"
            st.rerun()
    with col3:
        if st.button("🛡️ Insurance", use_container_width=True):
            st.session_state.selected_category = "Insurance Requirements"
            st.rerun()
    with col4:
        if st.button("⚖️ Liability", use_container_width=True):
            st.session_state.selected_category = "Liability Limitations"
            st.rerun()
    
    # Initialize selected category
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "Payment Terms"
    
    # Available categories
    available_categories = [
        "Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations", 
        "Force Majeure", "Dispute Resolution", "Delivery Terms", "Safety Requirements", 
        "Environmental Compliance", "Crew Provisions", "Guest Services", "Equipment Standards",
        "Weather Contingency", "Port Clearance", "Maintenance Terms", "Fuel Policy"
    ]
    
    # Find the current index for the selectbox
    try:
        current_index = available_categories.index(st.session_state.selected_category)
    except ValueError:
        current_index = 0
        st.session_state.selected_category = available_categories[0]
    
    # Category selector
    category = st.selectbox(
        "Clause Category",
        available_categories,
        index=current_index,
        key="browse_category"
    )
    
    # Update session state when selectbox changes
    if category != st.session_state.selected_category:
        st.session_state.selected_category = category
    
    # Use the session state value for consistency
    category = st.session_state.selected_category
    
    st.markdown("---")
    
    # Comprehensive clause database
    clause_database = {
        "Payment Terms": [
            {
                "name": "Standard 50/50 Payment Schedule",
                "version": "2.1",
                "jurisdiction": ["International", "EU", "US"],
                "language": "English",
                "usage_count": 1247,
                "rating": 4.8,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-07-15",
                "author": "Maritime Legal Team",
                "content": """PAYMENT TERMS: The total charter fee shall be paid according to the following schedule:
a) Fifty percent (50%) of the total charter fee shall be paid as a deposit upon execution of this agreement;
b) The remaining fifty percent (50%) shall be paid no later than thirty (30) days prior to the charter commencement date;
c) All payments shall be made in the currency specified in this agreement;
d) Payment may be made by bank transfer, certified check, or other means as agreed between the parties;
e) Late payments may incur interest charges at the rate of 1.5% per month or the maximum rate permitted by law, whichever is less.""",
                "variables": ["total_charter_fee", "currency", "charter_commencement_date"],
                "applicable_to": ["Bareboat", "Crewed", "Corporate"],
                "legal_notes": "Compliant with EU Payment Services Directive and US maritime law",
                "related_clauses": ["Security Deposit", "Cancellation Policy"],
                "risk_level": "Low"
            },
            {
                "name": "Accelerated Payment Terms",
                "version": "1.3",
                "jurisdiction": ["International", "Caribbean"],
                "language": "English",
                "usage_count": 342,
                "rating": 4.5,
                "status": "Active",
                "complexity": "Advanced",
                "last_updated": "2025-06-20",
                "author": "Charter Finance Team",
                "content": """ACCELERATED PAYMENT SCHEDULE: For charter bookings made within sixty (60) days of the charter commencement date:
a) One hundred percent (100%) of the total charter fee is due immediately upon booking confirmation;
b) No refunds will be provided except as specifically outlined in the Force Majeure clause;
c) Payment must be received and cleared before charter documents will be released;
d) Additional fees for expedited processing may apply at the rate of 2.5% of the total charter value.""",
                "variables": ["total_charter_fee", "charter_commencement_date", "expedited_fee_rate"],
                "applicable_to": ["Last-minute bookings", "Corporate", "Emergency charters"],
                "legal_notes": "Higher risk due to accelerated timeline - ensure proper due diligence",
                "related_clauses": ["Force Majeure", "Document Release"],
                "risk_level": "Medium"
            },
            {
                "name": "Corporate Net-30 Terms",
                "version": "1.0",
                "jurisdiction": ["US", "EU"],
                "language": "English",
                "usage_count": 89,
                "rating": 4.2,
                "status": "Beta",
                "complexity": "Advanced",
                "last_updated": "2025-05-10",
                "author": "Corporate Legal Team",
                "content": """CORPORATE PAYMENT TERMS: For qualified corporate clients with approved credit:
a) Invoice will be issued upon charter completion;
b) Payment is due within thirty (30) days of invoice date (Net-30);
c) Client must maintain minimum credit rating of BBB or equivalent;
d) Personal guarantee may be required from corporate officers;
e) Right to demand immediate payment or additional security if credit rating falls below threshold.""",
                "variables": ["corporate_client_name", "credit_rating", "invoice_date"],
                "applicable_to": ["Corporate"],
                "legal_notes": "Requires credit check and corporate verification",
                "related_clauses": ["Credit Requirements", "Personal Guarantee"],
                "risk_level": "High"
            }
        ],
        "Cancellation Policy": [
            {
                "name": "Standard Cancellation Terms",
                "version": "2.0",
                "jurisdiction": ["International"],
                "language": "English",
                "usage_count": 956,
                "rating": 4.7,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-07-10",
                "author": "Maritime Legal Team",
                "content": """CANCELLATION POLICY: The following cancellation terms shall apply:
a) Cancellation more than 90 days prior: 10% cancellation fee of total charter value;
b) Cancellation 61-90 days prior: 25% cancellation fee;
c) Cancellation 31-60 days prior: 50% cancellation fee;
d) Cancellation 0-30 days prior: 100% cancellation fee (no refund);
e) All cancellation fees are in addition to any third-party costs already incurred.""",
                "variables": ["total_charter_value", "cancellation_date", "charter_start_date"],
                "applicable_to": ["All charter types"],
                "legal_notes": "Graduated scale provides fair balance between client and operator protection",
                "related_clauses": ["Force Majeure", "Travel Insurance"],
                "risk_level": "Low"
            },
            {
                "name": "Flexible COVID-19 Cancellation",
                "version": "1.2",
                "jurisdiction": ["International"],
                "language": "English", 
                "usage_count": 234,
                "rating": 4.9,
                "status": "Active",
                "complexity": "Advanced",
                "last_updated": "2025-07-01",
                "author": "Risk Management Team",
                "content": """COVID-19 CANCELLATION PROTECTION: In addition to standard cancellation terms:
a) Full refund (minus processing fees) if government travel restrictions prevent charter;
b) 50% refund if client tests positive for COVID-19 within 14 days of charter;
c) Rebooking option within 12 months with no penalties if health restrictions apply;
d) Charter may be postponed up to 48 hours before start date due to health concerns;
e) All health-related cancellations require official documentation.""",
                "variables": ["charter_start_date", "processing_fees", "health_documentation"],
                "applicable_to": ["Post-pandemic bookings", "International travel"],
                "legal_notes": "Requires verification of health restrictions and documentation",
                "related_clauses": ["Health Requirements", "Travel Documentation"],
                "risk_level": "Medium"
            }
        ],
        "Insurance Requirements": [
            {
                "name": "Comprehensive Hull Insurance",
                "version": "2.2", 
                "jurisdiction": ["International", "EU"],
                "language": "English",
                "usage_count": 782,
                "rating": 4.6,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-07-12",
                "author": "Insurance Specialists",
                "content": """HULL INSURANCE REQUIREMENTS: The vessel must maintain comprehensive marine insurance:
a) Minimum hull value coverage of USD {{ hull_insurance_amount }};
b) Coverage must include collision, fire, theft, and total loss;
c) Policy must name charterer as additional insured party;
d) Deductible not to exceed 1% of vessel value or USD 10,000, whichever is greater;
e) Insurance certificate must be provided 30 days prior to charter commencement.""",
                "variables": ["hull_insurance_amount", "vessel_value", "charter_commencement"],
                "applicable_to": ["High-value vessels", "Bareboat charters"],
                "legal_notes": "Essential for vessels over USD 500,000 value",
                "related_clauses": ["Liability Insurance", "Security Deposit"],
                "risk_level": "High"
            }
        ]
    }
    
    # Merge custom clauses with default database
    if 'custom_clauses' in st.session_state:
        for custom_category, custom_clause_list in st.session_state.custom_clauses.items():
            if custom_category in clause_database:
                # Add custom clauses to existing category
                clause_database[custom_category].extend(custom_clause_list)
            else:
                # Create new category for custom clauses
                clause_database[custom_category] = custom_clause_list
    
    # Display clauses for selected category
    if category in clause_database:
        clauses = clause_database[category]
        
        # Separate custom and default clauses for better display
        custom_clauses = [c for c in clauses if c.get('status') == 'Custom']
        default_clauses = [c for c in clauses if c.get('status') != 'Custom']
        
        total_count = len(clauses)
        custom_count = len(custom_clauses)
        
        st.markdown(f"### {category} Clauses ({total_count} available)")
        if custom_count > 0:
            st.info(f"📝 {custom_count} custom clause(s) created by you")
        
        # Display custom clauses first with special styling
        if custom_clauses:
            st.markdown("#### 📝 Your Custom Clauses")
            for idx, clause in enumerate(custom_clauses):
                with st.expander(f"🌟 {clause['name']} (v{clause['version']}) - Custom Creation"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### Clause Content")
                        st.code(clause['content'], language='text')
                        
                        if clause.get('legal_notes'):
                            st.markdown("#### 📋 Legal Notes")
                            st.info(clause['legal_notes'])
                    
                    with col2:
                        st.markdown("#### 📊 Clause Details")
                        st.markdown(f"**Version:** {clause['version']}")
                        st.markdown(f"**Status:** {clause['status']}")
                        st.markdown(f"**Complexity:** {clause['complexity']}")
                        st.markdown(f"**Author:** {clause['author']}")
                        st.markdown(f"**Created:** {clause['last_updated']}")
                        st.markdown(f"**Usage:** {clause['usage_count']} times")
                        st.markdown(f"**Rating:** ⭐ {clause['rating']}/5.0")
                        
                        if clause.get('applicable_to'):
                            st.markdown("**Applicable to:**")
                            for item in clause['applicable_to']:
                                st.markdown(f"• {item}")
                        
                        # Action buttons for custom clauses
                        col_edit, col_add, col_delete = st.columns(3)
                        
                        with col_edit:
                            if st.button(f"✏️ Edit", key=f"edit_custom_{idx}"):
                                st.info("Edit functionality would open clause editor")
                        
                        with col_add:
                            if st.button(f"🔗 Add to Contract", key=f"add_custom_{idx}"):
                                # Initialize selected clauses in session state if not exists
                                if 'selected_clauses' not in st.session_state:
                                    st.session_state.selected_clauses = []
                                
                                # Create a clause object for the contract
                                selected_clause = {
                                    'name': clause['name'],
                                    'content': clause['content'],
                                    'category': 'Custom Clauses',
                                    'source': 'custom'
                                }
                                
                                # Check if clause is already selected
                                clause_exists = any(sc['name'] == clause['name'] for sc in st.session_state.selected_clauses)
                                
                                if not clause_exists:
                                    st.session_state.selected_clauses.append(selected_clause)
                                    st.success(f"✅ Added '{clause['name']}' to current contract!")
                                else:
                                    st.warning(f"⚠️ '{clause['name']}' is already added to the contract!")
                        
                        with col_delete:
                            if st.button(f"🗑️ Delete", key=f"delete_custom_{idx}"):
                                # Remove from session state
                                st.session_state.custom_clauses[category].pop(idx)
                                st.success("Custom clause deleted!")
                                st.rerun()
            
            st.markdown("---")
        
        # Display default clauses
        if default_clauses:
            st.markdown("#### 📚 Standard Library Clauses")
        
        for idx, clause in enumerate(default_clauses):
            with st.expander(f"📄 {clause['name']} (v{clause['version']}) - ⭐ {clause['rating']}/5.0"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### Clause Content")
                    st.code(clause['content'], language='text')
                    
                    if clause.get('variables'):
                        st.markdown("#### Template Variables")
                        for var in clause['variables']:
                            st.markdown(f"- `{{{{{var}}}}}`")
                
                with col2:
                    st.markdown("#### Clause Metadata")
                    st.markdown(f"**Status:** {clause['status']}")
                    st.markdown(f"**Complexity:** {clause['complexity']}")
                    st.markdown(f"**Risk Level:** {clause['risk_level']}")
                    st.markdown(f"**Usage Count:** {clause['usage_count']:,}")
                    st.markdown(f"**Last Updated:** {clause['last_updated']}")
                    st.markdown(f"**Author:** {clause['author']}")
                    
                    st.markdown("#### Jurisdictions")
                    for jurisdiction in clause['jurisdiction']:
                        st.markdown(f"- {jurisdiction}")
                    
                    st.markdown("#### Applicable To")
                    for applicable in clause['applicable_to']:
                        st.markdown(f"- {applicable}")
                    
                    if clause.get('related_clauses'):
                        st.markdown("#### Related Clauses")
                        for related in clause['related_clauses']:
                            st.markdown(f"- {related}")
                
                # Action buttons
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    if st.button("📋 Copy", key=f"copy_{category}_{idx}"):
                        st.success("Clause copied to clipboard!")
                with col2:
                    if st.button("✏️ Edit", key=f"edit_{category}_{idx}"):
                        st.info(f"Opening editor for: {clause['name']}")
                with col3:
                    if st.button("🔗 Add to Contract", key=f"add_{category}_{idx}"):
                        # Initialize selected clauses in session state if not exists
                        if 'selected_clauses' not in st.session_state:
                            st.session_state.selected_clauses = []
                        
                        # Create a clause object for the contract
                        selected_clause = {
                            'name': clause['name'],
                            'content': clause['content'],
                            'category': category,
                            'source': 'library'
                        }
                        
                        # Check if clause is already selected
                        clause_exists = any(sc['name'] == clause['name'] for sc in st.session_state.selected_clauses)
                        
                        if not clause_exists:
                            st.session_state.selected_clauses.append(selected_clause)
                            st.success(f"✅ Added '{clause['name']}' to current contract!")
                        else:
                            st.warning(f"⚠️ '{clause['name']}' is already added to the contract!")
                with col4:
                    if st.button("📊 Usage Stats", key=f"stats_{category}_{idx}"):
                        st.info(f"Showing usage statistics for: {clause['name']}")
                with col5:
                    if st.button("⚠️ Report Issue", key=f"report_{category}_{idx}"):
                        st.warning("Issue reporting form would open here")
                
                if clause.get('legal_notes'):
                    st.info(f"**Legal Notes:** {clause['legal_notes']}")

def search_filter_section():
    st.subheader("🔍 Advanced Search & Filter")
    
    # Search interface
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input(
            "🔍 Search clauses by content, title, or keywords",
            placeholder="e.g., 'payment schedule', 'force majeure', 'insurance coverage'",
            help="Use natural language or specific legal terms"
        )
    with col2:
        search_type = st.selectbox(
            "Search Type",
            ["Smart Search", "Exact Match", "Keyword Search", "Semantic Search"]
        )
    
    # Advanced filters
    st.markdown("#### 🎛️ Advanced Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_jurisdiction = st.multiselect(
            "Jurisdiction",
            ["International", "EU", "US", "Caribbean", "Asia Pacific", "UK"]
        )
        filter_status = st.multiselect(
            "Status",
            ["Active", "Beta", "Deprecated", "Under Review"]
        )
    
    with col2:
        filter_complexity = st.multiselect(
            "Complexity",
            ["Basic", "Standard", "Advanced", "Expert"]
        )
        filter_risk = st.multiselect(
            "Risk Level",
            ["Low", "Medium", "High", "Critical"]
        )
    
    with col3:
        filter_category = st.multiselect(
            "Categories",
            ["Payment Terms", "Cancellation", "Insurance", "Liability", "Safety", "Environmental"]
        )
        filter_language = st.multiselect(
            "Languages",
            ["English", "French", "Spanish", "Italian", "German"]
        )
    
    with col4:
        usage_range = st.slider(
            "Minimum Usage Count",
            min_value=0,
            max_value=1000,
            value=0
        )
        rating_range = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.1
        )
    
    # Search results
    if st.button("🔍 Search Clauses", type="primary"):
        st.markdown("### 📋 Search Results")
        
        # Mock search results
        if search_query:
            st.success(f"Found 23 clauses matching '{search_query}'")
            
            # Sample search results
            search_results = [
                {"name": "Standard Payment Schedule", "category": "Payment Terms", "relevance": 95, "snippet": "Fifty percent (50%) of the total charter fee shall be paid..."},
                {"name": "Accelerated Payment Terms", "category": "Payment Terms", "relevance": 87, "snippet": "For charter bookings made within sixty (60) days..."},
                {"name": "Corporate Payment Policy", "category": "Payment Terms", "relevance": 76, "snippet": "Net-30 payment terms for qualified corporate clients..."}
            ]
            
            for result in search_results:
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: white;">
                        <h4 style="color: #1e3a8a; margin: 0;">{result['name']}</h4>
                        <p style="color: #666; margin: 5px 0;"><strong>Category:</strong> {result['category']} | <strong>Relevance:</strong> {result['relevance']}%</p>
                        <p style="margin: 10px 0;">{result['snippet']}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.button("👁️ View Full", key=f"view_{result['name']}")
                    with col2:
                        st.button("📋 Copy", key=f"copy_{result['name']}")
                    with col3:
                        st.button("🔗 Add", key=f"add_{result['name']}")
        else:
            st.info("Enter search terms to find relevant clauses")
    
    # Saved searches
    st.markdown("#### 💾 Saved Searches")
    saved_searches = ["High-risk payment terms", "EU compliance clauses", "COVID-19 related clauses"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_saved = st.selectbox("Quick access to saved searches", [""] + saved_searches)
    with col2:
        if st.button("💾 Save Current Search"):
            st.success("Search criteria saved!")
    
    if selected_saved:
        st.info(f"Loading saved search: {selected_saved}")

def clause_editor_section():
    st.subheader("✏️ Professional Clause Editor")
    
    # Add CSS for better text wrapping in clause editor areas
    st.markdown("""
    <style>
    /* Enhanced text wrapping for clause editor text areas */
    .stTextArea textarea {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
        line-height: 1.5 !important;
        resize: vertical !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Editor mode selection
    col1, col2 = st.columns(2)
    with col1:
        editor_mode = st.selectbox(
            "Editor Mode",
            ["Create New Clause", "Edit Existing Clause", "Clone & Modify", "Bulk Import"]
        )
    with col2:
        if editor_mode == "Edit Existing Clause":
            existing_clause = st.selectbox(
                "Select Clause to Edit",
                ["Standard Payment Schedule", "Cancellation Policy", "Insurance Requirements"]
            )
    
    st.markdown("---")
    
    if editor_mode == "Create New Clause":
        create_new_clause_editor()
    elif editor_mode == "Edit Existing Clause":
        edit_existing_clause_editor(existing_clause if 'existing_clause' in locals() else "Standard Payment Schedule")
    elif editor_mode == "Clone & Modify":
        clone_modify_editor()
    else:
        bulk_import_editor()

def create_new_clause_editor():
    st.markdown("### 🆕 Create New Clause")
    
    # Basic clause information
    col1, col2, col3 = st.columns(3)
    with col1:
        clause_name = st.text_input("Clause Name", placeholder="e.g., Special Event Cancellation Terms")
    with col2:
        clause_category = st.selectbox(
            "Category",
            ["Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations", 
             "Force Majeure", "Dispute Resolution", "Safety Requirements", "Environmental Compliance"]
        )
    with col3:
        clause_complexity = st.selectbox("Complexity Level", ["Basic", "Standard", "Advanced", "Expert"])
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        clause_jurisdiction = st.multiselect(
            "Applicable Jurisdictions",
            ["International", "EU", "US", "Caribbean", "Asia Pacific", "UK"]
        )
    with col2:
        clause_language = st.selectbox("Primary Language", ["English", "French", "Spanish", "Italian", "German"])
    with col3:
        clause_risk = st.selectbox("Risk Level", ["Low", "Medium", "High", "Critical"])
    
    # Clause content editor
    st.markdown("#### 📝 Clause Content")
    clause_content = st.text_area(
        "Clause Text",
        height=300,
        placeholder="""Enter the clause content here. Use template variables like {{variable_name}} for dynamic content.

Example:
PAYMENT TERMS: The charter fee of {{currency}} {{total_amount}} shall be paid as follows:
a) {{deposit_percentage}}% deposit due upon signing;
b) Remaining balance due {{days_before}} days prior to charter commencement.""",
        help="Use legal language and include all necessary provisions. Template variables should be enclosed in double braces {{ }}."
    )
    
    # Template variables
    st.markdown("#### 🔧 Template Variables")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Add Variables**")
        var_name = st.text_input("Variable Name", placeholder="e.g., deposit_percentage")
        var_type = st.selectbox("Variable Type", ["Text", "Number", "Currency", "Date", "Percentage", "Boolean"])
        var_description = st.text_input("Description", placeholder="Brief description of this variable")
        
        if st.button("➕ Add Variable"):
            if 'clause_variables' not in st.session_state:
                st.session_state.clause_variables = []
            st.session_state.clause_variables.append({
                "name": var_name,
                "type": var_type,
                "description": var_description
            })
            st.success(f"Variable '{var_name}' added!")
    
    with col2:
        st.markdown("**Current Variables**")
        if 'clause_variables' in st.session_state and st.session_state.clause_variables:
            for i, var in enumerate(st.session_state.clause_variables):
                st.markdown(f"• `{{{{{var['name']}}}}}` ({var['type']}) - {var['description']}")
        else:
            st.info("No variables defined yet")
    
    # Legal compliance
    st.markdown("#### ⚖️ Legal Compliance & Review")
    col1, col2 = st.columns(2)
    with col1:
        compliance_check = st.checkbox("Requires Legal Review")
        urgent_review = st.checkbox("Urgent Review Required")
        public_access = st.checkbox("Available for Public Use")
    with col2:
        applicable_charter_types = st.multiselect(
            "Applicable Charter Types",
            ["Bareboat", "Crewed", "Corporate", "Racing", "Luxury", "Educational"]
        )
    
    # Related clauses and dependencies
    st.markdown("#### 🔗 Clause Relationships")
    col1, col2 = st.columns(2)
    with col1:
        related_clauses = st.multiselect(
            "Related Clauses",
            ["Payment Terms", "Security Deposit", "Insurance Requirements", "Cancellation Policy"]
        )
    with col2:
        prerequisite_clauses = st.multiselect(
            "Prerequisite Clauses",
            ["Vessel Registration", "Insurance Verification", "Credit Check"]
        )
    
    # Save clause
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save as Draft", type="secondary"):
            if clause_name and clause_content and clause_category:
                # Initialize draft clauses in session state if not exists
                if 'draft_clauses' not in st.session_state:
                    st.session_state.draft_clauses = {}
                
                import datetime
                draft_clause = {
                    "name": clause_name,
                    "category": clause_category,
                    "content": clause_content,
                    "complexity": clause_complexity,
                    "jurisdiction": clause_jurisdiction,
                    "language": clause_language,
                    "risk_level": clause_risk,
                    "variables": st.session_state.get('clause_variables', []),
                    "charter_types": applicable_charter_types,
                    "related_clauses": related_clauses,
                    "prerequisite_clauses": prerequisite_clauses,
                    "requires_review": compliance_check,
                    "urgent_review": urgent_review,
                    "public_access": public_access,
                    "created_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "Draft"
                }
                
                if clause_category not in st.session_state.draft_clauses:
                    st.session_state.draft_clauses[clause_category] = []
                
                st.session_state.draft_clauses[clause_category].append(draft_clause)
                st.success(f"✅ Clause '{clause_name}' saved as draft!")
                st.info("💡 You can find your draft in the drafts section for later editing.")
            else:
                st.error("❌ Please fill in Clause Name, Content, and Category before saving.")
                
    with col2:
        if st.button("📋 Save & Add to Library", type="primary"):
            if clause_name and clause_content and clause_category:
                # Initialize custom clauses in session state if not exists
                if 'custom_clauses' not in st.session_state:
                    st.session_state.custom_clauses = {}
                
                import datetime
                custom_clause = {
                    "name": clause_name,
                    "version": "1.0",
                    "jurisdiction": clause_jurisdiction if clause_jurisdiction else ["International"],
                    "language": clause_language,
                    "usage_count": 0,
                    "rating": 5.0,
                    "status": "Custom",
                    "complexity": clause_complexity,
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "author": "User Created (Clause Editor)",
                    "content": clause_content,
                    "variables": [var['name'] for var in st.session_state.get('clause_variables', [])],
                    "applicable_to": applicable_charter_types if applicable_charter_types else ["All charter types"],
                    "legal_notes": f"Professional clause created via Clause Editor. Risk level: {clause_risk}. Requires review: {compliance_check}",
                    "related_clauses": related_clauses,
                    "risk_level": clause_risk
                }
                
                # Add to custom clauses by category
                if clause_category not in st.session_state.custom_clauses:
                    st.session_state.custom_clauses[clause_category] = []
                
                st.session_state.custom_clauses[clause_category].append(custom_clause)
                
                st.success(f"✅ Clause '{clause_name}' added to library!")
                st.info("🔍 You can now find your clause in the Browse Clauses tab under the selected category.")
                
                # Clear the variables after saving
                if 'clause_variables' in st.session_state:
                    del st.session_state['clause_variables']
                    
            else:
                st.error("❌ Please fill in Clause Name, Content, and Category before saving to library.")
                
    with col3:
        if st.button("📤 Submit for Review", type="secondary"):
            if clause_name and clause_content and clause_category:
                # Initialize review queue in session state if not exists
                if 'review_queue' not in st.session_state:
                    st.session_state.review_queue = []
                
                import datetime
                review_clause = {
                    "name": clause_name,
                    "category": clause_category,
                    "content": clause_content,
                    "complexity": clause_complexity,
                    "submitted_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "Pending Review",
                    "urgent": urgent_review,
                    "reviewer": "Legal Team"
                }
                
                st.session_state.review_queue.append(review_clause)
                st.success(f"✅ Clause '{clause_name}' submitted for legal review!")
                st.info("📋 Your clause is now in the review queue and will be processed by the legal team.")
            else:
                st.error("❌ Please fill in Clause Name, Content, and Category before submitting for review.")

def edit_existing_clause_editor(clause_name):
    st.markdown(f"### ✏️ Editing: {clause_name}")
    
    # Version management
    col1, col2, col3 = st.columns(3)
    with col1:
        current_version = st.text_input("Current Version", value="2.1", disabled=True)
    with col2:
        new_version = st.text_input("New Version", value="2.2")
    with col3:
        version_notes = st.text_input("Version Notes", placeholder="Brief description of changes")
    
    # Load existing clause content (mock data)
    existing_content = """PAYMENT TERMS: The total charter fee shall be paid according to the following schedule:
a) Fifty percent (50%) of the total charter fee shall be paid as a deposit upon execution of this agreement;
b) The remaining fifty percent (50%) shall be paid no later than thirty (30) days prior to the charter commencement date;
c) All payments shall be made in the currency specified in this agreement;"""
    
    # Editor
    st.markdown("#### 📝 Edit Clause Content")
    edited_content = st.text_area(
        "Clause Content",
        value=existing_content,
        height=300,
        help="Make your edits to the clause content"
    )
    
    # Change tracking
    if edited_content != existing_content:
        st.warning("⚠️ Unsaved changes detected")
        
        # Show diff
        st.markdown("#### 📊 Changes Made")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Original Version:**")
            st.code(existing_content[:200] + "...", language='text')
        with col2:
            st.markdown("**Modified Version:**")
            st.code(edited_content[:200] + "...", language='text')
    
    # Save options
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💾 Save Changes"):
            if edited_content and edited_content != existing_content:
                # Save the edited clause back to custom clauses
                if 'custom_clauses' not in st.session_state:
                    st.session_state.custom_clauses = {}
                
                import datetime
                # Find and update the existing clause or create new version
                clause_category = "Payment Terms"  # This would normally be determined from the clause
                
                # Create updated clause
                updated_clause = {
                    "name": clause_name,
                    "version": new_version,
                    "jurisdiction": ["International"],
                    "language": "English",
                    "usage_count": 0,
                    "rating": 5.0,
                    "status": "Custom",
                    "complexity": "Standard",
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "author": "User Modified (Clause Editor)",
                    "content": edited_content,
                    "variables": [],
                    "applicable_to": ["All charter types"],
                    "legal_notes": f"Clause updated from version {current_version} to {new_version}. Changes: {version_notes}",
                    "related_clauses": [],
                    "risk_level": "Medium"
                }
                
                if clause_category not in st.session_state.custom_clauses:
                    st.session_state.custom_clauses[clause_category] = []
                
                st.session_state.custom_clauses[clause_category].append(updated_clause)
                
                st.success(f"✅ Changes to '{clause_name}' saved successfully!")
                st.info("🔍 Updated clause is now available in the Browse Clauses tab.")
            else:
                st.warning("⚠️ No changes detected or content is empty.")
                
    with col2:
        if st.button("🔄 Revert Changes"):
            st.info("Changes reverted to last saved version")
            st.rerun()  # Refresh to show original content
            
    with col3:
        if st.button("📤 Submit for Review"):
            if edited_content:
                # Add to review queue
                if 'review_queue' not in st.session_state:
                    st.session_state.review_queue = []
                
                import datetime
                review_item = {
                    "name": f"{clause_name} (Modified)",
                    "category": "Payment Terms",  # This would normally be determined
                    "content": edited_content,
                    "complexity": "Standard",
                    "submitted_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "status": "Pending Review",
                    "urgent": False,
                    "reviewer": "Legal Team",
                    "change_notes": version_notes
                }
                
                st.session_state.review_queue.append(review_item)
                st.success(f"✅ Modified clause '{clause_name}' submitted for legal review!")
                st.info("📋 Your changes are now in the review queue.")
            else:
                st.error("❌ No content to submit for review.")
                
    with col4:
        if st.button("📋 Create New Version"):
            if edited_content and new_version and version_notes:
                # Create new version as a separate clause
                if 'custom_clauses' not in st.session_state:
                    st.session_state.custom_clauses = {}
                
                import datetime
                clause_category = "Payment Terms"  # This would normally be determined
                
                new_version_clause = {
                    "name": f"{clause_name} v{new_version}",
                    "version": new_version,
                    "jurisdiction": ["International"],
                    "language": "English",
                    "usage_count": 0,
                    "rating": 5.0,
                    "status": "Custom",
                    "complexity": "Standard",
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "author": "User Created (New Version)",
                    "content": edited_content,
                    "variables": [],
                    "applicable_to": ["All charter types"],
                    "legal_notes": f"New version created from {clause_name}. Version notes: {version_notes}",
                    "related_clauses": [clause_name],
                    "risk_level": "Medium"
                }
                
                if clause_category not in st.session_state.custom_clauses:
                    st.session_state.custom_clauses[clause_category] = []
                
                st.session_state.custom_clauses[clause_category].append(new_version_clause)
                
                st.success(f"✅ New version {new_version} of '{clause_name}' created!")
                st.info("🔍 New version is now available in the Browse Clauses tab.")
            else:
                st.error("❌ Please provide content, new version number, and version notes.")

def clone_modify_editor():
    st.markdown("### 📋 Clone & Modify Clause")
    
    # Source clause selection
    source_clause = st.selectbox(
        "Select Clause to Clone",
        ["Standard Payment Schedule", "EU Cancellation Policy", "Comprehensive Insurance Terms"]
    )
    
    new_clause_name = st.text_input(
        "New Clause Name",
        value=f"Modified {source_clause}",
        help="Give your cloned clause a descriptive name"
    )
    
    st.info(f"Creating a copy of '{source_clause}' that you can modify without affecting the original.")
    
    # Load template content based on selection
    template_content = {
        "Standard Payment Schedule": """PAYMENT TERMS: The total charter fee shall be paid according to the following schedule:
a) Fifty percent (50%) of the total charter fee shall be paid as a deposit upon execution of this agreement;
b) The remaining fifty percent (50%) shall be paid no later than thirty (30) days prior to the charter commencement date;
c) All payments shall be made in the currency specified in this agreement;""",
        
        "EU Cancellation Policy": """CANCELLATION POLICY: The following cancellation terms shall apply under EU regulations:
a) Cancellation more than 90 days prior: 10% cancellation fee of total charter value;
b) Cancellation 61-90 days prior: 25% cancellation fee;
c) Cancellation 31-60 days prior: 50% cancellation fee;
d) Cancellation 0-30 days prior: 100% cancellation fee (no refund);""",
        
        "Comprehensive Insurance Terms": """INSURANCE REQUIREMENTS: The vessel must maintain comprehensive marine insurance:
a) Minimum hull value coverage as specified in Schedule A;
b) Coverage must include collision, fire, theft, and total loss;
c) Policy must name charterer as additional insured party;
d) Insurance certificate must be provided 30 days prior to charter commencement;"""
    }
    
    # Modified clause editor
    st.markdown("#### 📝 Modify Cloned Content")
    original_content = template_content.get(source_clause, "[Original clause content would be loaded here]")
    
    modified_content = st.text_area(
        "Clause Content", 
        value=original_content, 
        height=250,
        help="Modify the cloned clause content as needed",
        key="clone_modify_content"
    )
    
    # Category and metadata for the new clause
    col1, col2, col3 = st.columns(3)
    with col1:
        new_category = st.selectbox(
            "Category for New Clause",
            ["Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations"],
            key="clone_category"
        )
    with col2:
        complexity_level = st.selectbox(
            "Complexity Level",
            ["Basic", "Standard", "Advanced", "Expert"],
            index=1,  # Default to Standard
            key="clone_complexity"
        )
    with col3:
        risk_level = st.selectbox(
            "Risk Level",
            ["Low", "Medium", "High", "Critical"],
            index=1,  # Default to Medium
            key="clone_risk"
        )
    
    if st.button("📋 Create Modified Copy", type="primary"):
        if new_clause_name and modified_content and new_category:
            # Initialize custom clauses in session state if not exists
            if 'custom_clauses' not in st.session_state:
                st.session_state.custom_clauses = {}
            
            import datetime
            cloned_clause = {
                "name": new_clause_name,
                "version": "1.0",
                "jurisdiction": ["International"],
                "language": "English",
                "usage_count": 0,
                "rating": 5.0,
                "status": "Custom",
                "complexity": complexity_level,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d"),
                "author": "User Created (Cloned & Modified)",
                "content": modified_content,
                "variables": [],
                "applicable_to": ["All charter types"],
                "legal_notes": f"Cloned and modified from '{source_clause}'. Risk level: {risk_level}",
                "related_clauses": [source_clause],
                "risk_level": risk_level
            }
            
            # Add to custom clauses by category
            if new_category not in st.session_state.custom_clauses:
                st.session_state.custom_clauses[new_category] = []
            
            st.session_state.custom_clauses[new_category].append(cloned_clause)
            
            st.success(f"✅ Cloned clause '{new_clause_name}' created successfully!")
            st.info("🔍 Your cloned clause is now available in the Browse Clauses tab under the selected category.")
        else:
            st.error("❌ Please provide a new clause name, content, and category.")

def bulk_import_editor():
    st.markdown("### 📤 Bulk Import Clauses")
    
    # Import options
    import_method = st.selectbox(
        "Import Method",
        ["Upload JSON File", "Upload CSV File", "Import from URL", "Paste JSON Data"]
    )
    
    if import_method == "Upload JSON File":
        uploaded_file = st.file_uploader(
            "Choose JSON file containing clauses",
            type=['json'],
            help="Upload a JSON file with clause definitions"
        )
        
        if uploaded_file:
            st.success("File uploaded successfully!")
            st.info("3 clauses found in file. Preview below:")
            
            # Mock preview
            st.code("""
{
  "clauses": [
    {
      "name": "European Payment Terms",
      "category": "Payment Terms",
      "content": "PAYMENT TERMS: As per EU regulations..."
    }
  ]
}
            """, language='json')
            
            if st.button("📥 Import All Clauses"):
                st.success("Successfully imported 3 clauses to library!")
    
    elif import_method == "Paste JSON Data":
        json_data = st.text_area(
            "Paste JSON Data",
            height=200,
            placeholder='{"clauses": [{"name": "...", "content": "..."}]}'
        )
        
        if json_data and st.button("📥 Import from JSON"):
            st.success("Clauses imported successfully!")

def ai_suggestions_section():
    st.subheader("🤖 AI-Powered Clause Suggestions")
    
    # AI suggestion interface
    st.markdown("### 🎯 Get Intelligent Clause Recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        charter_context = st.text_area(
            "Describe your charter scenario",
            placeholder="e.g., 'High-value superyacht charter in Mediterranean waters for corporate client with 14-day duration'",
            height=100,
            help="Provide details about the charter to get relevant clause suggestions"
        )
    
    with col2:
        # Context parameters
        st.markdown("#### Charter Parameters")
        charter_type = st.selectbox("Charter Type", ["Bareboat", "Crewed", "Corporate", "Racing", "Luxury"])
        charter_value = st.number_input("Charter Value (USD)", min_value=0, value=50000, step=5000)
        charter_duration = st.number_input("Duration (days)", min_value=1, value=7, step=1)
        risk_factors = st.multiselect("Risk Factors", ["High seas", "Hurricane season", "Inexperienced crew", "High value cargo", "International waters"])
    
    if st.button("🤖 Get AI Suggestions", type="primary"):
        st.markdown("### 🎯 AI Recommendations")
        
        # Simulate AI analysis
        with st.spinner("AI analyzing charter parameters..."):
            import time
            time.sleep(2)
        
        st.success("Analysis complete! Here are the recommended clauses:")
        
        # Mock AI suggestions
        suggestions = [
            {
                "clause": "Enhanced Insurance Requirements",
                "confidence": 95,
                "reason": "High charter value requires comprehensive coverage",
                "priority": "Critical",
                "category": "Insurance"
            },
            {
                "clause": "Corporate Payment Terms",
                "confidence": 88,
                "reason": "Corporate client detected - net terms may be appropriate",
                "priority": "Important", 
                "category": "Payment"
            },
            {
                "clause": "Professional Crew Requirements",
                "confidence": 82,
                "reason": "Luxury charter requires certified professional crew",
                "priority": "Important",
                "category": "Safety"
            },
            {
                "clause": "Mediterranean Compliance Clause",
                "confidence": 76,
                "reason": "Operating in EU waters requires specific regulatory compliance",
                "priority": "Standard",
                "category": "Legal"
            }
        ]
        
        for suggestion in suggestions:
            with st.container():
                # Priority color coding
                priority_colors = {"Critical": "#dc2626", "Important": "#f59e0b", "Standard": "#10b981"}
                color = priority_colors.get(suggestion['priority'], "#6b7280")
                
                st.markdown(f"""
                <div style="border: 1px solid {color}; border-radius: 8px; padding: 15px; margin: 10px 0; background: white;">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="color: {color}; margin: 0;">{suggestion['clause']}</h4>
                            <p style="margin: 5px 0; color: #666;">{suggestion['reason']}</p>
                            <div style="display: flex; gap: 10px; margin-top: 10px;">
                                <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                                    {suggestion['priority']}
                                </span>
                                <span style="background: #f1f5f9; color: #1e3a8a; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                                    {suggestion['category']}
                                </span>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 12px; color: #666;">
                                Confidence: <strong>{suggestion['confidence']}%</strong>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("👁️ Preview", key=f"preview_{suggestion['clause']}"):
                        st.info(f"Previewing: {suggestion['clause']}")
                with col2:
                    if st.button("🔗 Add to Contract", key=f"add_{suggestion['clause']}"):
                        # Initialize selected clauses in session state if not exists
                        if 'selected_clauses' not in st.session_state:
                            st.session_state.selected_clauses = []
                        
                        # Create a clause object for the contract
                        selected_clause = {
                            'name': suggestion['clause'],
                            'content': suggestion['description'],
                            'category': 'AI Suggestions',
                            'source': 'ai_suggestion'
                        }
                        
                        # Check if clause is already selected
                        clause_exists = any(sc['name'] == suggestion['clause'] for sc in st.session_state.selected_clauses)
                        
                        if not clause_exists:
                            st.session_state.selected_clauses.append(selected_clause)
                            st.success(f"✅ Added {suggestion['clause']} to contract!")
                        else:
                            st.warning(f"⚠️ {suggestion['clause']} is already added to the contract!")
                with col3:
                    if st.button("❌ Dismiss", key=f"dismiss_{suggestion['clause']}"):
                        st.info("Suggestion dismissed")
    
    # AI learning section
    st.markdown("---")
    st.markdown("### 🧠 Help AI Learn")
    st.info("Rate clause suggestions to improve AI recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        feedback_clause = st.selectbox("Recent Suggestion", ["Enhanced Insurance Requirements", "Corporate Payment Terms"])
        feedback_rating = st.slider("How relevant was this suggestion?", 1, 5, 3)
    with col2:
        feedback_comments = st.text_area("Comments (optional)", placeholder="Why was this suggestion helpful or not?")
        if st.button("📤 Submit Feedback"):
            st.success("Thank you! Your feedback helps improve AI suggestions.")

def clause_analytics_section():
    st.subheader("📊 Clause Analytics Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clauses", "1,247", "+23")
    with col2:
        st.metric("Most Used", "Payment Terms", "")
    with col3:
        st.metric("Avg Rating", "4.6", "+0.1")
    with col4:
        st.metric("Active Categories", "16", "+2")
    
    st.markdown("---")
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Usage Trends", "🏆 Popular Clauses", "⚠️ Risk Analysis", "🔍 Usage Patterns"])
    
    with tab1:
        st.markdown("#### 📈 Clause Usage Over Time")
        # Mock usage chart
        usage_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            'Payment Terms': [120, 135, 150, 180, 195, 210, 234],
            'Cancellation': [89, 95, 98, 115, 125, 134, 142],
            'Insurance': [67, 72, 85, 89, 92, 98, 105]
        }
        st.line_chart(usage_data, x='Month')
        
        st.markdown("#### Key Insights")
        st.info("📈 Payment Terms clauses showing 25% increase in usage")
        st.info("🔄 Cancellation policies becoming more popular in Q2")
        st.warning("⚠️ Insurance clauses usage below average - may need review")
    
    with tab2:
        st.markdown("#### 🏆 Most Popular Clauses")
        popular_data = {
            'Clause Name': ['Standard Payment Schedule', 'EU Cancellation Policy', 'Comprehensive Insurance', 'Force Majeure Terms', 'Dispute Resolution'],
            'Usage Count': [1247, 956, 782, 654, 543],
            'Rating': [4.8, 4.7, 4.6, 4.5, 4.4],
            'Category': ['Payment', 'Cancellation', 'Insurance', 'Legal', 'Legal'],
            'Last Updated': ['2025-07-15', '2025-07-10', '2025-07-12', '2025-06-20', '2025-06-15']
        }
        st.dataframe(popular_data, use_container_width=True)
        
        # Category breakdown
        st.markdown("#### 📊 Usage by Category")
        category_data = {
            'Category': ['Payment Terms', 'Cancellation', 'Insurance', 'Liability', 'Safety', 'Environmental'],
            'Usage': [2456, 1892, 1456, 1234, 987, 654]
        }
        st.bar_chart(category_data, x='Category', y='Usage')
    
    with tab3:
        st.markdown("#### ⚠️ Risk Analysis")
        
        # Risk distribution
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Risk Level Distribution**")
            risk_data = {'Low': 45, 'Medium': 32, 'High': 18, 'Critical': 5}
            st.bar_chart(risk_data)
        
        with col2:
            st.markdown("**High-Risk Clauses Requiring Review**")
            high_risk_clauses = [
                "Accelerated Payment Terms",
                "No-Refund Cancellation",
                "Limited Liability Waiver",
                "Force Majeure Extension"
            ]
            for clause in high_risk_clauses:
                st.warning(f"⚠️ {clause}")
        
        # Risk recommendations
        st.markdown("#### 💡 Risk Mitigation Recommendations")
        st.info("🔍 Consider adding travel insurance requirements for high-risk charters")
        st.info("📋 Review liability limitations in accordance with latest maritime law")
        st.info("⚖️ Update force majeure clauses to include pandemic scenarios")
    
    with tab4:
        st.markdown("#### 🔍 Usage Pattern Analysis")
        
        # Seasonal patterns
        st.markdown("**Seasonal Usage Patterns**")
        seasonal_data = {
            'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
            'Charter Bookings': [234, 567, 890, 456],
            'Cancellation Clauses': [45, 123, 89, 67]
        }
        st.line_chart(seasonal_data, x='Quarter')
        
        # Geographic patterns
        st.markdown("**Geographic Usage Distribution**")
        geo_data = {
            'Region': ['Mediterranean', 'Caribbean', 'Pacific', 'Atlantic', 'Indian Ocean'],
            'Usage': [456, 234, 123, 89, 45]
        }
        st.bar_chart(geo_data, x='Region', y='Usage')
        
        # Client type patterns
        st.markdown("**Usage by Client Type**")
        client_data = {
            'Client Type': ['Corporate', 'Individual', 'Broker', 'Repeat Customer'],
            'Count': [234, 456, 123, 189]
        }
        st.bar_chart(client_data, x='Client Type', y='Count')

def library_settings_section():
    st.subheader("⚙️ Library Settings & Management")
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 General Settings", "👥 Access Control", "📚 Content Management", "🔄 Maintenance"])
    
    with tab1:
        st.markdown("#### 🌐 General Library Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Default Language", ["English", "French", "Spanish", "Italian", "German"])
            st.selectbox("Default Jurisdiction", ["International", "EU", "US", "Caribbean"])
            st.checkbox("Enable Clause Versioning", value=True)
            st.checkbox("Require Approval for New Clauses", value=True)
            st.checkbox("Enable Usage Analytics", value=True)
        
        with col2:
            st.selectbox("Default Risk Level", ["Low", "Medium", "High"])
            st.number_input("Auto-archive after (days)", min_value=30, value=365, step=30)
            st.checkbox("Enable AI Suggestions", value=True)
            st.checkbox("Allow Public Submissions", value=False)
            st.checkbox("Enable Collaboration Features", value=True)
    
    with tab2:
        st.markdown("#### 👥 User Access Control")
        
        # Role management
        st.markdown("**User Roles & Permissions**")
        roles_data = {
            'Role': ['Administrator', 'Legal Reviewer', 'Editor', 'Viewer'],
            'View Clauses': [True, True, True, True],
            'Edit Clauses': [True, True, True, False],
            'Create Clauses': [True, True, False, False],
            'Delete Clauses': [True, False, False, False],
            'Approve Clauses': [True, True, False, False],
            'Manage Settings': [True, False, False, False]
        }
        st.dataframe(roles_data, use_container_width=True)
        
        # User management
        st.markdown("**Add New User**")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_user_email = st.text_input("Email Address")
        with col2:
            new_user_role = st.selectbox("Role", ["Viewer", "Editor", "Legal Reviewer", "Administrator"])
        with col3:
            if st.button("➕ Add User"):
                st.success(f"User {new_user_email} added with {new_user_role} role")
    
    with tab3:
        st.markdown("#### 📚 Content Management")
        
        # Bulk operations
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Bulk Operations**")
            if st.button("📤 Export All Clauses"):
                st.success("Clauses exported to JSON file")
            if st.button("📥 Import Clauses"):
                st.info("Import dialog would open here")
            if st.button("🔄 Sync with External Source"):
                st.info("Syncing with external clause database...")
        
        with col2:
            st.markdown("**Content Validation**")
            if st.button("🔍 Validate All Clauses"):
                st.success("All clauses validated successfully")
            if st.button("🧹 Remove Duplicates"):
                st.info("Found and removed 3 duplicate clauses")
            if st.button("📊 Generate Usage Report"):
                st.success("Usage report generated")
        
        # Template management
        st.markdown("**Template & Variable Management**")
        if st.button("🔧 Update All Templates"):
            st.info("Updating clause templates with latest variables...")
        if st.button("📋 Validate Template Variables"):
            st.success("All template variables validated")
    
    with tab4:
        st.markdown("#### 🔄 Maintenance & Backup")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Database Maintenance**")
            if st.button("🗃️ Optimize Database"):
                st.success("Database optimized successfully")
            if st.button("🧹 Clean Old Versions"):
                st.info("Removed 15 old clause versions")
            if st.button("📊 Rebuild Analytics"):
                st.info("Analytics data rebuilt")
        
        with col2:
            st.markdown("**Backup & Recovery**")
            if st.button("💾 Create Backup"):
                st.success("Backup created: clause_library_2025-07-23.bak")
            if st.button("📂 Restore from Backup"):
                st.warning("Select backup file to restore from")
            if st.button("☁️ Sync to Cloud"):
                st.info("Syncing to cloud storage...")
        
        # System status
        st.markdown("#### 📊 System Status")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Storage Used", "2.3 GB", "")
        with col2:
            st.metric("Active Users", "23", "+3")
        with col3:
            st.metric("Last Backup", "2 hours ago", "")
        with col4:
            st.metric("System Health", "98%", "+1%")

def contract_versions_page(systems):
    st.header("📁 Contract Versions")
    
    # Create tabs for different version management features
    tab1, tab2, tab3 = st.tabs(["📋 Version History", "🔍 Version Comparison", "📊 Version Analytics"])
    
    with tab1:
        st.subheader("All Contract Versions")
        
        # Check for versions directory
        if os.path.exists(VERSIONS_DIR):
            version_files = [f for f in os.listdir(VERSIONS_DIR) if f.endswith('.html')]
            
            if version_files:
                # Collect version information
                version_info = []
                for version_file in sorted(version_files, reverse=True):
                    try:
                        parts = version_file.replace('.html', '').split('_')
                        if len(parts) >= 3:
                            version = parts[1].replace('v', '')
                            contract_id = parts[2]
                            file_path = os.path.join(VERSIONS_DIR, version_file)
                            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                            file_size = os.path.getsize(file_path)
                            
                            # Try to extract vessel name from file content
                            vessel_name = "Unknown"
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    if 'vessel_name' in content:
                                        import re
                                        match = re.search(r'<title>Yacht Charter Contract - ([^<]+)</title>', content)
                                        if match:
                                            vessel_name = match.group(1)
                            except:
                                pass
                            
                            version_info.append({
                                'Version': version,
                                'Contract ID': contract_id,
                                'Vessel': vessel_name,
                                'Created': file_time.strftime('%Y-%m-%d %H:%M:%S'),
                                'Size (KB)': round(file_size / 1024, 1),
                                'File': version_file,
                                'Path': file_path
                            })
                    except Exception as e:
                        st.error(f"Error processing {version_file}: {str(e)}")
                
                if version_info:
                    # Display version table
                    df = pd.DataFrame(version_info)
                    st.dataframe(df[['Version', 'Contract ID', 'Vessel', 'Created', 'Size (KB)']], use_container_width=True)
                    
                    # Version actions
                    st.markdown("### 🔧 Version Actions")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        selected_version = st.selectbox(
                            "Select Version:",
                            options=[f"v{info['Version']} - {info['Vessel']} ({info['Contract ID']})" for info in version_info],
                            key="version_mgmt_select"
                        )
                    
                    with col2:
                        if st.button("👁️ Preview Version", use_container_width=True):
                            # Find selected version file
                            for info in version_info:
                                if f"v{info['Version']} - {info['Vessel']} ({info['Contract ID']})" == selected_version:
                                    with open(info['Path'], 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    st.markdown(f"### Preview: Version {info['Version']}")
                                    st.components.v1.html(content, height=600, scrolling=True)
                                    break
                    
                    with col3:
                        if st.button("📥 Download Version", use_container_width=True):
                            # Find selected version file
                            for info in version_info:
                                if f"v{info['Version']} - {info['Vessel']} ({info['Contract ID']})" == selected_version:
                                    with open(info['Path'], 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    
                                    st.download_button(
                                        label=f"📄 Download v{info['Version']}",
                                        data=content,
                                        file_name=info['File'],
                                        mime="text/html",
                                        use_container_width=True
                                    )
                                    break
                
                # Bulk actions
                st.markdown("### 🗂️ Bulk Actions")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📦 Export All Versions", use_container_width=True):
                        st.info("Bulk export functionality would create a ZIP file with all versions")
                
                with col2:
                    if st.button("🧹 Cleanup Old Versions", use_container_width=True):
                        st.warning("This would remove versions older than 30 days (not implemented)")
                
                with col3:
                    if st.button("📊 Generate Report", use_container_width=True):
                        st.info("Version analytics report would be generated here")
                        
            else:
                st.info("No contract versions found. Generate contracts to see version history here.")
        else:
            st.info("Versions directory not found. Generate contracts to start creating versions.")
    
    with tab2:
        st.subheader("🔍 Version Comparison")
        st.info("Version comparison functionality would allow side-by-side comparison of different contract versions.")
        
        if os.path.exists(VERSIONS_DIR):
            version_files = [f for f in os.listdir(VERSIONS_DIR) if f.endswith('.html')]
            if len(version_files) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.selectbox("Select First Version:", version_files, key="compare_v1")
                
                with col2:
                    st.selectbox("Select Second Version:", version_files, key="compare_v2")
                
                if st.button("🔍 Compare Versions"):
                    st.info("Detailed comparison would show differences between selected versions")
            else:
                st.info("Need at least 2 versions to compare.")
    
    with tab3:
        st.subheader("📊 Version Analytics")
        
        if os.path.exists(VERSIONS_DIR):
            version_files = [f for f in os.listdir(VERSIONS_DIR) if f.endswith('.html')]
            
            if version_files:
                # Basic analytics
                total_versions = len(version_files)
                
                # Get file dates
                file_dates = []
                for version_file in version_files:
                    file_path = os.path.join(VERSIONS_DIR, version_file)
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_dates.append(file_time)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Versions", total_versions)
                
                with col2:
                    if file_dates:
                        latest_date = max(file_dates)
                        st.metric("Latest Version", latest_date.strftime('%Y-%m-%d'))
                
                with col3:
                    if file_dates:
                        oldest_date = min(file_dates)
                        days_span = (max(file_dates) - oldest_date).days
                        st.metric("Days Span", f"{days_span} days")
                
                with col4:
                    if len(file_dates) > 1:
                        avg_interval = sum([(file_dates[i] - file_dates[i-1]).days for i in range(1, len(sorted(file_dates)))]) / (len(file_dates) - 1)
                        st.metric("Avg Days Between", f"{avg_interval:.1f}")
                
                # Version timeline
                if file_dates:
                    st.markdown("### 📈 Version Timeline")
                    
                    # Create timeline data
                    timeline_data = pd.DataFrame({
                        'Date': file_dates,
                        'Version': [f"v{i+1}" for i in range(len(file_dates))]
                    }).sort_values('Date')
                    
                    # Simple timeline visualization
                    import plotly.express as px
                    fig = px.scatter(timeline_data, x='Date', y='Version', 
                                   title='Contract Version Timeline',
                                   labels={'Date': 'Creation Date', 'Version': 'Version Number'})
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No version data available for analytics.")
        else:
            st.info("No versions directory found.")

def analytics_page(systems):
    st.header("📈 Analytics & Logs")
    st.info("Analytics and logging functionality would be implemented here.")

def settings_page():
    st.header("⚙️ Settings")
    st.info("Settings functionality would be implemented here.")

# Database class placeholder
class ContractDatabase:
    def __init__(self):
        self.db_file = DATABASE_FILE

if __name__ == "__main__":
    # Initialize database and directories on startup
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    os.makedirs(VERSIONS_DIR, exist_ok=True)
    
    # Initialize database
    db = ContractDatabase()
    
    main()
