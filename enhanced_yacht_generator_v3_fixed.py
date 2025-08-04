import streamlit as st
import pandas as pd
import datetime
import os
import io
import json
import uuid
import hashlib
import smtplib
import random
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
        <h2>Force Majeure (Recommended)</h2>
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
        <h2>{{ clause.name }}</h2>
        <p>{{ clause.content | replace('\n', '<br>') }}</p>
        {% if clause.category %}
        <p style="font-size: 9px; color: #6b7280; margin-top: 8px;">
            <strong>Category:</strong> {{ clause.category }}
        </p>
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}

    {% if services_clauses %}
    <h1>Services</h1>
    {% for clause in services_clauses %}
    <div class="services-clause" style="background: #f0fdf4; border: 1px solid #16a34a; padding: 15px; margin: 15px 0; border-radius: 8px;">
        <h2 style="color: #15803d;">🔧 {{ clause.name }}</h2>
        <p>{{ clause.content | replace('\n', '<br>') }}</p>
        {% if clause.category %}
        <p style="font-size: 9px; color: #16a34a; margin-top: 8px;">
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
            <th>Recommended</th>
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

    {% if risk_assessment.mitigation_strategies %}
    <h1>6A. RISK MITIGATION STRATEGIES</h1>
    <div style="background: #f0f9ff; border: 1px solid #0ea5e9; padding: 15px; margin: 15px 0;">
        <p style="font-weight: bold; color: #0c4a6e; margin-bottom: 15px;">
            The following risk mitigation strategies have been identified and recommended for this charter based on the comprehensive risk assessment:
        </p>
        
        {% for mitigation in risk_assessment.mitigation_strategies %}
        <div style="background: white; border-left: 4px solid #0ea5e9; padding: 12px; margin: 10px 0; border-radius: 4px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="margin: 0; color: #0c4a6e;">{{ mitigation.name }}</h3>
                <div style="display: flex; gap: 10px;">
                    <span style="background: {% if mitigation.effectiveness > 0.7 %}#10b981{% elif mitigation.effectiveness > 0.5 %}#f59e0b{% else %}#ef4444{% endif %}; 
                                 color: white; padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: bold;">
                        {{ (mitigation.effectiveness * 100) | round }}% Effective
                    </span>
                    <span style="background: {% if mitigation.cost_impact == 'Low' %}#10b981{% elif mitigation.cost_impact == 'Medium' %}#f59e0b{% else %}#ef4444{% endif %}; 
                                 color: white; padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: bold;">
                        {{ mitigation.cost_impact }} Cost
                    </span>
                </div>
            </div>
            <p style="margin: 5px 0; font-size: 11px; color: #374151;">
                <strong>Description:</strong> {{ mitigation.description }}
            </p>
            <p style="margin: 5px 0; font-size: 10px; color: #6b7280;">
                <strong>Implementation:</strong> {{ mitigation.implementation }}
            </p>
        </div>
        {% endfor %}
        
        <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 10px; margin-top: 15px; border-radius: 4px;">
            <p style="margin: 0; font-size: 10px; color: #92400e;">
                <strong>⚠️ Implementation Notice:</strong> The Lessor commits to implementing the above mitigation strategies 
                where feasible and cost-effective. Some strategies may require additional discussion and mutual agreement between parties.
                Implementation timeline and specific details shall be confirmed in writing prior to charter commencement.
            </p>
        </div>
    </div>
    {% endif %}

    <h1>6. OPERATIONAL LIMITATIONS & SAFETY</h1>
    <div class="two-column">
        <div>
            <h3>Operational Areas</h3>
            <p>{{ operational_area }}</p>
            
            <h3>Weather Restrictions</h3>
            <p>As per recommended weather clause above. Captain's discretion applies for safety.</p>
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
                <p><strong>Features Applied:</strong></p>
                <p>✅ Risk Assessment & Optimization</p>
                <p>✅ Intelligent Clause Selection</p>
                <p>✅ Industry Best Practices</p>
            </div>
        </div>
        <p style="text-align: center; margin-top: 10px; font-style: italic;">
            This contract includes Risk assessment and clause optimization based on vessel specifications, operational requirements, and charter client profile.
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
            content.append(Paragraph("4A. ADDITIONAL SELECTED CLAUSES", heading_style))
            content.append(Spacer(1, 8))
            
            for i, clause in enumerate(additional_clauses, 1):
                # Clause title with source
                source_text = ""
                if clause.get('source') == 'ai_suggestion':
                    source_text = " (Suggested)"
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
        
        # Services clauses in separate section
        services_clauses = contract_data.get('services_clauses', [])
        if services_clauses:
            # Services section heading with special styling
            services_heading_style = ParagraphStyle(
                'ServicesHeading',
                parent=heading_style,
                textColor=colors.HexColor('#16a34a'),  # Green color for services
                borderColor=colors.HexColor('#16a34a'),
                backColor=colors.HexColor('#f0fdf4')  # Light green background
            )
            
            content.append(Paragraph("Services", services_heading_style))
            content.append(Spacer(1, 8))
            
            for i, clause in enumerate(services_clauses, 1):
                # Services clause title with special styling
                source_text = ""
                if clause.get('source') == 'ai_suggestion':
                    source_text = " (Suggested)"
                elif clause.get('source') == 'custom':
                    source_text = " (Custom)"
                
                clause_title = f"🔧 {i}. {clause.get('name', 'Untitled Service')}{source_text}"
                
                services_subheading_style = ParagraphStyle(
                    'ServicesSubHeading',
                    parent=subheading_style,
                    textColor=colors.HexColor('#15803d'),  # Darker green
                    backColor=colors.HexColor('#f0fdf4'),
                    borderWidth=1,
                    borderColor=colors.HexColor('#16a34a'),
                    borderPadding=6
                )
                
                content.append(Paragraph(clause_title, services_subheading_style))
                content.append(Spacer(1, 4))
                
                # Services clause content
                clause_content = clause.get('content', 'No content available')
                services_normal_style = ParagraphStyle(
                    'ServicesNormal',
                    parent=normal_style,
                    backColor=colors.HexColor('#f0fdf4'),
                    borderPadding=8
                )
                content.append(Paragraph(clause_content, services_normal_style))
                
                # Category with services styling
                if clause.get('category'):
                    category_text = f"Category: {clause['category']}"
                    content.append(Paragraph(category_text, 
                        ParagraphStyle('ServicesCategoryStyle', parent=styles['Normal'], 
                                     fontSize=8, textColor=colors.HexColor('#16a34a'),
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
Features: Risk Assessment, Intelligent Clause Selection, Industry Best Practices</i>"""
        
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
        <p>Contract Generation with Risk Assessment & Optimization</p>
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
    #st.header("🚀 Contract Generator") #Removed
    
    # Add compact CSS for metrics
    st.markdown("""
    <style>
    /* Compact metrics styling */
    div[data-testid="metric-container"] {
        background: #F9136D;
        border: 1px solid #e5e7eb;
        padding: 0.2rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="metric-container"] > div {
        width: fit-content;
        flex: none;
    }
    div[data-testid="metric-container"] label {
        font-size: 0.68rem !important;
        font-weight: 600 !important;
        color: #4b5563 !important;
        margin-bottom: 0.1rem !important;
    }
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: white !important;
    }
    /* Make analytics headers smaller */
    h4 .metric-header {
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Quick stats at top (Removed)
    # col1, col2, col3, col4 = st.columns(4)
    
    # with col1:
    #     st.metric("Total Contracts", "0")
    # with col2:
    #     st.metric("Active Templates", "1")
    # with col3:
    #     st.metric("Avg Risk Score", "1.2")
    # with col4:
    #     st.metric("Features", "4 Active")
    
    # Main two-column layout
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.markdown("## 📝 Contract Input")
        
        # AI Vessel Name Generator (outside form)
        st.markdown("### 🤖 Vessel Name Generator")
        col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        if st.button("🎲 Generate Random Vessel Name", key="btn_1"):
            # Define vessel name components
            prefixes = ["M/Y", "S/Y", "MY", "SY", ""]
            luxury_words = ["Royal", "Elite", "Diamond", "Platinum", "Golden", "Silver", "Crystal", "Pearl"]
            nature_words = ["Ocean", "Sea", "Wave", "Breeze", "Horizon", "Sunset", "Dawn", "Star"]
            mythological = ["Poseidon", "Neptune", "Triton", "Odyssey", "Phoenix", "Atlas", "Apollo", "Zeus"]
            modern_names = ["Infinity", "Serenity", "Harmony", "Destiny", "Legacy", "Victory", "Freedom", "Spirit"]
            
            styles = [
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
        if st.button("🔄 Generate Another", key="btn_2"):
            # Define vessel name components
            prefixes = ["M/Y", "S/Y", "MY", "SY", ""]
            luxury_words = ["Royal", "Elite", "Diamond", "Platinum", "Golden", "Silver", "Crystal", "Pearl"]
            nature_words = ["Ocean", "Sea", "Wave", "Breeze", "Horizon", "Sunset", "Dawn", "Star"]
            mythological = ["Poseidon", "Neptune", "Triton", "Odyssey", "Phoenix", "Atlas", "Apollo", "Zeus"]
            modern_names = ["Infinity", "Serenity", "Harmony", "Destiny", "Legacy", "Victory", "Freedom", "Spirit"]
            
            styles = [
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
            
            generated_name = random.choice(styles)()
            st.session_state.ai_generated_vessel_name = generated_name
            st.info(f"🔄 New suggestion: **{generated_name}**")
    
    with col3:
        # Show example generated names for inspiration
        if st.button("💡 Show Examples", key="btn_3"):
            vessel_examples = [
                "Royal Odyssey",
                "Serenity Breeze",
                "Azure Horizon",
                "Poseidon's Pearl",
                "Celestial Voyager",
                "Diamond Seas",
                "Majestic Wave"
            ]
            st.table(pd.DataFrame(vessel_examples, columns=["Luxury Yacht Names"]))
    
    st.markdown("---")
    
    # In the LEFT column - Continue with AI Generators & Form Input
    with left_col:
        # AI Company Name Generator
        st.markdown("#### 🏢 Company Name Generator")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            if st.button("🎲 Generate Charter Company", key="btn_company"):
                # Company name components
                luxury_prefixes = ["Elite", "Prestige", "Premier", "Royal", "Monaco", "Azure", "Platinum", "Diamond"]
                nautical_words = ["Marine", "Yacht", "Charter", "Seas", "Maritime", "Ocean", "Harbour", "Bay"]
                locations = ["Monaco", "Mediterranean", "Caribbean", "Riviera", "Coast", "Islands", "Waters"]
                suffixes = ["Ltd.", "S.A.", "Group", "Charters", "International", "Marine", "Yachting"]
                
                company_styles = [
                    lambda: f"{random.choice(luxury_prefixes)} {random.choice(nautical_words)} {random.choice(suffixes)}",
                    lambda: f"{random.choice(locations)} {random.choice(luxury_prefixes)} {random.choice(suffixes)}",
                    lambda: f"{random.choice(luxury_prefixes)} {random.choice(locations)} {random.choice(nautical_words)}"
                ]
                
                generated_company = random.choice(company_styles)()
                st.session_state.ai_generated_lessor = {
                    'name': generated_company,
                    'address': f"{random.randint(1, 99)} Port {random.choice(['Royal', 'Marina', 'Elite'])}\n{random.choice(['98000 Monaco', '06400 Cannes', '83990 Saint-Tropez'])}\n{random.choice(['Monaco', 'France', 'Italy'])}",
                    'contact': f"Captain {random.choice(['Jean-Luc', 'Alessandro', 'William', 'Francesco'])} {random.choice(['Moreau', 'Rossi', 'Smith', 'Costa'])}",
                    'email': f"{generated_company.lower().replace(' ', '').replace('.', '')}@{random.choice(['monaco', 'riviera', 'charter'])}.{random.choice(['mc', 'com', 'fr'])}",
                    'phone': f"+{random.choice(['377', '33', '39'])} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                }
                st.success(f"🏢 Generated company: **{generated_company}**")
        
        with col2:
            if st.button("🔄 Another Co.", key="btn_company_2"):
                # Company name components (defined here for scope)
                luxury_prefixes = ["Elite", "Prestige", "Premier", "Royal", "Monaco", "Azure", "Platinum", "Diamond"]
                nautical_words = ["Marine", "Yacht", "Charter", "Seas", "Maritime", "Ocean", "Harbour", "Bay"]
                locations = ["Monaco", "Mediterranean", "Caribbean", "Riviera", "Coast", "Islands", "Waters"]
                suffixes = ["Ltd.", "S.A.", "Group", "Charters", "International", "Marine", "Yachting"]
                
                company_styles = [
                    lambda: f"{random.choice(luxury_prefixes)} {random.choice(nautical_words)} {random.choice(suffixes)}",
                    lambda: f"{random.choice(locations)} {random.choice(luxury_prefixes)} {random.choice(suffixes)}",
                    lambda: f"{random.choice(luxury_prefixes)} {random.choice(locations)} {random.choice(nautical_words)}"
                ]
                
                generated_company = random.choice(company_styles)()
                st.session_state.ai_generated_lessor = {
                    'name': generated_company,
                    'address': f"{random.randint(1, 99)} Port {random.choice(['Royal', 'Marina', 'Elite'])}\n{random.choice(['98000 Monaco', '06400 Cannes', '83990 Saint-Tropez'])}\n{random.choice(['Monaco', 'France', 'Italy'])}",
                    'contact': f"Captain {random.choice(['Jean-Luc', 'Alessandro', 'William', 'Francesco'])} {random.choice(['Moreau', 'Rossi', 'Smith', 'Costa'])}",
                    'email': f"{generated_company.lower().replace(' ', '').replace('.', '')}@{random.choice(['monaco', 'riviera', 'charter'])}.{random.choice(['mc', 'com', 'fr'])}",
                    'phone': f"+{random.choice(['377', '33', '39'])} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}"
                }
                st.info(f"🔄 New company: **{generated_company}**")
        
        with col3:
            if st.button("💡 Company Examples", key="btn_company_3"):
                company_examples = [
                    "Monaco Elite Charters Ltd.",
                    "Riviera Prestige Marine",
                    "Azure Coast Yachting",
                    "Mediterranean Royal Group",
                    "Diamond Seas International",
                    "Premier Monaco Maritime"
                ]
                st.table(pd.DataFrame(company_examples, columns=["Charter Companies"]))
        
        # AI Client Generator
        st.markdown("#### 👥 Charter Client Generator")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            if st.button("🎲 Generate Charter Client", key="btn_client"):
                # Client name components
                first_names = ["James", "William", "Alexander", "Charles", "Robert", "Michael", "David", "Richard"]
                last_names = ["Richardson", "Hamilton", "Wellington", "Morrison", "Thompson", "Anderson", "Williams", "Johnson"]
                titles = ["Mr. & Mrs.", "Dr. & Mrs.", "Sir & Lady", "Mr.", "Ms.", "Dr."]
                locations = ["London", "New York", "Geneva", "Zurich", "Paris", "Milan", "Dubai", "Hong Kong"]
                streets = ["Berkeley Square", "Park Avenue", "Rue de la Paix", "Via Montenapoleone", "Bahnhofstrasse"]
                
                title = random.choice(titles)
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                location = random.choice(locations)
                
                generated_client = f"{title} {first_name} {last_name}"
                st.session_state.ai_generated_lessee = {
                    'name': generated_client,
                    'address': f"{random.randint(1, 999)} {random.choice(streets)}\n{location} {random.choice(['W1J 5AT', '10021', '1201', '75001', '20121'])}\n{random.choice(['United Kingdom', 'United States', 'Switzerland', 'France', 'Italy'])}",
                    'contact': first_name + " " + last_name,
                    'email': f"{first_name.lower()}.{last_name.lower()}@{random.choice(['email', 'gmail', 'outlook'])}.com",
                    'phone': f"+{random.choice(['44', '1', '41', '33', '39'])} {random.randint(10, 99)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
                }
                st.success(f"👥 Generated client: **{generated_client}**")
        
        with col2:
            if st.button("🔄 Another Client", key="btn_client_2"):
                # Client name components (defined here for scope)
                first_names = ["James", "William", "Alexander", "Charles", "Robert", "Michael", "David", "Richard"]
                last_names = ["Richardson", "Hamilton", "Wellington", "Morrison", "Thompson", "Anderson", "Williams", "Johnson"]
                titles = ["Mr. & Mrs.", "Dr. & Mrs.", "Sir & Lady", "Mr.", "Ms.", "Dr."]
                locations = ["London", "New York", "Geneva", "Zurich", "Paris", "Milan", "Dubai", "Hong Kong"]
                streets = ["Berkeley Square", "Park Avenue", "Rue de la Paix", "Via Montenapoleone", "Bahnhofstrasse"]
                
                title = random.choice(titles)
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                location = random.choice(locations)
                
                generated_client = f"{title} {first_name} {last_name}"
                st.session_state.ai_generated_lessee = {
                    'name': generated_client,
                    'address': f"{random.randint(1, 999)} {random.choice(streets)}\n{location} {random.choice(['W1J 5AT', '10021', '1201', '75001', '20121'])}\n{random.choice(['United Kingdom', 'United States', 'Switzerland', 'France', 'Italy'])}",
                    'contact': first_name + " " + last_name,
                    'email': f"{first_name.lower()}.{last_name.lower()}@{random.choice(['email', 'gmail', 'outlook'])}.com",
                    'phone': f"+{random.choice(['44', '1', '41', '33', '39'])} {random.randint(10, 99)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
                }
                st.info(f"🔄 New client: **{generated_client}**")
        
        with col3:
            if st.button("💡 Client Examples", key="btn_client_3"):
                client_examples = [
                    "Mr. & Mrs. Richardson",
                    "Sir & Lady Hamilton",
                    "Dr. & Mrs. Wellington",
                    "Mr. Alexander Morrison",
                    "Ms. Charlotte Thompson",
                    "Dr. William Anderson"
                ]
                st.table(pd.DataFrame(client_examples, columns=["Charter Clients"]))
        
        st.markdown("---")
        
        # Selected clauses summary for contract generation (moved to left column)
        if 'selected_clauses' in st.session_state and st.session_state.selected_clauses:
            with st.expander(f"📋 Selected Additional Clauses ({len(st.session_state.selected_clauses)} clauses will be added to contract)", expanded=False):
                for clause in st.session_state.selected_clauses:
                    st.markdown(f"• **{clause['name']}** *(from {clause['category']})*")
                st.info(f"💡 These {len(st.session_state.selected_clauses)} clause(s) will be automatically included in the generated contract. You can manage them in the Clause Library.")
        
        # Comprehensive contract form in left column
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
    
    # In the RIGHT column - Summary, Preview, and Actions
    with right_col:
        st.markdown("## 📊 Contract Summary & Preview")
        
        # Check if contract has been generated (either from form submission or already in session state)
        contract_generated = hasattr(st.session_state, 'contract_html') and st.session_state.contract_html
        
        # If contract is not generated yet, show placeholder
        if not contract_generated:
            st.info("📝 Complete the form and click 'Generate Enhanced Contract' to see your contract preview here.")
            st.markdown("#### 📈 Contract Analytics")
            sample_col1, sample_col2, sample_col3, sample_col4 = st.columns(4)
            metric_style = """
            <style>
            .custom-metric {
                background: #7E50EA;
                border: 1px solid #e5e7eb;
                padding: 0.5rem 0.5rem 0.3rem 0.5rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                text-align: center;
                margin-bottom: 0.5rem;
            }
            .custom-metric-label {
                font-size: 0.85rem;
                font-weight: 600;
                color: white;
                margin-bottom: 0.2rem;
                display: block;
            }
            .custom-metric-value {
                font-size: 1.1rem;
                font-weight: 700;
                color: white;
                margin-bottom: 0.1rem;
                display: block;
            }
            .custom-metric-help {
                font-size: 0.7rem;
                color: #e5e7eb;
                margin-top: 0.1rem;
                display: block;
            }
            </style>
            """
            st.markdown(metric_style, unsafe_allow_html=True)
            with sample_col1:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Contract Value</span>
                        <span class="custom-metric-value">€ --,---</span>
                        <span class="custom-metric-help">Total charter value</span>
                    </div>''', unsafe_allow_html=True)
            with sample_col2:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Charter Duration</span>
                        <span class="custom-metric-value">-- days</span>
                        <span class="custom-metric-help">Length of charter</span>
                    </div>''', unsafe_allow_html=True)
            with sample_col3:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Risk Score</span>
                        <span class="custom-metric-value">--.- (--)</span>
                        <span class="custom-metric-help">Risk assessment</span>
                    </div>''', unsafe_allow_html=True)
            with sample_col4:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Vessel LOA</span>
                        <span class="custom-metric-value">--m</span>
                        <span class="custom-metric-help">Length overall</span>
                    </div>''', unsafe_allow_html=True)

            # All following sections should NOT be indented under any column
            st.markdown("#### 📑 Contract Preview")
            st.info("Contract preview will appear here after generation.")

            st.markdown("#### 📥 Download Options")
            st.info("Download options will be available after contract generation.")

            st.markdown("#### 🚀 Actions")
            st.info("Additional actions will be available after contract generation.")

            st.markdown("#### 📋 Version History")
            st.info("Version history will be available after contract generation and saving new versions.")
    
    # Contract generation logic (moved outside of form)
    if submitted:
        # Enhanced risk score calculation using the new risk assessment system
        enhanced_risk_score = 1.0
        risk_factors_count = len(risk_factors)
        
        # Use enhanced risk assessment if available
        if hasattr(st.session_state, 'risk_assessment_report') and st.session_state.risk_assessment_report:
            enhanced_risk_score = st.session_state.risk_assessment_report['overall_score']
            risk_category = st.session_state.risk_assessment_report['risk_level']
            st.info(f"🎯 Using Enhanced Risk Assessment: Score {enhanced_risk_score:.2f} ({risk_category})")
        else:
            # Fallback to basic risk calculation
            if charter_experience == "First Time":
                enhanced_risk_score += 0.6
            elif charter_experience == "Occasional (2-3 times)":
                enhanced_risk_score += 0.3
            
            enhanced_risk_score += risk_factors_count * 0.2
            risk_category = "Low" if enhanced_risk_score < 1.3 else "Medium" if enhanced_risk_score < 1.7 else "High"
            st.warning("⚠️ Using basic risk calculation. Visit Risk Assessment page for comprehensive analysis.")
        
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
            
            # Enhanced Risk Assessment Object
            'risk_assessment': {
                'risk_score': f"{enhanced_risk_score:.2f}",
                'risk_category': risk_category,
                'recommended_hull_insurance': int(hull_insurance * enhanced_risk_score),
                'recommended_liability_insurance': int(liability_insurance * enhanced_risk_score),
                'recommendations': [
                    f"Charter experience level: {charter_experience}",
                    f"Risk factors identified: {len(risk_factors)}",
                    f"Operational area: {operational_area[:50]}..."
                ],
                'regional_warnings': [
                    "Ensure all documentation is current for operational areas",
                    "Verify local maritime regulations compliance"
                ] if "Remote Destinations" in risk_factors else [],
                'enhanced_assessment': st.session_state.get('risk_assessment_report', {}),
                'mitigation_strategies': st.session_state.get('selected_mitigations', [])
            },
            
            # Contract Clauses
            'suggested_clauses': suggested_clauses,
            'additional_clauses': [clause for clause in st.session_state.get('selected_clauses', []) if clause.get('category') != 'Services'],
            'services_clauses': [clause for clause in st.session_state.get('selected_clauses', []) if clause.get('category') == 'Services'],
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
        
        # Force a rerun to ensure everything refreshes properly
        st.rerun()
    
    # If contract exists in session state, display it in the right column
    if hasattr(st.session_state, 'contract_html') and st.session_state.contract_html:
        # Display existing contract in right column
        with right_col:
            # Get data from session state
            contract_html = st.session_state.contract_html
            contract_data = st.session_state.contract_data
            
            st.success("🎉 Enhanced Contract Generated Successfully!")
            
            # Contract summary metrics
            st.markdown("#### 📈 Contract Analytics")
            col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     st.metric("Contract Value", f"{contract_data.get('currency', 'EUR')} {contract_data.get('total_charter_value', '0')}", help="Total charter value")
            # with col2:
            #     st.metric("Charter Duration", f"{contract_data.get('charter_duration', '0')} days", help="Length of charter")
            # with col3:
            #     risk_score = contract_data.get('risk_assessment', {}).get('risk_score', '0.0')
            #     risk_category = contract_data.get('risk_assessment', {}).get('risk_category', 'Unknown')
            #     st.metric("Risk Score", f"{risk_score} ({risk_category})", help="Risk assessment")
            # with col4:
            #     st.metric("Vessel LOA", f"{contract_data.get('length_overall', '0')}m", help="Length overall")
            
            metric_style = """
            <style>
            .custom-metric {
                background: #7E50EA;
                border: 1px solid #e5e7eb;
                padding: 0.5rem 0.5rem 0.3rem 0.5rem;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                text-align: center;
                margin-bottom: 0.5rem;
            }
            .custom-metric-label {
                font-size: 0.85rem;
                font-weight: 600;
                color: white;
                margin-bottom: 0.2rem;
                display: block;
            }
            .custom-metric-value {
                font-size: 1.1rem;
                font-weight: 700;
                color: white;
                margin-bottom: 0.1rem;
                display: block;
            }
            .custom-metric-help {
                font-size: 0.7rem;
                color: #e5e7eb;
                margin-top: 0.1rem;
                display: block;
            }
            </style>
            """

           
            st.markdown(metric_style, unsafe_allow_html=True)
            with col1:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Contract Value</span>
                        <span class="custom-metric-value">'''f"{contract_data.get('currency', 'EUR')} {contract_data.get('total_charter_value', '0')}"'''</span>
                        <span class="custom-metric-help">Total charter value</span>
                    </div>''', unsafe_allow_html=True)
            with col2:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Charter Duration</span>
                        <span class="custom-metric-value">'''f"{contract_data.get('charter_duration', '0')}"''' days</span>
                        <span class="custom-metric-help">Length of charter</span>
                    </div>''', unsafe_allow_html=True)
            with col3:
                risk_score = contract_data.get('risk_assessment', {}).get('risk_score', '0.0')
                risk_category = contract_data.get('risk_assessment', {}).get('risk_category', 'Unknown')
                # Set background color based on risk_category
                if risk_category == "Medium":
                    bg_color = "#FAC898"
                elif risk_category == "High":
                    bg_color = "#F9136D"
                elif risk_category == "Critical":
                    bg_color = "#8b0000"
                else:
                    bg_color = "#4DC786"  # default

                st.markdown(
                    f'''<div class="custom-metric" style="background: {bg_color};">
                        <span class="custom-metric-label">Risk Score</span>
                        <span class="custom-metric-value">{risk_score} ({risk_category})</span>
                        <span class="custom-metric-help">Risk assessment</span>
                    </div>''', unsafe_allow_html=True)
            with col4:
                st.markdown(
                    '''<div class="custom-metric">
                        <span class="custom-metric-label">Vessel LOA</span>
                        <span class="custom-metric-value">'''f"{contract_data.get('length_overall', '0')}m"'''</span>
                        <span class="custom-metric-help">Length overall</span>
                    </div>''', unsafe_allow_html=True)

            # Display contract preview
            st.markdown("#### 📑 Contract Preview")
            with st.expander("View Full Contract", expanded=True):
                st.components.v1.html(contract_html, height=600, scrolling=True)
            
            # Download options
            st.markdown("#### 📥 Download Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Download HTML Contract",
                    data=contract_html,
                    file_name=f"yacht_contract_{contract_data['contract_id']}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                # Generate PDF
                pdf_filename = f"yacht_contract_{contract_data['contract_id']}.pdf"
                generate_pdf_contract(contract_html, pdf_filename, contract_data)
                
                with open(pdf_filename, 'rb') as pdf_file:
                    st.download_button(
                        label="� Download PDF Contract",
                        data=pdf_file.read(),
                        file_name=pdf_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            with col3:
                # Contract data as JSON
                contract_json = json.dumps(contract_data, indent=2, default=str)
                st.download_button(
                    label="� Download Contract Data",
                    data=contract_json,
                    file_name=f"contract_data_{contract_data['contract_id']}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Additional actions
            st.markdown("#### 🚀 Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("� Send via Email", key="btn_email_send"):
                    st.success("📧 Email functionality will be implemented in future version")
            
            with col2:
                if st.button("💾 Save to Database", key="btn_save_db"):
                    st.success("💾 Contract saved to database")
            
            with col3:
                if st.button("🔄 Create New Version", key="btn_new_version"):
                    st.success("� New version functionality will be implemented")
            
            # Version History
            st.markdown("#### 📋 Version History")
            
            # Sample version data for demonstration
            version_data = [
                {"Version": "1.0", "Contract ID": contract_data['contract_id'], "Date": contract_data['agreement_date'], "Status": "Current"},
                {"Version": "0.9", "Contract ID": "A1B2C3D4", "Date": "20 July 2025", "Status": "Previous"},
                {"Version": "0.8", "Contract ID": "E5F6G7H8", "Date": "15 July 2025", "Status": "Draft"}
            ]
            
            df = pd.DataFrame(version_data)
            st.dataframe(df, use_container_width=True)
            
            # Option to download previous versions
            selected_version = st.selectbox(
                "Select version to download:", 
                options=[f"v{row['Version']} ({row['Contract ID']})" for _, row in df.iterrows()],
                key="version_select_download"
            )
            
            if st.button("📥 Download Selected Version", key="btn_download_version"):
                st.success("📥 Version downloaded successfully")
    

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
                if st.button(f"📄 Preview", key="btn_13"):
                    st.success("Template previewed")
                    
            template_select = st.selectbox(
                "Select Template",
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
        
        if st.button("💾 Save New Template", key="btn_14"):
            st.success("Template saved successfully")
            
        variable_name = st.text_input("Variable Name", placeholder="e.g., custom_clause_1")
        variable_type = st.selectbox("Variable Type", ["Text", "Number", "Date", "Boolean", "List"])
        variable_description = st.text_input("Description", placeholder="Description of this variable")
        
        if st.button("➕ Add Variable", key="btn_var_1"):
            st.success(f"Variable '{variable_name}' added to template")
        
        # Save changes button
        if st.button("💾 Save Changes", key="btn_15"):
            st.success("Changes saved successfully")
            
        selected_category = "Cancellation"
        if selected_category == "Cancellation":
            clauses = [
                "Standard Cancellation Terms",
                "Flexible Cancellation (Force Majeure)",
                "No-Refund Policy",
                "Graduated Cancellation Fees"
            ]
        else:
            clauses = [f"Sample {selected_category} Clause 1", f"Sample {selected_category} Clause 2"]
        
        selected_clause = st.selectbox("Available Clauses", clauses)
        
        if st.button("👁️ Preview Clause", key="btn_preview_clause"):
            st.info(f"Previewing: {selected_clause}")
            st.code("""
PAYMENT TERMS: The charter fee shall be paid as follows:
- 50% deposit due upon execution of this agreement
- 50% balance due 30 days prior to charter commencement
- All payments to be made in the currency specified herein
- Late payment penalties may apply as per local regulations
            """)
    
    with col2:
        st.markdown("#### ✨ Clause Suggestions")
        
        # AI-powered clause suggestions
        charter_type = st.selectbox("Charter Type", 
            ["Bareboat", "Crewed", "Corporate", "Racing"], 
            key="btn_16"
        )
        
        suggested_clauses = [
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
    
    if st.button("💾 Save Custom Clause", key="btn_17"):
        st.success("Custom clause saved successfully")

def template_analytics_section():
    st.subheader("📊 Template Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Usage Trends")
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
        if st.button("📦 Export All Templates", key="btn_export_templates"):
            st.success("Templates exported to yacht_templates_backup.zip")
        
        st.file_uploader("📂 Import Templates", key="btn_18")
        
    # This appears to be misplaced code for a category selector
    # Fixing the structure
    category_selector = st.selectbox(
        "Select Category",
        ["All Templates", "Bareboat", "Crewed", "Corporate", "Racing"],
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
        for custom_clause in st.session_state.custom_clauses:
            clause_category = custom_clause.get('category', 'Custom Clauses')
            if clause_category in clause_database:
                # Add custom clause to existing category
                clause_database[clause_category].append(custom_clause)
            else:
                # Create new category for custom clauses
                clause_database[clause_category] = [custom_clause]
    
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
                            if st.button(f"✏️ Edit", key=f"edit_custom_browse_{idx}"):
                                # Store the clause to edit in session state
                                st.session_state.edit_clause_mode = True
                                st.session_state.edit_clause_data = {
                                    'name': clause['name'],
                                    'content': clause['content'],
                                    'category': 'Custom Clauses',
                                    'source': 'custom',
                                    'index': idx
                                }
                                st.success(f"Opening editor for: {clause['name']}")
                                st.info("💡 Navigate to the 'Clause Editor' tab to modify this clause")
                                st.rerun()
                        
                        with col_add:
                            if st.button(f"➕ Add", key=f"add_custom_browse_{idx}"):
                                # Check if clause is already selected
                                clause_exists = any(sc['name'] == clause['name'] for sc in st.session_state.selected_clauses)
                                
                                if not clause_exists:
                                    selected_clause = {
                                        'name': clause['name'],
                                        'content': clause['content'],
                                        'category': 'Custom Clauses',
                                        'source': 'custom'
                                    }
                                    st.session_state.selected_clauses.append(selected_clause)
                                    st.success(f"✅ Added '{clause['name']}' to current contract!")
                                else:
                                    st.warning(f"⚠️ '{clause['name']}' is already added to the contract!")
                        
                        with col_delete:
                            if st.button(f"🗑️ Delete", key=f"delete_custom_browse_{idx}"):
                                st.error(f"Deleted clause: {clause['name']}")
                                
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
                    if st.button("📋 Copy", key="btn_21"):
                        selected_clause = {
                            'name': clause['name'],
                            'content': clause['content'],
                            'category': clause.get('category', 'General'),
                            'source': clause.get('source', 'library')
                        }
                        
                        clause_exists = any(sc['name'] == clause['name'] for sc in st.session_state.selected_clauses)
                        
                        if not clause_exists:
                            st.session_state.selected_clauses.append(selected_clause)
                            st.success(f"✅ Added '{clause['name']}' to current contract!")
                        else:
                            st.warning(f"⚠️ '{clause['name']}' is already added to the contract!")
                            
                with col4:
                    if st.button("📊 Usage Stats", key="btn_22"):
                        st.info(f"Usage statistics for {clause['name']}")

def clause_library_search_section():
    st.subheader("🔍 Clause Search")
    
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
    if st.button("🔍 Search Clauses", key="btn_23"):
        st.success("Searching clauses with the specified criteria")
        
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
             "Force Majeure", "Dispute Resolution", "Safety Requirements", "Environmental Compliance",
             "Crew Provisions", "Guest Services", "Equipment Standards", "Weather Contingency", 
             "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services"]
        )
    with col3:
        clause_complexity = st.selectbox("Complexity Level", ["Basic", "Standard", "Advanced", "Expert"])    # Metadata
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
        
        if st.button("➕ Add Variable", key="btn_var_2"):
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
        if st.button("💾 Save as Draft", key="btn_25"):
            st.success("Clause saved as draft")
            
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
        if st.button("💾 Save Changes", key="btn_5"):
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
        if st.button("🔄 Revert Changes", key="btn_6"):
            st.info("Changes reverted to last saved version")
            st.rerun()  # Refresh to show original content
            
    with col3:
        if st.button("📤 Submit for Review", key="btn_7"):
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
        if st.button("📋 Create New Version", key="btn_8"):
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
            ["Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations",
             "Force Majeure", "Dispute Resolution", "Safety Requirements", "Environmental Compliance",
             "Crew Provisions", "Guest Services", "Equipment Standards", "Weather Contingency", 
             "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services"],
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
    
    if st.button("📋 Create Modified Copy", key="btn_31"):
        st.success("Modified copy created successfully!")

def bulk_import_editor():
    st.markdown("### 📤 Bulk Import Clauses")
    
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
            
            if st.button("📥 Import All Clauses", key="btn_var_9"):
                st.success("Successfully imported 3 clauses to library!")
    
    elif import_method == "Paste JSON Data":
        json_data = st.text_area(
            "Paste JSON Data", key="btn_32",
            height=200,
            placeholder='{"clauses": [{"name": "...", "content": "..."}]}'
        )
        
        if json_data and st.button("📥 Import from JSON", key="btn_var_10"):
            st.success("Clauses imported successfully!")

def ai_suggestions_section():
    st.subheader("🤖 Clause Suggestions")
    
    # AI suggestion interface
    st.markdown("### 🎯 Get Intelligent Clause Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        charter_description = st.text_area(
            "Describe your charter scenario",
            placeholder="e.g., 'High-value superyacht charter in Mediterranean waters for corporate client with 14-day duration'",
            height=100,
            help="Provide details about the charter to get relevant clause suggestions",
            key="charter_description"
        )
    
    with col2:
        # Context parameters
        st.markdown("#### Charter Parameters")
        charter_type = st.selectbox("Charter Type", ["Bareboat", "Crewed", "Corporate", "Racing", "Luxury"], key="ai_charter_type")
        charter_value = st.number_input("Charter Value (USD)", min_value=0, value=50000, step=5000, key="ai_charter_value")
        charter_duration = st.number_input("Duration (days)", min_value=1, value=7, step=1, key="ai_charter_duration")
        risk_factors = st.multiselect("Risk Factors", ["High seas", "Hurricane season", "Inexperienced crew", "High value cargo", "International waters"], key="ai_risk_factors")
    
    if st.button("🤖 Get Suggestions", key="btn_34"):
        st.success("Suggestions generated")
        
        # Example suggestion
        suggestion = {
            'clause': 'Weather Contingency Clause',
            'reason': 'Based on the hurricane season risk factor',
            'priority': 'Important',
            'category': 'Safety',
            'confidence': 89
        }
        
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
            if st.button("👁️ Preview", key="btn_35"):
                st.info(f"Previewing clause: {suggestion['clause']}")
                
        with col2:
            if st.button("➕ Add to Contract", key="btn_add_to_contract"):
                selected_clause = {
                    'name': suggestion['clause'],
                    'content': "Sample clause content for " + suggestion['clause'],
                    'category': suggestion['category'],
                    'source': 'AI'
                }
                
                if 'selected_clauses' not in st.session_state:
                    st.session_state.selected_clauses = []
                    
                clause_exists = any(sc['name'] == suggestion['clause'] for sc in st.session_state.selected_clauses)
                
                if not clause_exists:
                    st.session_state.selected_clauses.append(selected_clause)
                    st.success(f"✅ Added {suggestion['clause']} to contract!")
                else:
                    st.warning(f"⚠️ {suggestion['clause']} is already added to the contract!")
                    
        with col3:
            if st.button("❌ Dismiss", key="btn_36"):
                st.info(f"Dismissed suggestion: {suggestion['clause']}")
        
        st.markdown("### 📊 Clause Usage Analytics")
        
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
            st.checkbox("Enable Suggestions", value=True)
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
            if st.button("➕ Add User", key="btn_11"):
                st.success(f"User {new_user_email} added with {new_user_role} role")
    
    with tab3:
        st.markdown("#### 📚 Content Management")
        
        # Bulk operations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Version Management**")
            
            # Create example version info
            version_info = [
                {
                    'Version': '1.0', 
                    'Contract ID': 'YC-2023-001',
                    'Vessel': 'Ocean Explorer',
                    'Created': '2023-07-01',
                    'Size (KB)': 125.4
                },
                {
                    'Version': '1.1', 
                    'Contract ID': 'YC-2023-002',
                    'Vessel': 'Sea Breeze',
                    'Created': '2023-07-15',
                    'Size (KB)': 132.1
                }
            ]
            
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
                if st.button("👁️ Preview Version", key="btn_38"):
                    st.success("Previewing selected version")
                    
            with col3:
                if st.button("📥 Download Version", key="btn_39"):
                    st.success("Downloading selected version")
                            
                    # Example timeline visualization
                    st.markdown("### 📊 Version Timeline")
                    
                    import pandas as pd
                    
                    # Create sample timeline data
                    timeline_data = {
                        'Date': ['2023-06-01', '2023-07-15', '2023-08-20', '2023-09-10'],
                        'Version': ['1.0', '1.1', '1.2', '2.0']
                    }
                    
                    # Display as a table
                    df_timeline = pd.DataFrame(timeline_data)
                    st.dataframe(df_timeline, use_container_width=True)

def template_manager_page(systems):
    """Comprehensive Template Management System"""
    st.header("📋 Template Manager")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📚 Template Library", 
        "✏️ Edit Templates", 
        "🔧 Clause Builder", 
        "📊 Template Analytics", 
        "⚙️ Settings"
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
    """Rich template library with cards and filtering"""
    st.subheader("� Template Library")
    
    # Search and filter controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_query = st.text_input("🔍 Search Templates", placeholder="Search by name, description...")
    
    with col2:
        category_filter = st.selectbox("📂 Category", 
            ["All Categories", "Bareboat Charter", "Crewed Charter", "Corporate Charter", "Luxury Superyacht", "Racing Charter"])
    
    with col3:
        jurisdiction_filter = st.selectbox("🌍 Jurisdiction",
            ["All Jurisdictions", "International", "Mediterranean (EU)", "Caribbean", "US Waters", "UK/Gibraltar"])
    
    with col4:
        sort_by = st.selectbox("📊 Sort By", 
            ["Name", "Last Updated", "Usage Count", "Rating", "Category"])
    
    st.markdown("---")
    
    # Sample templates data
    templates = [
        {
            'name': 'Mediterranean Bareboat Charter',
            'description': 'Comprehensive bareboat charter template optimized for Mediterranean waters with EU compliance.',
            'category': 'Bareboat Charter',
            'jurisdiction': 'Mediterranean (EU)',
            'status': 'Active',
            'version': '2.1',
            'last_updated': '2025-07-15',
            'usage_count': 234,
            'rating': 4.8,
            'features': ['Multi-language', 'Weather Clauses', 'Insurance Integration', 'Digital Signatures']
        },
        {
            'name': 'Caribbean Crewed Superyacht',
            'description': 'Luxury crewed charter template for superyachts in Caribbean waters with comprehensive service levels.',
            'category': 'Luxury Superyacht',
            'jurisdiction': 'Caribbean',
            'status': 'Active',
            'version': '1.8',
            'last_updated': '2025-07-10',
            'usage_count': 189,
            'rating': 4.9,
            'features': ['Crew Provisions', 'Luxury Amenities', 'VIP Services', 'Gourmet Catering']
        },
        {
            'name': 'Corporate Charter Agreement',
            'description': 'Professional corporate charter template with liability coverage and team-building provisions.',
            'category': 'Corporate Charter',
            'jurisdiction': 'International',
            'status': 'Active',
            'version': '3.0',
            'last_updated': '2025-06-20',
            'usage_count': 145,
            'rating': 4.6,
            'features': ['Corporate Liability', 'Team Building', 'Business Insurance', 'Flexible Scheduling']
        },
        {
            'name': 'Racing Charter Template',
            'description': 'Specialized template for racing charters with performance clauses and competition requirements.',
            'category': 'Racing Charter',
            'jurisdiction': 'International',
            'status': 'Beta',
            'version': '1.2',
            'last_updated': '2025-07-01',
            'usage_count': 97,
            'rating': 4.7,
            'features': ['Performance Metrics', 'Racing Rules', 'Equipment Lists', 'Competition Clauses']
        },
        {
            'name': 'Basic Day Charter',
            'description': 'Simple day charter template for short-term recreational use.',
            'category': 'Bareboat Charter',
            'jurisdiction': 'International',
            'status': 'Active',
            'version': '1.5',
            'last_updated': '2025-06-15',
            'usage_count': 312,
            'rating': 4.3,
            'features': ['Simplified Terms', 'Day Use Only', 'Basic Insurance', 'Quick Setup']
        }
    ]
    
    # Display templates as cards
    for template in templates:
        # Create template card
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #e5e7eb; 
                border-radius: 12px; 
                padding: 20px; 
                margin: 15px 0; 
                background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            ">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex-grow: 1;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <h3 style="margin: 0; color: #1f2937; font-size: 18px; font-weight: 600;">
                                📄 {template['name']}
                            </h3>
                        </div>
                        
                        <p style="margin: 8px 0; color: #6b7280; font-size: 14px; line-height: 1.5;">
                            {template['description']}
                        </p>
                        
                        <div style="display: flex; gap: 8px; margin: 12px 0; flex-wrap: wrap;">
                            <span style="background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
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
                if st.button(f"📄 Preview", key=f"preview_{template['name'].lower().replace(' ', '_')}"):
                    st.info(f"Previewing {template['name']} template...")
            with col2:
                if st.button(f"📝 Use Template", key=f"use_{template['name'].lower().replace(' ', '_')}"):
                    st.success(f"Using {template['name']} as base template!")
            with col3:
                if st.button(f"✏️ Edit", key=f"edit_{template['name'].lower().replace(' ', '_')}"):
                    st.info(f"Opening {template['name']} for editing...")
            with col4:
                if st.button(f"📋 Duplicate", key=f"duplicate_{template['name'].lower().replace(' ', '_')}"):
                    st.success(f"Created copy of {template['name']}!")
            with col5:
                if st.button(f"🗑️ Delete", key=f"delete_{template['name'].lower().replace(' ', '_')}"):
                    st.warning(f"Are you sure you want to delete {template['name']}?")
    
    # Add new template button
    st.markdown("---")
    if st.button("➕ Create New Template", key="create_new_template_btn"):
        st.info("Opening template creation wizard...")

def template_editor_section():
    """Template editing interface"""
    st.subheader("✏️ Template Editor")
    
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
        
        if st.button("💾 Save New Template", key="save_new_template_btn"):
            st.success(f"New template '{template_name}' saved successfully!")
    
    else:
        st.markdown(f"### ✏️ Editing: {selected_template}")
        
        if template_action == "Edit Content":
            st.markdown("#### 📝 Template Content")
            current_content = st.text_area(
                "HTML Content",
                height=400,
                value="<div>Current template content...</div>",
                help="Edit the template HTML structure and content"
            )
        
        elif template_action == "Configure Variables":
            st.markdown("#### 🔧 Template Variables")
            
            # Variable management
            st.markdown("**Add New Variable:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                variable_name = st.text_input("Variable Name", placeholder="e.g., custom_clause_1")
            with col2:
                variable_type = st.selectbox("Variable Type", ["Text", "Number", "Date", "Boolean", "List"])
            with col3:
                variable_description = st.text_input("Description", placeholder="Description of this variable")
            
            if st.button("➕ Add Variable", key="add_variable_btn"):
                st.success(f"Variable '{variable_name}' added to template")
        
        # Save changes button
        if st.button("💾 Save Changes", key="save_template_changes_btn"):
            st.success("Template changes saved successfully!")

def clause_builder_section():
    """Advanced clause building interface"""
    st.subheader("🔧 Clause Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Clause Library")
        
        clause_categories = ["Payment Terms", "Cancellation Policy", "Insurance Requirements", 
                           "Force Majeure", "Liability", "Vessel Condition", "Crew Provisions", "Services"]
        
        selected_category = st.selectbox("Clause Category", clause_categories, key="clause_category_select")
        
        # Show relevant clauses based on category
        if selected_category == "Payment Terms":
            clauses = [
                "Standard Payment Schedule",
                "Graduated Payment Plan", 
                "Corporate Account Terms",
                "Seasonal Adjustment Clause"
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
        
        if st.button("👁️ Preview Clause", key="preview_clause_btn"):
            st.info(f"Previewing: {selected_clause}")
            st.code("""
PAYMENT TERMS: The charter fee shall be paid as follows:
- 50% deposit due upon execution of this agreement
- 50% balance due 30 days prior to charter commencement
- All payments to be made in the currency specified herein
- Late payment penalties may apply as per local regulations
            """)
    
    with col2:
        st.markdown("#### ✨ Suggestions")
        
        # AI-powered clause suggestions
        charter_type = st.selectbox("Charter Type", 
            ["Bareboat", "Crewed", "Corporate", "Racing"], key="ai_charter_type")
        
        if charter_type:
            suggested_clauses = [
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
    
    if st.button("💾 Save Custom Clause", key="save_custom_clause_btn"):
        st.success(f"Custom clause '{clause_title}' saved successfully!")

def template_analytics_section():
    """Template usage analytics and insights"""
    st.subheader("📊 Template Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Template Usage Trends")
        # Placeholder for usage chart
        chart_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
            'Usage': [45, 67, 89, 123, 156, 178, 234]
        }
        st.line_chart(chart_data)
    
    with col2:
        st.markdown("#### 🥧 Template Categories")
        # Placeholder for category distribution
        category_data = {
            'Category': ['Bareboat', 'Crewed', 'Corporate', 'Racing', 'Luxury'],
            'Count': [45, 32, 18, 12, 8]
        }
        st.bar_chart(category_data)
    
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
    """Template system settings"""
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
        st.number_input("Page Margins (mm)", min_value=10, max_value=50, value=20)
        
        if st.button("💾 Save Styling Settings", key="save_styling_settings_btn"):
            st.success("Styling settings saved successfully!")

def risk_assessment_page(systems):
    st.header("⚠️ Enhanced Risk Assessment System")
    st.markdown("### Comprehensive Risk Analysis & Management for Yacht Charters")
    
    # Initialize risk categories and factors in session state
    if 'risk_categories' not in st.session_state:
        st.session_state.risk_categories = {
            'operational': {
                'name': 'Operational Risk',
                'weight': 0.3,
                'color': '#ff6b6b',
                'factors': {
                    'High Season Charter': {'weight': 0.8, 'description': 'Charter during peak season with high demand'},
                    'Remote Destinations': {'weight': 1.2, 'description': 'Operating in remote or poorly serviced areas'},
                    'Extreme Weather Season': {'weight': 1.5, 'description': 'Charter during hurricane or storm season'},
                    'High Traffic Waters': {'weight': 0.6, 'description': 'Operating in congested shipping lanes'},
                    'Night Navigation': {'weight': 0.9, 'description': 'Extended night sailing requirements'}
                }
            },
            'financial': {
                'name': 'Financial Risk',
                'weight': 0.25,
                'color': '#4ecdc4',
                'factors': {
                    'High Value Charter': {'weight': 1.0, 'description': 'Charter value exceeds €500,000'},
                    'Complex Payment Terms': {'weight': 0.7, 'description': 'Non-standard payment schedule'},
                    'Currency Risk': {'weight': 0.8, 'description': 'Multi-currency transactions'},
                    'Late Payment History': {'weight': 1.3, 'description': 'Client has history of payment delays'},
                    'No Credit Check': {'weight': 1.1, 'description': 'Client credit not verified'}
                }
            },
            'regulatory': {
                'name': 'Regulatory Risk',
                'weight': 0.2,
                'color': '#45b7d1',
                'factors': {
                    'Political Instability': {'weight': 1.4, 'description': 'Operating in politically unstable regions'},
                    'Multiple Jurisdictions': {'weight': 0.9, 'description': 'Charter crosses multiple legal jurisdictions'},
                    'Complex Customs': {'weight': 0.8, 'description': 'Complex customs and immigration requirements'},
                    'Environmental Restrictions': {'weight': 0.7, 'description': 'Operating in protected marine areas'},
                    'Flag State Issues': {'weight': 1.2, 'description': 'Vessel flagged in problematic jurisdiction'}
                }
            },
            'human': {
                'name': 'Human Factor Risk',
                'weight': 0.15,
                'color': '#96ceb4',
                'factors': {
                    'Inexperienced Guests': {'weight': 1.1, 'description': 'First-time or inexperienced charterers'},
                    'Large Guest Count': {'weight': 0.8, 'description': 'Maximum capacity charter'},
                    'Crew Shortage': {'weight': 1.3, 'description': 'Operating with minimum crew'},
                    'Language Barriers': {'weight': 0.6, 'description': 'Communication challenges with guests'},
                    'Special Needs Guests': {'weight': 0.9, 'description': 'Guests with medical or accessibility needs'}
                }
            },
            'technical': {
                'name': 'Technical Risk',
                'weight': 0.1,
                'color': '#feca57',
                'factors': {
                    'Aging Vessel': {'weight': 1.2, 'description': 'Vessel over 15 years old'},
                    'Complex Systems': {'weight': 0.9, 'description': 'Advanced technical systems requiring expertise'},
                    'Recent Repairs': {'weight': 0.8, 'description': 'Major systems recently repaired'},
                    'Equipment Limitations': {'weight': 0.7, 'description': 'Missing standard safety/comfort equipment'},
                    'Maintenance Overdue': {'weight': 1.5, 'description': 'Overdue maintenance items'}
                }
            }
        }
    
    # Initialize mitigation strategies
    if 'mitigation_strategies' not in st.session_state:
        st.session_state.mitigation_strategies = {
            'insurance_adjustment': {
                'name': 'Insurance Coverage Adjustment',
                'description': 'Increase insurance coverage based on risk profile',
                'effectiveness': 0.8,
                'cost_impact': 'Medium',
                'implementation': 'Contact insurance provider to adjust coverage levels'
            },
            'crew_enhancement': {
                'name': 'Enhanced Crew Requirements',
                'description': 'Additional qualified crew members for high-risk charters',
                'effectiveness': 0.7,
                'cost_impact': 'High',
                'implementation': 'Hire additional certified crew members'
            },
            'equipment_upgrade': {
                'name': 'Safety Equipment Upgrade',
                'description': 'Additional safety and communication equipment',
                'effectiveness': 0.6,
                'cost_impact': 'Medium',
                'implementation': 'Install additional safety systems and equipment'
            },
            'route_modification': {
                'name': 'Route and Timing Optimization',
                'description': 'Modify charter route to reduce exposure to risks',
                'effectiveness': 0.9,
                'cost_impact': 'Low',
                'implementation': 'Plan alternative routes avoiding high-risk areas'
            },
            'documentation_enhancement': {
                'name': 'Enhanced Documentation',
                'description': 'Additional legal clauses and waivers',
                'effectiveness': 0.5,
                'cost_impact': 'Low',
                'implementation': 'Add comprehensive risk-specific contract clauses'
            },
            'pre_charter_briefing': {
                'name': 'Comprehensive Safety Briefing',
                'description': 'Extended safety briefing and guest orientation',
                'effectiveness': 0.6,
                'cost_impact': 'Low',
                'implementation': 'Conduct detailed pre-charter safety and operational briefing'
            }
        }
    
    # Main interface tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Risk Dashboard", "⚙️ Risk Configuration", "🎯 Risk Analysis", "🛡️ Mitigation Strategies", "📋 Generate Report"])
    
    with tab1:
        st.markdown("#### 📊 Risk Assessment Dashboard")
        
        # Calculate current risk scores
        total_risk_score = 0
        category_scores = {}
        active_factors = {}
        
        for category_key, category in st.session_state.risk_categories.items():
            category_risk = 0
            category_active_factors = []
            
            for factor_key, factor in category['factors'].items():
                if st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False):
                    factor_score = factor['weight']
                    category_risk += factor_score
                    category_active_factors.append({
                        'name': factor_key,
                        'weight': factor['weight'],
                        'description': factor['description']
                    })
            
            weighted_category_score = category_risk * category['weight']
            category_scores[category_key] = {
                'raw_score': category_risk,
                'weighted_score': weighted_category_score,
                'active_factors': category_active_factors
            }
            total_risk_score += weighted_category_score
            active_factors[category_key] = category_active_factors
        
        # Overall risk metrics
        risk_level = "Low" if total_risk_score < 1.0 else "Medium" if total_risk_score < 2.0 else "High" if total_risk_score < 3.0 else "Critical"
        risk_color = "#28a745" if risk_level == "Low" else "#ffc107" if risk_level == "Medium" else "#fd7e14" if risk_level == "High" else "#dc3545"
        
        # Risk overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div style="background: {risk_color}; padding: 1rem; border-radius: 8px; text-align: center; color: white;">
                <h3 style="margin: 0; color: white;">Overall Risk Score</h3>
                <h2 style="margin: 0.5rem 0; color: white;">{total_risk_score:.2f}</h2>
                <p style="margin: 0; color: white;">{risk_level} Risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            active_factor_count = sum(len(factors) for factors in active_factors.values())
            st.metric("Active Risk Factors", active_factor_count, help="Total number of active risk factors")
        
        with col3:
            highest_category = max(category_scores.items(), key=lambda x: x[1]['weighted_score']) if category_scores else ("None", {"weighted_score": 0})
            st.metric("Highest Risk Category", 
                     st.session_state.risk_categories[highest_category[0]]['name'] if highest_category[0] != "None" else "None",
                     f"{highest_category[1]['weighted_score']:.2f}")
        
        with col4:
            recommended_mitigations = min(3, max(1, int(total_risk_score)))
            st.metric("Recommended Mitigations", recommended_mitigations, help="Suggested number of mitigation strategies")
        
        st.markdown("---")
        
        # Risk category breakdown charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk category pie chart
            if any(score['weighted_score'] > 0 for score in category_scores.values()):
                fig_pie = go.Figure(data=[go.Pie(
                    labels=[st.session_state.risk_categories[cat]['name'] for cat, score in category_scores.items() if score['weighted_score'] > 0],
                    values=[score['weighted_score'] for cat, score in category_scores.items() if score['weighted_score'] > 0],
                    marker_colors=[st.session_state.risk_categories[cat]['color'] for cat, score in category_scores.items() if score['weighted_score'] > 0],
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Score: %{value:.2f}<br>Percentage: %{percent}<extra></extra>'
                )])
                fig_pie.update_layout(
                    title="Risk Distribution by Category",
                    showlegend=True,
                    height=400
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("📊 Risk distribution chart will appear when risk factors are selected")
        
        with col2:
            # Risk factor bar chart
            if active_factor_count > 0:
                all_active_factors = []
                for category_key, factors in active_factors.items():
                    for factor in factors:
                        all_active_factors.append({
                            'name': factor['name'][:20] + "..." if len(factor['name']) > 20 else factor['name'],
                            'weight': factor['weight'],
                            'category': st.session_state.risk_categories[category_key]['name']
                        })
                
                if all_active_factors:
                    fig_bar = go.Figure(data=[go.Bar(
                        x=[factor['weight'] for factor in all_active_factors],
                        y=[factor['name'] for factor in all_active_factors],
                        orientation='h',
                        marker_color=[st.session_state.risk_categories[cat_key]['color'] 
                                    for cat_key in st.session_state.risk_categories.keys()
                                    for factor in active_factors.get(cat_key, [])],
                        hovertemplate='<b>%{y}</b><br>Weight: %{x}<br>Category: %{customdata}<extra></extra>',
                        customdata=[factor['category'] for factor in all_active_factors]
                    )])
                    fig_bar.update_layout(
                        title="Active Risk Factors by Weight",
                        xaxis_title="Risk Weight",
                        yaxis_title="Risk Factors",
                        height=400
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("📊 Active risk factors chart will appear when factors are selected")
        
        # Detailed risk breakdown
        if active_factor_count > 0:
            st.markdown("#### 🔍 Detailed Risk Analysis")
            for category_key, category in st.session_state.risk_categories.items():
                if category_scores[category_key]['active_factors']:
                    with st.expander(f"{category['name']} - Score: {category_scores[category_key]['weighted_score']:.2f}", expanded=False):
                        for factor in category_scores[category_key]['active_factors']:
                            st.markdown(f"""
                            **{factor['name']}** (Weight: {factor['weight']})  
                            {factor['description']}
                            """)
    
    with tab2:
        st.markdown("#### ⚙️ Risk Factor Configuration")
        st.info("Configure risk categories, factors, and their weights. Changes will be applied immediately.")
        
        # Category weight adjustment
        st.markdown("##### 📊 Category Weight Distribution")
        
        total_weight = 0
        new_weights = {}
        
        for category_key, category in st.session_state.risk_categories.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{category['name']}**")
            
            with col2:
                new_weight = st.slider(
                    f"Weight",
                    min_value=0.0,
                    max_value=1.0,
                    value=category['weight'],
                    step=0.05,
                    key=f"weight_{category_key}",
                    help=f"Adjust the importance of {category['name']} in overall risk calculation"
                )
                new_weights[category_key] = new_weight
                total_weight += new_weight
            
            with col3:
                st.metric("Current", f"{category['weight']:.2f}")
        
        # Update weights button
        if st.button("🔄 Update Category Weights"):
            # Normalize weights to sum to 1.0
            if total_weight > 0:
                for category_key in st.session_state.risk_categories.keys():
                    st.session_state.risk_categories[category_key]['weight'] = new_weights[category_key] / total_weight
                st.success("✅ Category weights updated and normalized!")
                st.rerun()
            else:
                st.error("❌ Total weight cannot be zero!")
        
        if total_weight != 1.0:
            st.warning(f"⚠️ Total weight is {total_weight:.2f}. Weights will be normalized to sum to 1.0 when updated.")
        
        st.markdown("---")
        
        # Risk factor management
        st.markdown("##### 🎯 Risk Factor Management")
        
        selected_category = st.selectbox(
            "Select Category to Manage",
            options=list(st.session_state.risk_categories.keys()),
            format_func=lambda x: st.session_state.risk_categories[x]['name']
        )
        
        if selected_category:
            category = st.session_state.risk_categories[selected_category]
            
            st.markdown(f"**Managing: {category['name']}**")
            
            # Display existing factors
            st.markdown("**Existing Risk Factors:**")
            
            factors_to_remove = []
            for factor_key, factor in category['factors'].items():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    new_description = st.text_input(
                        "Description",
                        value=factor['description'],
                        key=f"desc_{selected_category}_{factor_key}"
                    )
                
                with col2:
                    new_weight = st.number_input(
                        "Weight",
                        value=factor['weight'],
                        min_value=0.1,
                        max_value=2.0,
                        step=0.1,
                        key=f"factor_weight_{selected_category}_{factor_key}"
                    )
                
                with col3:
                    if st.button("💾", key=f"save_{selected_category}_{factor_key}", help="Save changes"):
                        st.session_state.risk_categories[selected_category]['factors'][factor_key]['description'] = new_description
                        st.session_state.risk_categories[selected_category]['factors'][factor_key]['weight'] = new_weight
                        st.success("✅ Factor updated!")
                        st.rerun()
                
                with col4:
                    if st.button("🗑️", key=f"delete_{selected_category}_{factor_key}", help="Delete factor"):
                        factors_to_remove.append(factor_key)
            
            # Remove factors
            for factor_key in factors_to_remove:
                del st.session_state.risk_categories[selected_category]['factors'][factor_key]
                st.success(f"✅ Removed factor: {factor_key}")
                st.rerun()
            
            st.markdown("---")
            
            # Add new factor
            st.markdown("**Add New Risk Factor:**")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_factor_name = st.text_input("Factor Name", key="new_factor_name")
                new_factor_desc = st.text_input("Factor Description", key="new_factor_desc")
            
            with col2:
                new_factor_weight = st.number_input("Weight", value=1.0, min_value=0.1, max_value=2.0, step=0.1, key="new_factor_weight")
            
            with col3:
                if st.button("➕ Add Factor"):
                    if new_factor_name and new_factor_desc:
                        st.session_state.risk_categories[selected_category]['factors'][new_factor_name] = {
                            'weight': new_factor_weight,
                            'description': new_factor_desc
                        }
                        st.success(f"✅ Added new factor: {new_factor_name}")
                        st.rerun()
                    else:
                        st.error("❌ Please provide both name and description!")
    
    with tab3:
        st.markdown("#### 🎯 Interactive Risk Analysis")
        st.info("Select risk factors that apply to your charter to calculate the overall risk score.")
        
        # Risk factor selection interface
        for category_key, category in st.session_state.risk_categories.items():
            with st.expander(f"{category['name']} (Weight: {category['weight']:.2f})", expanded=True):
                
                category_col1, category_col2 = st.columns([3, 1])
                
                with category_col1:
                    st.markdown(f"<div style='background: {category['color']}; padding: 0.5rem; border-radius: 4px; color: white; font-weight: bold; text-align: center;'>{category['name']}</div>", unsafe_allow_html=True)
                
                with category_col2:
                    # Category-wide toggle
                    if st.button(f"Toggle All", key=f"toggle_all_{category_key}"):
                        current_state = any(st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False) 
                                          for factor_key in category['factors'].keys())
                        for factor_key in category['factors'].keys():
                            st.session_state[f"risk_factor_{category_key}_{factor_key}"] = not current_state
                        st.rerun()
                
                # Individual factor selection
                for factor_key, factor in category['factors'].items():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Initialize the session state if it doesn't exist
                        if f"risk_factor_{category_key}_{factor_key}" not in st.session_state:
                            st.session_state[f"risk_factor_{category_key}_{factor_key}"] = False
                        
                        factor_selected = st.checkbox(
                            f"**{factor_key}**",
                            key=f"risk_factor_{category_key}_{factor_key}",
                            help=factor['description']
                        )
                    
                    with col2:
                        st.metric("Weight", f"{factor['weight']}")
                    
                    with col3:
                        factor_selected = st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False)
                        if factor_selected:
                            impact = factor['weight'] * category['weight']
                            st.metric("Impact", f"{impact:.3f}")
                        else:
                            st.write("")
                    
                    factor_selected = st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False)
                    if factor_selected:
                        st.markdown(f"*{factor['description']}*")
                
                st.markdown("---")
    
    with tab4:
        st.markdown("#### 🛡️ Risk Mitigation Strategies")
        
        # Calculate current risk for recommendations
        current_risk_score = sum(
            sum(factor['weight'] for factor_key, factor in category['factors'].items() 
                if st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False)) * category['weight']
            for category_key, category in st.session_state.risk_categories.items()
        )
        
        if current_risk_score > 0:
            st.success(f"📊 Current Risk Score: {current_risk_score:.2f}")
            
            # Recommend mitigation strategies based on risk level
            recommended_count = min(3, max(1, int(current_risk_score)))
            st.markdown(f"##### 💡 Recommended Mitigation Strategies ({recommended_count} strategies)")
            
            # Sort strategies by effectiveness for recommendations
            sorted_strategies = sorted(
                st.session_state.mitigation_strategies.items(),
                key=lambda x: x[1]['effectiveness'],
                reverse=True
            )
            
            selected_mitigations = []
            
            for i, (strategy_key, strategy) in enumerate(sorted_strategies[:recommended_count + 2]):
                with st.expander(f"{strategy['name']} (Effectiveness: {strategy['effectiveness']:.0%})", expanded=i < recommended_count):
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {strategy['description']}")
                        st.markdown(f"**Implementation:** {strategy['implementation']}")
                    
                    with col2:
                        effectiveness_color = "#28a745" if strategy['effectiveness'] > 0.7 else "#ffc107" if strategy['effectiveness'] > 0.5 else "#fd7e14"
                        st.markdown(f"<div style='background: {effectiveness_color}; padding: 0.5rem; border-radius: 4px; color: white; text-align: center;'><strong>Effectiveness<br>{strategy['effectiveness']:.0%}</strong></div>", unsafe_allow_html=True)
                    
                    with col3:
                        cost_color = "#dc3545" if strategy['cost_impact'] == "High" else "#ffc107" if strategy['cost_impact'] == "Medium" else "#28a745"
                        st.markdown(f"<div style='background: {cost_color}; padding: 0.5rem; border-radius: 4px; color: white; text-align: center;'><strong>Cost Impact<br>{strategy['cost_impact']}</strong></div>", unsafe_allow_html=True)
                    
                    # Selection checkbox
                    if st.checkbox(f"Include in contract recommendations", key=f"select_mitigation_{strategy_key}"):
                        selected_mitigations.append({
                            'name': strategy['name'],
                            'description': strategy['description'],
                            'implementation': strategy['implementation'],
                            'effectiveness': strategy['effectiveness'],
                            'cost_impact': strategy['cost_impact']
                        })
            
            # Store selected mitigations for contract generation
            st.session_state.selected_mitigations = selected_mitigations
            
            if selected_mitigations:
                st.success(f"✅ {len(selected_mitigations)} mitigation strategies selected for contract inclusion")
        
        else:
            st.info("📊 Configure risk factors in the Risk Analysis tab to see mitigation recommendations")
        
        # Custom mitigation strategy
        st.markdown("---")
        st.markdown("##### ➕ Add Custom Mitigation Strategy")
        
        with st.form("custom_mitigation"):
            col1, col2 = st.columns(2)
            
            with col1:
                custom_name = st.text_input("Strategy Name")
                custom_description = st.text_area("Description")
                custom_implementation = st.text_area("Implementation Steps")
            
            with col2:
                custom_effectiveness = st.slider("Effectiveness", 0.0, 1.0, 0.7, 0.1)
                custom_cost = st.selectbox("Cost Impact", ["Low", "Medium", "High"])
            
            if st.form_submit_button("➕ Add Custom Strategy"):
                if custom_name and custom_description:
                    st.session_state.mitigation_strategies[custom_name.lower().replace(' ', '_')] = {
                        'name': custom_name,
                        'description': custom_description,
                        'implementation': custom_implementation,
                        'effectiveness': custom_effectiveness,
                        'cost_impact': custom_cost
                    }
                    st.success(f"✅ Added custom mitigation strategy: {custom_name}")
                    st.rerun()
                else:
                    st.error("❌ Please provide at least name and description")
    
    with tab5:
        st.markdown("#### 📋 Risk Assessment Report Generation")
        
        # Calculate comprehensive risk assessment
        final_risk_score = sum(
            sum(factor['weight'] for factor_key, factor in category['factors'].items() 
                if st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False)) * category['weight']
            for category_key, category in st.session_state.risk_categories.items()
        )
        
        if final_risk_score > 0:
            # Generate comprehensive report
            st.markdown("##### 📊 Executive Risk Summary")
            
            risk_level = "Low" if final_risk_score < 1.0 else "Medium" if final_risk_score < 2.0 else "High" if final_risk_score < 3.0 else "Critical"
            
            # Risk summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Risk Score", f"{final_risk_score:.2f}")
            with col2:
                st.metric("Risk Level", risk_level)
            with col3:
                active_factors = sum(
                    sum(1 for factor_key in category['factors'].keys() 
                        if st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False))
                    for category_key, category in st.session_state.risk_categories.items()
                )
                st.metric("Active Risk Factors", active_factors)
            
            # Detailed risk breakdown for report
            report_data = {
                'overall_score': final_risk_score,
                'risk_level': risk_level,
                'category_breakdown': {},
                'active_factors': [],
                'selected_mitigations': st.session_state.get('selected_mitigations', [])
            }
            
            for category_key, category in st.session_state.risk_categories.items():
                category_factors = []
                category_score = 0
                
                for factor_key, factor in category['factors'].items():
                    if st.session_state.get(f"risk_factor_{category_key}_{factor_key}", False):
                        factor_info = {
                            'name': factor_key,
                            'weight': factor['weight'],
                            'description': factor['description']
                        }
                        category_factors.append(factor_info)
                        report_data['active_factors'].append(factor_info)
                        category_score += factor['weight']
                
                if category_factors:
                    report_data['category_breakdown'][category_key] = {
                        'name': category['name'],
                        'weight': category['weight'],
                        'raw_score': category_score,
                        'weighted_score': category_score * category['weight'],
                        'factors': category_factors
                    }
            
            # Store report data for contract generation
            st.session_state.risk_assessment_report = report_data
            
            # Display report preview
            st.markdown("##### 📄 Report Preview")
            
            with st.expander("🔍 View Full Risk Assessment Report", expanded=True):
                st.markdown(f"""
                **YACHT CHARTER RISK ASSESSMENT REPORT**
                
                **Overall Assessment:**
                - Risk Score: {final_risk_score:.2f}
                - Risk Level: {risk_level}
                - Total Active Risk Factors: {len(report_data['active_factors'])}
                
                **Risk Category Breakdown:**
                """)
                
                for category_key, category_data in report_data['category_breakdown'].items():
                    st.markdown(f"""
                    **{category_data['name']}**
                    - Category Weight: {category_data['weight']:.2f}
                    - Raw Score: {category_data['raw_score']:.2f}
                    - Weighted Score: {category_data['weighted_score']:.2f}
                    
                    Active Factors:
                    """)
                    for factor in category_data['factors']:
                        st.markdown(f"   • {factor['name']} (Weight: {factor['weight']}) - {factor['description']}")
                    st.markdown("")
                
                if report_data['selected_mitigations']:
                    st.markdown("**Recommended Mitigation Strategies:**")
                    for mitigation in report_data['selected_mitigations']:
                        st.markdown(f"""
                        **{mitigation['name']}** (Effectiveness: {mitigation['effectiveness']:.0%})
                        - {mitigation['description']}
                        - Implementation: {mitigation['implementation']}
                        """)
            
            st.success("✅ Risk assessment report generated and ready for contract integration!")
            st.info("💡 This risk assessment data will be automatically included in contracts generated from the Contract Generator page.")
            
        else:
            st.info("📊 Complete risk factor selection in the Risk Analysis tab to generate a comprehensive report.")

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
    # Check if there's an active edit session to highlight the editor tab
    editor_tab_title = "✏️ Clause Editor"
    if hasattr(st.session_state, 'edit_clause_mode') and st.session_state.edit_clause_mode:
        editor_tab_title = "🔥 Clause Editor (ACTIVE)"
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📚 Browse Clauses", 
        "🔍 Search & Filter", 
        editor_tab_title, 
        "🤖 Auto Suggestions",
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
    col1, col2, col3, col4, col5 = st.columns(5)
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
    with col5:
        if st.button("🔧 Services", use_container_width=True):
            st.session_state.selected_category = "Services"
            st.rerun()
    
    # Initialize selected category
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "Payment Terms"
    
    # Available categories
    available_categories = [
        "Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations", 
        "Force Majeure", "Dispute Resolution", "Delivery Terms", "Safety Requirements", 
        "Environmental Compliance", "Crew Provisions", "Guest Services", "Equipment Standards",
        "Weather Contingency", "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services"
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
    
    # Get clause database from centralized function
    clause_database = get_clause_database()
    
    # Merge custom clauses with default database
    if 'custom_clauses' in st.session_state:
        for custom_clause in st.session_state.custom_clauses:
            clause_category = custom_clause.get('category', 'Custom Clauses')
            if clause_category in clause_database:
                # Add custom clause to existing category
                clause_database[clause_category].append(custom_clause)
            else:
                # Create new category for custom clauses
                clause_database[clause_category] = [custom_clause]
    
    # Display clauses for selected category
    if category in clause_database:
        clauses = clause_database[category]
        
        # Get custom clauses for the selected category
        custom_clauses_list = []
        if 'custom_clauses' in st.session_state:
            custom_clauses_list = [clause for clause in st.session_state.custom_clauses 
                                 if clause.get('category') == category]
        
        # Get versioned clauses for the selected category
        versioned_clauses_list = []
        if 'clause_versions' in st.session_state:
            for original_key, versions in st.session_state.clause_versions.items():
                for version in versions:
                    if version.get('category') == category:
                        versioned_clauses_list.append(version)
        
        # Separate default, custom, and versioned clauses for better display
        default_clauses = [c for c in clauses if c.get('status') not in ['Custom', 'Modified']]
        
        total_count = len(clauses) + len(custom_clauses_list) + len(versioned_clauses_list)
        custom_count = len(custom_clauses_list)
        version_count = len(versioned_clauses_list)
        
        st.markdown(f"### {category} Clauses ({total_count} available)")
        if custom_count > 0:
            st.info(f"📝 {custom_count} custom clause(s) created by you")
        if version_count > 0:
            st.info(f"🔄 {version_count} modified version(s) of library clauses")
        
        # Display custom clauses first with special styling
        if custom_clauses_list:
            st.markdown("#### 📝 Your Custom Clauses")
            for idx, clause in enumerate(custom_clauses_list):
                with st.expander(f"🌟 {clause['name']} (v{clause.get('version', '1.0')}) - Custom Creation"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### Clause Content")
                        st.code(clause['content'], language='text')
                        
                        if clause.get('legal_notes'):
                            st.markdown("#### 📋 Legal Notes")
                            st.info(clause['legal_notes'])
                    
                    with col2:
                        st.markdown("#### 📊 Clause Details")
                        st.markdown(f"**Version:** {clause.get('version', '1.0')}")
                        st.markdown(f"**Status:** {clause.get('status', 'Custom')}")
                        st.markdown(f"**Complexity:** {clause.get('complexity', 'Standard')}")
                        st.markdown(f"**Author:** {clause.get('author', 'User Created')}")
                        st.markdown(f"**Created:** {clause.get('last_updated', 'Unknown')}")
                        st.markdown(f"**Usage:** {clause.get('usage_count', 0)} times")
                        st.markdown(f"**Rating:** ⭐ {clause.get('rating', 4.0)}/5.0")
                        
                        if clause.get('applicable_to'):
                            st.markdown("**Applicable to:**")
                            for item in clause['applicable_to']:
                                st.markdown(f"• {item}")
                        
                        # Action buttons for custom clauses
                        col_edit, col_add, col_delete = st.columns(3)
                        
                        with col_edit:
                            if st.button(f"✏️ Edit", key=f"edit_custom_{idx}"):
                                # Store the clause to edit in session state
                                st.session_state.edit_clause_mode = True
                                st.session_state.edit_clause_data = {
                                    'name': clause['name'],
                                    'content': clause['content'],
                                    'category': clause.get('category', 'Custom Clauses'),
                                    'source': 'custom',
                                    'version': clause.get('version', '1.0'),
                                    'priority': clause.get('priority', 'Medium'),
                                    'jurisdiction': clause.get('jurisdiction', ['International']),
                                    'language': clause.get('language', 'English'),
                                    'complexity': clause.get('complexity', 'Standard'),
                                    'rating': clause.get('rating', 4.0),
                                    'usage_count': clause.get('usage_count', 0),
                                    'author': clause.get('author', 'User Created'),
                                    'applicable_to': clause.get('applicable_to', []),
                                    'legal_notes': clause.get('legal_notes', ''),
                                    'related_clauses': clause.get('related_clauses', []),
                                    'risk_level': clause.get('risk_level', 'Medium')
                                }
                                st.success(f"Opening editor for: {clause['name']}")
                                st.info("💡 Navigate to the 'Clause Editor' tab to modify this clause")
                                st.rerun()
                        
                        with col_add:
                            if st.button(f"🔗 Add to Contract", key=f"add_custom_{idx}"):
                                # Initialize selected clauses in session state if not exists
                                if 'selected_clauses' not in st.session_state:
                                    st.session_state.selected_clauses = []
                                
                                # Create a clause object for the contract
                                selected_clause = {
                                    'name': clause['name'],
                                    'content': clause['content'],
                                    'category': clause.get('category', 'Custom Clauses'),
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
                                st.session_state.custom_clauses.remove(clause)
                                st.success("Custom clause deleted!")
                                st.rerun()
        
        # Display versioned clauses (modified library clauses)
        if versioned_clauses_list:
            st.markdown("#### 🔄 Modified Library Clauses")
            for idx, clause in enumerate(versioned_clauses_list):
                with st.expander(f"📝 {clause['name']} ({clause.get('version', 'v2.0')}) - Modified"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("#### Clause Content")
                        st.code(clause['content'], language='text')
                        
                        # Show modification info
                        st.markdown("#### 🔄 Modification Info")
                        st.info(f"**Base Version:** {clause.get('base_version', 'v1.0')} | **Your Version:** {clause.get('version', 'v2.0')}")
                        if clause.get('modification_notes'):
                            st.caption(f"📝 {clause.get('modification_notes')}")
                        
                        if clause.get('legal_notes'):
                            st.markdown("#### 📋 Legal Notes")
                            st.info(clause['legal_notes'])
                    
                    with col2:
                        st.markdown("#### 📊 Clause Details")
                        st.markdown(f"**Version:** {clause.get('version', 'v2.0')}")
                        st.markdown(f"**Status:** {clause.get('status', 'Modified')}")
                        st.markdown(f"**Complexity:** {clause.get('complexity', 'Standard')}")
                        st.markdown(f"**Original Author:** {clause.get('author', 'Unknown')}")
                        st.markdown(f"**Modified:** {clause.get('last_updated', 'Unknown')}")
                        st.markdown(f"**Usage:** {clause.get('usage_count', 0)} times")
                        st.markdown(f"**Rating:** ⭐ {clause.get('rating', 4.0)}/5.0")
                        
                        if clause.get('applicable_to'):
                            st.markdown("**Applicable to:**")
                            for item in clause['applicable_to']:
                                st.markdown(f"• {item}")
                        
                        # Action buttons for versioned clauses
                        col_edit, col_add = st.columns(2)
                        
                        with col_edit:
                            if st.button(f"✏️ Edit", key=f"edit_version_{idx}"):
                                # Store the clause to edit in session state
                                st.session_state.edit_clause_mode = True
                                st.session_state.edit_clause_data = {
                                    'name': clause['name'],
                                    'content': clause['content'],
                                    'category': clause.get('category', category),
                                    'source': 'version',
                                    'version': clause.get('version', 'v2.0'),
                                    'priority': clause.get('priority', 'Medium'),
                                    'jurisdiction': clause.get('jurisdiction', ['International']),
                                    'language': clause.get('language', 'English'),
                                    'complexity': clause.get('complexity', 'Standard'),
                                    'rating': clause.get('rating', 4.0),
                                    'usage_count': clause.get('usage_count', 0),
                                    'author': clause.get('author', 'Unknown'),
                                    'applicable_to': clause.get('applicable_to', []),
                                    'legal_notes': clause.get('legal_notes', ''),
                                    'related_clauses': clause.get('related_clauses', []),
                                    'risk_level': clause.get('risk_level', 'Medium')
                                }
                                st.success(f"Opening editor for: {clause['name']} ({clause.get('version', 'v2.0')})")
                                st.info("💡 Navigate to the 'Clause Editor' tab to modify this version")
                                st.rerun()
                        
                        with col_add:
                            if st.button(f"🔗 Add to Contract", key=f"add_version_{idx}"):
                                # Initialize selected clauses in session state if not exists
                                if 'selected_clauses' not in st.session_state:
                                    st.session_state.selected_clauses = []
                                
                                # Create a clause object for the contract
                                selected_clause = {
                                    'name': f"{clause['name']} ({clause.get('version', 'v2.0')})",
                                    'content': clause['content'],
                                    'category': clause.get('category', category),
                                    'source': 'version'
                                }
                                
                                # Check if clause is already selected
                                clause_exists = any(sc['name'] == selected_clause['name'] for sc in st.session_state.selected_clauses)
                                
                                if not clause_exists:
                                    st.session_state.selected_clauses.append(selected_clause)
                                    st.success(f"✅ Added '{selected_clause['name']}' to current contract!")
                                else:
                                    st.warning(f"⚠️ '{selected_clause['name']}' is already added to the contract!")
            
            st.markdown("---")
        
        # Display default library clauses
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
                        # Store the clause to edit in session state
                        st.session_state.edit_clause_mode = True
                        st.session_state.edit_clause_data = {
                            'name': clause['name'],
                            'content': clause['content'],
                            'category': category,
                            'source': 'library',
                            'index': idx
                        }
                        st.success(f"✅ Editor prepared for: {clause['name']}")
                        st.warning("� **ACTION REQUIRED:** Click on the '✏️ Clause Editor' tab above to start editing this clause")
                        st.rerun()
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
    search_executed = st.button("🔍 Search Clauses", type="primary")
    
    # Store search results in session state for persistence
    if search_executed:
        if search_query:
            # Perform actual search across the clause database
            search_results = perform_clause_search(search_query, filter_category, filter_jurisdiction, 
                                                 filter_complexity, filter_language, usage_range, rating_range)
            
            # Store results and query in session state
            st.session_state.current_search_results = search_results
            st.session_state.current_search_query = search_query
            st.session_state.search_executed = True
        else:
            st.session_state.current_search_results = []
            st.session_state.current_search_query = ""
            st.session_state.search_executed = False
            st.info("Enter search terms to find relevant clauses")
    
    # Display search results if they exist (from current search or previous searches)
    if hasattr(st.session_state, 'search_executed') and st.session_state.search_executed and hasattr(st.session_state, 'current_search_results'):
        st.markdown("### 📋 Search Results")
        
        search_results = st.session_state.current_search_results
        search_query = st.session_state.current_search_query
        
        if search_results:
                # Initialize session state for search results management
                if 'search_results_expanded' not in st.session_state:
                    st.session_state.search_results_expanded = {}
                if 'search_results_selected' not in st.session_state:
                    st.session_state.search_results_selected = []
                
                st.success(f"Found {len(search_results)} clauses matching '{search_query}'")
                
                # Results display options
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    results_per_page = st.selectbox("Results per page", [5, 10, 20, 50], index=1)
                with col2:
                    if st.button("📋 Select All Visible", key="select_all_results"):
                        # Select all results on current page
                        start_idx = (st.session_state.current_search_page - 1) * results_per_page
                        end_idx = min(start_idx + results_per_page, len(search_results))
                        page_results = search_results[start_idx:end_idx]
                        
                        for result in page_results:
                            result_key = f"{result['name']}_{result['category']}"
                            if result_key not in st.session_state.search_results_selected:
                                st.session_state.search_results_selected.append(result_key)
                with col3:
                    if st.button("🗑️ Clear Selection", key="clear_selection"):
                        st.session_state.search_results_selected = []
                        st.rerun()
                
                # Show selected count
                if st.session_state.search_results_selected:
                    st.info(f"📌 {len(st.session_state.search_results_selected)} clause(s) selected for addition to contract")
                
                # Pagination logic
                total_results = len(search_results)
                if 'current_search_page' not in st.session_state:
                    st.session_state.current_search_page = 1
                
                max_page = (total_results - 1) // results_per_page + 1
                
                # Page navigation
                if max_page > 1:
                    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                    with col1:
                        if st.button("⬅️ Previous", disabled=st.session_state.current_search_page <= 1):
                            st.session_state.current_search_page -= 1
                            # Only rerun for pagination since we need to recalculate page content
                            st.rerun()
                    with col2:
                        if st.button("➡️ Next", disabled=st.session_state.current_search_page >= max_page):
                            st.session_state.current_search_page += 1
                            # Only rerun for pagination since we need to recalculate page content
                            st.rerun()
                    with col3:
                        st.markdown(f"**Page {st.session_state.current_search_page} of {max_page}** ({total_results} total results)")
                    with col4:
                        if st.button("⬆️ First"):
                            st.session_state.current_search_page = 1
                            # Only rerun for pagination since we need to recalculate page content
                            st.rerun()
                    with col5:
                        if st.button("⬇️ Last"):
                            st.session_state.current_search_page = max_page
                            # Only rerun for pagination since we need to recalculate page content
                            st.rerun()
                
                # Calculate slice for current page
                start_idx = (st.session_state.current_search_page - 1) * results_per_page
                end_idx = start_idx + results_per_page
                page_results = search_results[start_idx:end_idx]
                
                # Display search results with enhanced functionality
                for i, result in enumerate(page_results):
                    result_key = f"{result['name']}_{result['category']}"
                    is_selected = result_key in st.session_state.search_results_selected
                    is_expanded = st.session_state.search_results_expanded.get(result_key, False)
                    
                    # Enhanced result container with selection
                    border_color = "#4CAF50" if is_selected else "#ddd"
                    bg_color = "#f0fff0" if is_selected else "white"
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="border: 2px solid {border_color}; border-radius: 8px; padding: 15px; margin: 10px 0; background: {bg_color};">
                            <div style="display: flex; justify-content: between; align-items: center;">
                                <h4 style="color: #1e3a8a; margin: 0; flex-grow: 1;">{result['name']}</h4>
                                <span style="background: #e3f2fd; color: #1565c0; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">
                                    {result['relevance']}% match
                                </span>
                            </div>
                            <p style="color: #666; margin: 5px 0;"><strong>Category:</strong> {result['category']} | 
                               <strong>Version:</strong> {result.get('version', '1.0')} | 
                               <strong>Rating:</strong> ⭐ {result.get('rating', 4.0)}/5.0 | 
                               <strong>Usage:</strong> {result.get('usage_count', 0)} times</p>
                            <p style="margin: 10px 0; font-style: italic;">{result['snippet']}{'...' if len(result.get('content', '')) > len(result['snippet']) else ''}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons row
                        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                        
                        with col1:
                            # Selection checkbox
                            selection_changed = st.checkbox(
                                "📌 Select", 
                                value=is_selected,
                                key=f"select_{result_key}_{start_idx + i}",
                                help="Select this clause to add to contract"
                            )
                            if selection_changed != is_selected:
                                if selection_changed:
                                    if result_key not in st.session_state.search_results_selected:
                                        st.session_state.search_results_selected.append(result_key)
                                else:
                                    if result_key in st.session_state.search_results_selected:
                                        st.session_state.search_results_selected.remove(result_key)
                                # State changes will be reflected automatically - no rerun needed
                        
                        with col2:
                            # View Full / Collapse button
                            if st.button(
                                "👁️ View Full" if not is_expanded else "📄 Collapse", 
                                key=f"expand_{result_key}_{start_idx + i}"
                            ):
                                st.session_state.search_results_expanded[result_key] = not is_expanded
                                # State changes will be reflected automatically - no rerun needed
                        
                        with col3:
                            # Copy content button
                            if st.button("📋 Copy", key=f"copy_{result_key}_{start_idx + i}"):
                                # Copy full content to clipboard (simulated with success message)
                                st.success(f"✅ Copied '{result['name']}' content to clipboard!")
                        
                        with col4:
                            # Quick add single clause
                            if st.button("🔗 Add", key=f"add_{result_key}_{start_idx + i}"):
                                add_clause_to_contract(result)
                                st.success(f"✅ Added '{result['name']}' to contract!")
                        
                        with col5:
                            # Edit this clause
                            if st.button("✏️ Edit", key=f"edit_{result_key}_{start_idx + i}"):
                                # Set edit mode for this clause
                                st.session_state.edit_clause_mode = True
                                st.session_state.edit_clause_data = {
                                    'name': result['name'],
                                    'content': result.get('content', result['snippet']),
                                    'category': result['category'],
                                    'source': result.get('source', 'library'),
                                    'version': result.get('version', '1.0'),
                                    'priority': 'Medium',
                                    'jurisdiction': result.get('jurisdiction', ['International']),
                                    'language': result.get('language', 'English'),
                                    'complexity': result.get('complexity', 'Standard'),
                                    'rating': result.get('rating', 4.0),
                                    'usage_count': result.get('usage_count', 0),
                                    'author': result.get('author', 'Unknown'),
                                    'applicable_to': result.get('applicable_to', []),
                                    'legal_notes': result.get('legal_notes', ''),
                                    'related_clauses': result.get('related_clauses', []),
                                    'risk_level': result.get('risk_level', 'Medium')
                                }
                                st.success(f"✅ Opening editor for '{result['name']}'")
                                st.info("💡 Navigate to the 'Clause Editor' tab to modify this clause")
                        
                        # Show full content if expanded
                        if is_expanded and result.get('content'):
                            st.markdown("#### 📄 Full Clause Content")
                            st.code(result['content'], language='text')
                            
                            # Additional metadata when expanded
                            if result.get('legal_notes'):
                                st.markdown("#### 📋 Legal Notes")
                                st.info(result['legal_notes'])
                            
                            if result.get('variables'):
                                st.markdown("#### 🔧 Template Variables")
                                for var in result['variables']:
                                    st.markdown(f"• `{{{{{var}}}}}`")
                            
                            if result.get('related_clauses'):
                                st.markdown("#### 🔗 Related Clauses")
                                for related in result['related_clauses']:
                                    st.markdown(f"• {related}")
                        
                        st.markdown("---")
                
                # Bulk actions for selected clauses
                if st.session_state.search_results_selected:
                    st.markdown("#### 🔄 Bulk Actions for Selected Clauses")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📥 Add All Selected to Contract", type="primary"):
                            added_count = 0
                            for selected_key in st.session_state.search_results_selected:
                                # Find the result by key
                                for result in search_results:
                                    if f"{result['name']}_{result['category']}" == selected_key:
                                        add_clause_to_contract(result)
                                        added_count += 1
                                        break
                            st.success(f"✅ Added {added_count} selected clauses to contract!")
                            st.session_state.search_results_selected = []  # Clear selection
                            st.rerun()
                    
                    with col2:
                        if st.button("📋 Copy All Selected"):
                            st.success(f"✅ Copied {len(st.session_state.search_results_selected)} clauses to clipboard!")
                    
                    with col3:
                        if st.button("📊 Create Comparison Report"):
                            st.info("📊 Comparison report feature coming soon!")
                
        else:
            st.warning(f"No clauses found matching '{search_query}' with current filters.")
            st.info("💡 Try adjusting your search terms or filters to find more results.")
    
    # Add a clear search button to reset results
    if hasattr(st.session_state, 'search_executed') and st.session_state.search_executed:
        if st.button("🗑️ Clear Search Results"):
            st.session_state.search_executed = False
            st.session_state.current_search_results = []
            st.session_state.current_search_query = ""
            st.session_state.search_results_expanded = {}
            st.session_state.search_results_selected = []
            if 'current_search_page' in st.session_state:
                st.session_state.current_search_page = 1
            st.rerun()

def perform_clause_search(query, categories=None, jurisdictions=None, complexity=None, 
                         languages=None, min_usage=0, min_rating=0.0):
    """Perform comprehensive search across all clause databases"""
    results = []
    
    # Get the clause database (same as used in browse_clauses_section)
    clause_database = get_clause_database()
    
    # Search through all categories
    for category, clauses in clause_database.items():
        # Apply category filter if specified
        if categories and category not in categories:
            continue
            
        for clause in clauses:
            # Apply filters
            if jurisdictions and not any(j in clause.get('jurisdiction', []) for j in jurisdictions):
                continue
            if complexity and clause.get('complexity') not in complexity:
                continue
            if languages and clause.get('language') not in languages:
                continue
            if clause.get('usage_count', 0) < min_usage:
                continue
            if clause.get('rating', 0) < min_rating:
                continue
            
            # Calculate relevance score
            relevance = calculate_relevance(query, clause)
            
            if relevance > 0:  # Only include if there's some relevance
                # Create snippet from content
                content = clause.get('content', '')
                snippet = create_snippet(query, content)
                
                result = {
                    'name': clause['name'],
                    'category': category,
                    'relevance': relevance,
                    'snippet': snippet,
                    'content': content,
                    'version': clause.get('version', '1.0'),
                    'rating': clause.get('rating', 4.0),
                    'usage_count': clause.get('usage_count', 0),
                    'complexity': clause.get('complexity', 'Standard'),
                    'jurisdiction': clause.get('jurisdiction', ['International']),
                    'language': clause.get('language', 'English'),
                    'author': clause.get('author', 'Unknown'),
                    'legal_notes': clause.get('legal_notes', ''),
                    'variables': clause.get('variables', []),
                    'related_clauses': clause.get('related_clauses', []),
                    'applicable_to': clause.get('applicable_to', []),
                    'risk_level': clause.get('risk_level', 'Medium'),
                    'source': 'library'
                }
                results.append(result)
    
    # Include custom clauses in search
    if 'custom_clauses' in st.session_state:
        for clause in st.session_state.custom_clauses:
            relevance = calculate_relevance(query, clause)
            if relevance > 0:
                content = clause.get('content', '')
                snippet = create_snippet(query, content)
                
                result = {
                    'name': clause['name'],
                    'category': clause.get('category', 'Custom'),
                    'relevance': relevance,
                    'snippet': snippet,
                    'content': content,
                    'version': clause.get('version', '1.0'),
                    'rating': clause.get('rating', 4.0),
                    'usage_count': clause.get('usage_count', 0),
                    'complexity': clause.get('complexity', 'Standard'),
                    'jurisdiction': clause.get('jurisdiction', ['International']),
                    'language': clause.get('language', 'English'),
                    'author': clause.get('author', 'User Created'),
                    'legal_notes': clause.get('legal_notes', ''),
                    'variables': clause.get('variables', []),
                    'related_clauses': clause.get('related_clauses', []),
                    'applicable_to': clause.get('applicable_to', []),
                    'risk_level': clause.get('risk_level', 'Medium'),
                    'source': 'custom'
                }
                results.append(result)
    
    # Include versioned clauses in search
    if 'clause_versions' in st.session_state:
        for original_key, versions in st.session_state.clause_versions.items():
            for version in versions:
                relevance = calculate_relevance(query, version)
                if relevance > 0:
                    content = version.get('content', '')
                    snippet = create_snippet(query, content)
                    
                    result = {
                        'name': f"{version['name']} ({version.get('version', 'v2.0')})",
                        'category': version.get('category', 'Modified'),
                        'relevance': relevance,
                        'snippet': snippet,
                        'content': content,
                        'version': version.get('version', 'v2.0'),
                        'rating': version.get('rating', 4.0),
                        'usage_count': version.get('usage_count', 0),
                        'complexity': version.get('complexity', 'Standard'),
                        'jurisdiction': version.get('jurisdiction', ['International']),
                        'language': version.get('language', 'English'),
                        'author': version.get('author', 'Modified'),
                        'legal_notes': version.get('legal_notes', ''),
                        'variables': version.get('variables', []),
                        'related_clauses': version.get('related_clauses', []),
                        'applicable_to': version.get('applicable_to', []),
                        'risk_level': version.get('risk_level', 'Medium'),
                        'source': 'version'
                    }
                    results.append(result)
    
    # Sort by relevance (highest first)
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return results

def calculate_relevance(query, clause):
    """Calculate relevance score for a clause based on search query"""
    query_lower = query.lower()
    score = 0
    
    # Check title match (highest weight)
    if query_lower in clause.get('name', '').lower():
        score += 50
    
    # Check content match (medium weight)
    content = clause.get('content', '').lower()
    query_words = query_lower.split()
    
    for word in query_words:
        if word in content:
            score += 10
        if word in clause.get('name', '').lower():
            score += 20
    
    # Check category match
    if query_lower in clause.get('category', '').lower():
        score += 30
    
    # Check legal notes match
    if query_lower in clause.get('legal_notes', '').lower():
        score += 15
    
    # Check applicable_to match
    applicable = ' '.join(clause.get('applicable_to', [])).lower()
    if query_lower in applicable:
        score += 20
    
    # Bonus for high-rated clauses
    rating = clause.get('rating', 0)
    if rating >= 4.5:
        score += 5
    elif rating >= 4.0:
        score += 3
    
    # Cap at 100%
    return min(score, 100)

def create_snippet(query, content, max_length=150):
    """Create a snippet from content highlighting the search query"""
    if not content:
        return "No content available"
    
    query_lower = query.lower()
    content_lower = content.lower()
    
    # Find the first occurrence of query terms
    query_words = query_lower.split()
    first_match_pos = len(content)
    
    for word in query_words:
        pos = content_lower.find(word)
        if pos != -1 and pos < first_match_pos:
            first_match_pos = pos
    
    # If no match found, return beginning of content
    if first_match_pos == len(content):
        return content[:max_length]
    
    # Create snippet around the match
    start = max(0, first_match_pos - 50)
    end = min(len(content), start + max_length)
    
    snippet = content[start:end]
    
    # Clean up snippet (don't start/end mid-word if possible)
    if start > 0 and not content[start].isspace():
        # Find next space
        space_pos = snippet.find(' ')
        if space_pos != -1:
            snippet = snippet[space_pos + 1:]
    
    if end < len(content):
        # Find last space
        space_pos = snippet.rfind(' ')
        if space_pos != -1:
            snippet = snippet[:space_pos]
    
    return snippet

def get_clause_database():
    """Get the complete clause database (same as in browse_clauses_section)"""
    # This is the same clause database structure as used in browse_clauses_section
    return {
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
        ],
        "Liability Limitations": [
            {
                "name": "Standard Liability Limits",
                "version": "1.8",
                "jurisdiction": ["International", "US", "EU"],
                "language": "English",
                "usage_count": 624,
                "rating": 4.4,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-07-05",
                "author": "Legal Risk Team",
                "content": """LIABILITY LIMITATIONS: The charter company's liability shall be limited as follows:
a) Total liability shall not exceed the total charter fee paid;
b) No liability for indirect, consequential, or punitive damages;
c) Liability for personal injury limited to insurance coverage amounts;
d) Guest activities undertaken at their own risk with proper acknowledgment;
e) Weather-related delays or cancellations subject to Force Majeure provisions.""",
                "variables": ["total_charter_fee", "insurance_coverage"],
                "applicable_to": ["All charter types", "High-risk activities"],
                "legal_notes": "Essential protection while maintaining reasonable guest coverage",
                "related_clauses": ["Force Majeure", "Guest Safety", "Insurance"],
                "risk_level": "Medium"
            }
        ],
        "Services": [
            {
                "name": "Standard Concierge Services",
                "version": "1.0",
                "jurisdiction": ["International"],
                "language": "English",
                "usage_count": 156,
                "rating": 4.5,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-08-04",
                "author": "Services Team",
                "content": """CONCIERGE SERVICES: The following concierge services are available upon request:
a) Provisioning coordination and grocery shopping services;
b) Restaurant reservations and dining recommendations;
c) Transportation arrangements to/from vessel;
d) Local activity planning and excursion booking;
e) Special event coordination for celebrations or business meetings;
f) Additional services may be available based on location and availability.""",
                "variables": ["location", "special_events", "dietary_requirements"],
                "applicable_to": ["Luxury charters", "Corporate events", "Special occasions"],
                "legal_notes": "Third-party service providers may apply separate terms",
                "related_clauses": ["Additional Fees", "Third-Party Services"],
                "risk_level": "Low"
            },
            {
                "name": "Professional Crew Services",
                "version": "1.0",
                "jurisdiction": ["International", "EU"],
                "language": "English",
                "usage_count": 89,
                "rating": 4.7,
                "status": "Active",
                "complexity": "Advanced",
                "last_updated": "2025-08-04",
                "author": "Crew Management Team",
                "content": """PROFESSIONAL CREW SERVICES: When crew services are included:
a) Certified captain with appropriate licensing for vessel and charter area;
b) Professional crew members as required by vessel size and charter type;
c) All crew wages, insurance, and travel expenses included in charter fee;
d) Crew quarters and meals provided separately from guest accommodations;
e) Crew gratuities are additional and at charterer's discretion;
f) Crew must comply with all safety protocols and maritime regulations.""",
                "variables": ["crew_size", "captain_license", "crew_qualifications"],
                "applicable_to": ["Crewed charters", "Luxury vessels", "Commercial operations"],
                "legal_notes": "Crew certification and insurance requirements vary by jurisdiction",
                "related_clauses": ["Safety Requirements", "Insurance Coverage", "Gratuities"],
                "risk_level": "Medium"
            },
            {
                "name": "Essential Maritime Operations",
                "version": "1.0",
                "jurisdiction": ["International", "Mediterranean"],
                "language": "English",
                "usage_count": 0,
                "rating": 4.8,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-08-04",
                "author": "Maritime Operations Team",
                "content": """ESSENTIAL MARITIME OPERATIONS: The following services are included within the base charter rate and represent the minimum service standards required for professional yacht operations:
a) Dedicated maritime operations center providing continuous monitoring and support services;
b) Real-time weather analysis and optimized routing recommendations based on current sea conditions and meteorological forecasts;
c) Shore support services encompassing all port coordination activities, including advance clearance procedures, berth reservations, customs documentation, and regulatory compliance management;
d) Technical support available on a 24-hour basis through qualified marine engineers providing remote diagnostics and troubleshooting assistance;
e) Strategic spare parts inventory at key Mediterranean locations, enabling parts delivery to major ports within 48 hours of request, subject to customs clearance procedures;
f) Preventive maintenance program following manufacturer specifications and industry best practices, with particular attention to engine performance monitoring and safety equipment certification requirements.""",
                "variables": ["operational_region", "support_response_time", "maintenance_schedule"],
                "applicable_to": ["Professional operations", "Mediterranean charters", "Extended voyages"],
                "legal_notes": "All maintenance activities documented in accordance with MCA guidelines",
                "related_clauses": ["Technical Support", "Port Services", "Maintenance Requirements"],
                "risk_level": "Low"
            },
            {
                "name": "Premium Hospitality Services",
                "version": "1.0",
                "jurisdiction": ["International", "Mediterranean"],
                "language": "English",
                "usage_count": 0,
                "rating": 4.7,
                "status": "Active",
                "complexity": "Premium",
                "last_updated": "2025-08-04",
                "author": "Hospitality Services Team",
                "content": """PREMIUM HOSPITALITY SERVICES: Enhanced hospitality services are available at a supplementary rate of €8,500 per charter day and include:
a) Executive chef position requiring Michelin-level training with demonstrated expertise in international cuisine and dietary accommodation capabilities, including kosher, halal, vegetarian, and allergen-free meal preparation;
b) Professional sommelier services including wine selection, cellar management, and pairing recommendations from an extensive collection of premium vintages curated to complement Mediterranean dining preferences;
c) Wellness and spa services coordinated through licensed practitioners including certified massage therapists, qualified yoga instructors, and personal fitness trainers (requiring 48-hour advance booking);
d) Event coordination capabilities extending to formal dinner parties, corporate functions, and celebration planning, including table setting according to international protocol standards, entertainment coordination, and specialized dietary arrangements for multi-course dining experiences.""",
                "variables": ["daily_rate", "advance_booking_period", "dietary_requirements", "event_type"],
                "applicable_to": ["Luxury charters", "Corporate events", "Special celebrations"],
                "legal_notes": "Supplementary services require advance booking and may have separate terms",
                "related_clauses": ["Additional Fees", "Advance Booking", "Dietary Requirements"],
                "risk_level": "Medium"
            },
            {
                "name": "Helicopter and Transportation Services",
                "version": "1.0",
                "jurisdiction": ["International", "Mediterranean"],
                "language": "English",
                "usage_count": 0,
                "rating": 4.6,
                "status": "Active",
                "complexity": "Premium",
                "last_updated": "2025-08-04",
                "author": "Transportation Services Team",
                "content": """HELICOPTER AND TRANSPORTATION SERVICES: Helicopter services are provided through established partnerships with certified operators:
a) Standard flight operations charged at €3,500 per flight hour with a minimum one-hour booking requirement;
b) For extended charter periods requiring helicopter standby availability, a daily retainer of €15,000 ensures dedicated aircraft and crew availability within a four-hour response window;
c) Ground transportation services include luxury vehicle coordination at destination ports, utilizing premium fleet vehicles such as Rolls-Royce, Bentley, and Mercedes S-Class models with professional chauffeur services (requiring 24-hour advance notice);
d) Private aviation coordination services assist with jet charter bookings, ground handling arrangements, and airport transfer logistics through established relationships with reputable charter operators;
e) Helicopter operations are subject to weather limitations, local aviation regulations, and landing platform certification requirements. Some ports may impose seasonal restrictions or require advance permits.""",
                "variables": ["flight_hourly_rate", "daily_retainer", "advance_notice_period", "operational_region"],
                "applicable_to": ["Ultra-luxury charters", "Corporate transport", "Emergency services"],
                "legal_notes": "Operations subject to aviation regulations and weather constraints",
                "related_clauses": ["Weather Limitations", "Advance Booking", "Third-Party Services"],
                "risk_level": "High"
            },
            {
                "name": "Bespoke Experience Services",
                "version": "1.0",
                "jurisdiction": ["International"],
                "language": "English",
                "usage_count": 0,
                "rating": 4.9,
                "status": "Active",
                "complexity": "Ultra-Premium",
                "last_updated": "2025-08-04",
                "author": "Luxury Experience Team",
                "content": """BESPOKE EXPERIENCE SERVICES: Ultra-premium services available on a project basis requiring detailed planning and advance coordination:
a) Celebrity chef experiences, ranging from €25,000 to €75,000 depending on chef reputation and menu complexity, including travel expenses, specialty ingredient procurement, and kitchen staff augmentation;
b) Live entertainment arrangements with internationally recognized performers, including classical musicians, opera singers, and contemporary artists, typically ranging from €50,000 to €250,000 per engagement based on artist availability, performance requirements, and exclusivity arrangements;
c) Cultural and educational experiences arranged through local expertise networks, providing access to private museum tours, archaeological site visits, and exclusive shopping experiences at premium retail establishments, priced individually based on complexity and exclusivity requirements;
d) All bespoke services require detailed planning discussions and written confirmation of arrangements. Cancellation policies may vary depending on contractual commitments with third-party providers.""",
                "variables": ["celebrity_chef_budget", "entertainment_budget", "cultural_experience_type", "planning_timeline"],
                "applicable_to": ["Ultra-luxury charters", "Celebrity clients", "Exclusive events"],
                "legal_notes": "Custom services require detailed planning and separate contractual commitments",
                "related_clauses": ["Advance Planning", "Third-Party Contracts", "Cancellation Policy"],
                "risk_level": "High"
            },
            {
                "name": "Service Standards and Performance Metrics",
                "version": "1.0",
                "jurisdiction": ["International"],
                "language": "English",
                "usage_count": 0,
                "rating": 4.8,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-08-04",
                "author": "Quality Assurance Team",
                "content": """SERVICE STANDARDS AND PERFORMANCE METRICS: The Lessor commits to specific response time standards for different service categories:
a) Emergency maritime situations receive immediate response within 15 minutes through the operations center, with technical support personnel available for remote assistance within 30 minutes of initial contact;
b) On-site technical support is dispatched within four hours where port access permits;
c) Concierge and hospitality requests are acknowledged within one hour of receipt, with standard fulfillment completed within 24 hours;
d) Complex arrangements requiring third-party coordination may require extended timeframes, which will be communicated upon request assessment;
e) Premium and bespoke services require advance booking periods ranging from 48 hours for specialized personnel to seven days for celebrity bookings and major entertainment arrangements;
f) These timeframes reflect the coordination requirements with external service providers and travel logistics.""",
                "variables": ["emergency_response_time", "standard_response_time", "advance_booking_requirements"],
                "applicable_to": ["All service categories", "Professional operations", "Quality assurance"],
                "legal_notes": "Response times are commitments subject to operational constraints",
                "related_clauses": ["Emergency Response", "Service Delivery", "Performance Guarantees"],
                "risk_level": "Medium"
            },
            {
                "name": "Service Guarantee and Remediation",
                "version": "1.0",
                "jurisdiction": ["International"],
                "language": "English",
                "usage_count": 0,
                "rating": 4.7,
                "status": "Active",
                "complexity": "Standard",
                "last_updated": "2025-08-04",
                "author": "Customer Service Team",
                "content": """SERVICE GUARANTEE AND REMEDIATION: Service quality and delivery guarantees:
a) In the event that confirmed services cannot be delivered due to Lessor default or operational failure, the Lessee shall receive service credit equal to 200% of the affected service fee;
b) Service credit may be applied to additional services during the current charter or credited against future charter agreements with the Lessor;
c) Service modifications and cancellations are accommodated subject to reasonable notice periods: standard premium services may be modified with 24-hour notice, specialized personnel services require 48-hour notice, and celebrity or major entertainment bookings require seven-day advance notice;
d) Cancellation fees may apply for third-party commitments already contracted;
e) The Lessor maintains liability insurance covering service delivery failures and will provide evidence of coverage upon request.""",
                "variables": ["service_credit_rate", "modification_notice_periods", "cancellation_fee_structure"],
                "applicable_to": ["Service delivery", "Quality guarantees", "Customer protection"],
                "legal_notes": "Service credits and guarantees subject to operational constraints and force majeure",
                "related_clauses": ["Service Credits", "Cancellation Policy", "Liability Insurance"],
                "risk_level": "Low"
            }
        ]
    }

def add_clause_to_contract(clause_result):
    """Add a search result clause to the contract"""
    # Initialize selected clauses in session state if not exists
    if 'selected_clauses' not in st.session_state:
        st.session_state.selected_clauses = []
    
    # Create a clause object for the contract
    selected_clause = {
        'name': clause_result['name'],
        'content': clause_result['content'],
        'category': clause_result['category'],
        'source': clause_result.get('source', 'search')
    }
    
    # Check if clause is already selected
    clause_exists = any(sc['name'] == clause_result['name'] for sc in st.session_state.selected_clauses)
    
    if not clause_exists:
        st.session_state.selected_clauses.append(selected_clause)
        return True
    return False

def clause_editor_section():
    st.subheader("✏️ Professional Clause Editor")
    
    # Check if we're in edit mode from a clicked Edit button
    if hasattr(st.session_state, 'edit_clause_mode') and st.session_state.edit_clause_mode:
        # Show prominent notification that we're in edit mode
        st.success(f"🎯 **EDIT MODE ACTIVE** - Ready to edit clause: **{st.session_state.edit_clause_data['name']}**")
        st.info("📝 The clause editor is now loaded with your selected clause. Make your changes below.")
    
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
    
    # Check if we're in edit mode from a clicked Edit button
    if hasattr(st.session_state, 'edit_clause_mode') and st.session_state.edit_clause_mode:
        # We're editing a specific clause
        clause_data = st.session_state.edit_clause_data
        
        st.info(f"🎯 **Editing Clause:** {clause_data['name']} (from {clause_data['category']})")
        
        # Add button to exit edit mode
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("❌ Cancel Edit"):
                st.session_state.edit_clause_mode = False
                st.session_state.edit_clause_data = {}
                st.rerun()
        with col2:
            if st.button("🆕 Create New Instead"):
                st.session_state.edit_clause_mode = False
                st.session_state.edit_clause_data = {}
        
        st.markdown("---")
        
        # Edit the existing clause
        edit_specific_clause(clause_data)
        
    else:
        # Normal editor mode selection
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

def edit_specific_clause(clause_data):
    """Edit a specific clause that was selected from the library"""
    st.markdown(f"### ✏️ Editing: **{clause_data['name']}**")
    st.caption(f"Category: {clause_data['category']} | Source: {clause_data['source']}")
    
    # Initialize or update session state for edited content
    # Check if we're editing a different clause than before
    current_clause_key = f"{clause_data['name']}_{clause_data['category']}_{clause_data['source']}"
    if 'current_editing_clause' not in st.session_state or st.session_state.current_editing_clause != current_clause_key:
        # We're editing a new/different clause, so reset the edited content
        st.session_state.edited_clause_content = clause_data['content']
        st.session_state.current_editing_clause = current_clause_key
    
    # Ensure edited_clause_content exists
    if 'edited_clause_content' not in st.session_state:
        st.session_state.edited_clause_content = clause_data['content']
    
    # Basic clause information
    col1, col2, col3 = st.columns(3)
    with col1:
        new_clause_name = st.text_input("Clause Name", value=clause_data['name'], key="edit_clause_name")
    with col2:
        new_category = st.selectbox(
            "Category",
            ["Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations", 
             "Force Majeure", "Dispute Resolution", "Delivery Terms", "Safety Requirements", 
             "Environmental Compliance", "Crew Provisions", "Guest Services", "Equipment Standards",
             "Weather Contingency", "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services", "Custom Clauses"],
            index=0 if clause_data['category'] not in ["Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations", 
                     "Force Majeure", "Dispute Resolution", "Delivery Terms", "Safety Requirements", 
                     "Environmental Compliance", "Crew Provisions", "Guest Services", "Equipment Standards",
                     "Weather Contingency", "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services", "Custom Clauses"] 
                  else ["Payment Terms", "Cancellation Policy", "Insurance Requirements", "Liability Limitations", 
                        "Force Majeure", "Dispute Resolution", "Delivery Terms", "Safety Requirements", 
                        "Environmental Compliance", "Crew Provisions", "Guest Services", "Equipment Standards",
                        "Weather Contingency", "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services", "Custom Clauses"].index(clause_data['category']),
            key="edit_clause_category"
        )
    with col3:
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=1, key="edit_clause_priority")
    
    # Clause content editor
    st.markdown("#### 📝 Edit Clause Content")
    
    new_content = st.text_area(
        "Clause Text",
        value=st.session_state.edited_clause_content,
        height=300,
        help="Make your edits to the clause content",
        key="edit_clause_text_area"
    )
    
    # Update session state when content changes
    if new_content != st.session_state.edited_clause_content:
        st.session_state.edited_clause_content = new_content
    
    # Show character count and word count
    char_count = len(new_content)
    word_count = len(new_content.split())
    st.caption(f"📊 {char_count} characters, {word_count} words")
    
    # Metadata fields
    st.markdown("#### 📋 Clause Metadata")
    col1, col2, col3 = st.columns(3)
    with col1:
        jurisdiction = st.multiselect(
            "Applicable Jurisdictions",
            ["International", "EU", "US", "UK", "Caribbean", "Mediterranean", "Australia"],
            default=["International"],
            key="edit_clause_jurisdiction"
        )
    with col2:
        language = st.selectbox("Language", ["English", "French", "Spanish", "Italian"], key="edit_clause_language")
    with col3:
        complexity = st.selectbox("Complexity", ["Simple", "Standard", "Advanced", "Expert"], index=1, key="edit_clause_complexity")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            import datetime
            
            if clause_data['source'] == 'custom':
                # Editing a user-created custom clause - update it directly
                updated_clause = {
                    'name': new_clause_name,
                    'content': new_content,
                    'category': new_category,
                    'priority': priority,
                    'jurisdiction': jurisdiction,
                    'language': language,
                    'complexity': complexity,
                    'last_updated': datetime.date.today().isoformat(),
                    'version': clause_data.get('version', '1.0'),
                    'status': 'Custom',
                    'rating': clause_data.get('rating', 4.0),
                    'usage_count': clause_data.get('usage_count', 0),
                    'author': 'User Created (Custom Clause)',
                    'applicable_to': clause_data.get('applicable_to', ['Custom']),
                    'legal_notes': f'Custom clause modified via Clause Editor. Priority: {priority}',
                    'related_clauses': clause_data.get('related_clauses', []),
                    'risk_level': clause_data.get('risk_level', 'Medium')
                }
                
                # Initialize custom clauses if needed
                if 'custom_clauses' not in st.session_state:
                    st.session_state.custom_clauses = []
                
                # Update existing custom clause by finding it in the list
                clause_found = False
                for i, custom_clause in enumerate(st.session_state.custom_clauses):
                    if (custom_clause.get('name') == clause_data['name'] and 
                        custom_clause.get('category') == clause_data['category']):
                        st.session_state.custom_clauses[i] = updated_clause
                        clause_found = True
                        break
                
                if not clause_found:
                    st.session_state.custom_clauses.append(updated_clause)
                
                st.success(f"✅ Updated custom clause: {new_clause_name}")
                
            elif clause_data['source'] == 'library':
                # Editing a library clause - create a new version
                if 'clause_versions' not in st.session_state:
                    st.session_state.clause_versions = {}
                
                # Create version key
                original_key = f"{clause_data['name']}_{clause_data['category']}"
                
                # Get current version number
                if original_key not in st.session_state.clause_versions:
                    st.session_state.clause_versions[original_key] = []
                
                version_number = f"v{len(st.session_state.clause_versions[original_key]) + 2}.0"  # Start from v2.0
                
                # Create versioned clause
                versioned_clause = {
                    'name': clause_data['name'],  # Keep original name
                    'original_name': clause_data['name'],
                    'content': new_content,
                    'category': clause_data['category'],
                    'priority': priority,
                    'jurisdiction': jurisdiction,
                    'language': language,
                    'complexity': complexity,
                    'last_updated': datetime.date.today().isoformat(),
                    'version': version_number,
                    'status': 'Modified',
                    'rating': clause_data.get('rating', 4.0),
                    'usage_count': clause_data.get('usage_count', 0),
                    'author': f"Modified by User ({clause_data.get('author', 'Unknown')})",
                    'applicable_to': clause_data.get('applicable_to', ['Modified']),
                    'legal_notes': f'Version {version_number} of library clause. Modified via Clause Editor. Priority: {priority}',
                    'related_clauses': clause_data.get('related_clauses', []),
                    'risk_level': clause_data.get('risk_level', 'Medium'),
                    'base_version': clause_data.get('version', '1.0'),
                    'modification_notes': f'Modified on {datetime.date.today().isoformat()}'
                }
                
                # Add to versions
                st.session_state.clause_versions[original_key].append(versioned_clause)
                
                st.success(f"✅ Created {version_number} of clause: {clause_data['name']}")
                st.info(f"💡 Original clause preserved. New version available in Browse Clauses.")
                
            else:
                st.error("❌ Unknown clause source. Cannot save changes.")
                return
            
            # Update the edit mode data to reflect the saved changes
            if clause_data['source'] == 'library':
                # For library clauses, update to point to the new version
                st.session_state.edit_clause_data.update({
                    'name': clause_data['name'],
                    'content': new_content,
                    'category': clause_data['category'],
                    'source': 'version',
                    'version': version_number
                })
            else:
                # For custom clauses, keep as custom
                st.session_state.edit_clause_data.update({
                    'name': new_clause_name,
                    'content': new_content,
                    'category': new_category,
                    'source': 'custom'
                })
            
            # Keep the edited content in session state for continued editing
            st.session_state.edited_clause_content = new_content
    
    with col2:
        if st.button("🔄 Reset to Original"):
            # Reset to the original clause content
            st.session_state.edited_clause_content = clause_data['content']
            st.info("🔄 Content reset to original")
            st.rerun()
    
    with col3:
        if st.button("📋 Save as New"):
            # Save as new custom clause without overwriting original with all required fields
            new_clause = {
                'name': f"{new_clause_name} (Copy)",
                'content': new_content,
                'category': new_category,
                'priority': priority,
                'jurisdiction': jurisdiction,
                'language': language,
                'complexity': complexity,
                'last_updated': datetime.date.today().isoformat(),
                'version': '1.0',
                'status': 'Custom',
                'rating': 4.0,  # Default rating for custom clauses
                'usage_count': 0,  # Start with 0 usage
                'author': 'User Created (Clause Editor)',
                'applicable_to': ['Custom'],
                'legal_notes': f'Custom clause created via Clause Editor. Priority: {priority}',
                'related_clauses': [],
                'risk_level': 'Medium'  # Default risk level
            }
            
            if 'custom_clauses' not in st.session_state:
                st.session_state.custom_clauses = []
            
            st.session_state.custom_clauses.append(new_clause)
            st.success(f"✅ Saved as new clause: {new_clause['name']}")
    
    with col4:
        if st.button("❌ Cancel"):
            st.session_state.edit_clause_mode = False
            st.session_state.edit_clause_data = {}
            st.session_state.edited_clause_content = ""
            st.rerun()

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
             "Force Majeure", "Dispute Resolution", "Safety Requirements", "Environmental Compliance",
             "Crew Provisions", "Guest Services", "Equipment Standards", "Weather Contingency", 
             "Port Clearance", "Maintenance Terms", "Fuel Policy", "Services"]
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
                    st.session_state.custom_clauses = []
                
                import datetime
                custom_clause = {
                    "name": clause_name,
                    "version": "1.0",
                    "category": clause_category,  # Add the category field
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
                
                # Add to custom clauses as a flat list
                st.session_state.custom_clauses.append(custom_clause)
                
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
    st.info("Edit existing clause functionality - implementation would load and modify clause content")

def clone_modify_editor():
    st.markdown("### 📋 Clone & Modify Clause")
    st.info("Clone and modify clause functionality - implementation would duplicate and allow editing")

def bulk_import_editor():
    st.markdown("### 📤 Bulk Import Clauses")
    st.info("Bulk import functionality - implementation would handle file uploads and batch processing")

def ai_suggestions_section():
    st.subheader("🤖 Clause Suggestions")
    
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
    
    if st.button("🤖 Get Auto Suggestions", type="primary"):
        st.markdown("### 🎯 Auto Recommendations")
        
        # Simulate AI analysis
        with st.spinner("Analyzing charter parameters..."):
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
                "category": "Insurance",
                "description": "Enhanced insurance requirements for high-value charter operations"
            },
            {
                "clause": "Corporate Payment Terms",
                "confidence": 88,
                "reason": "Corporate client detected - net terms may be appropriate",
                "priority": "Important", 
                "category": "Payment",
                "description": "Corporate payment terms with extended payment schedules"
            },
            {
                "clause": "Professional Crew Requirements",
                "confidence": 82,
                "reason": "Luxury charter requires certified professional crew",
                "priority": "Important",
                "category": "Safety",
                "description": "Professional crew certification and experience requirements"
            },
            {
                "clause": "Mediterranean Compliance Clause",
                "confidence": 76,
                "reason": "Operating in EU waters requires specific regulatory compliance",
                "priority": "Standard",
                "category": "Legal",
                "description": "Compliance requirements for Mediterranean charter operations"
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
                            'category': 'Suggestions',
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
        st.line_chart(usage_data)
        
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
        st.bar_chart(category_data)
    
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
        st.line_chart(seasonal_data)
        
        # Geographic patterns
        st.markdown("**Geographic Usage Distribution**")
        geo_data = {
            'Region': ['Mediterranean', 'Caribbean', 'Pacific', 'Atlantic', 'Indian Ocean'],
            'Usage': [456, 234, 123, 89, 45]
        }
        st.bar_chart(geo_data)
        
        # Client type patterns
        st.markdown("**Usage by Client Type**")
        client_data = {
            'Client Type': ['Corporate', 'Individual', 'Broker', 'Repeat Customer'],
            'Count': [234, 456, 123, 189]
        }
        st.bar_chart(client_data)

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
            st.checkbox("Enable Auto Suggestions", value=True)
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
    st.info("🚧 Contract version management functionality is under development.")
    
    # Placeholder version management content
    st.markdown("### Recent Contract Versions")
    version_data = {
        'Contract ID': ['C001', 'C002', 'C003'],
        'Version': ['1.0', '1.1', '2.0'],
        'Created': ['2025-07-20', '2025-07-22', '2025-07-25'],
        'Status': ['Active', 'Draft', 'Current']
    }
    
    import pandas as pd
    df_versions = pd.DataFrame(version_data)
    st.dataframe(df_versions, use_container_width=True)
    
    if st.button("Create New Version", key="create_version_btn"):
        st.success("New version creation would be implemented here")

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
