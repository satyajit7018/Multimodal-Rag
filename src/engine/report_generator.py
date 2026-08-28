"""Automated PDF Engineering Design Report & Bill of Materials (BOM) Generator.
Produces branded, publication-ready PDF reports for multi-component circuits
containing BOM tables, compatibility verification checklists, and wiring schedules.
"""

from __future__ import annotations
import os
import datetime
from typing import List, Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from src.engine.circuit_validator import validate_circuit_compatibility, COMPONENT_REGISTRY
from src.engine.wiring_assistant import generate_wiring_plan

REPORT_OUTPUT_DIR = "data/reports"


def generate_engineering_pdf_report(
    project_name: str,
    host_mcu: str,
    peripherals: List[str],
    output_path: str = None,
) -> str:
    """Generates a complete PDF engineering design report for a hardware project."""
    os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
    if not output_path:
        clean_proj = project_name.lower().replace(" ", "_")
        output_path = os.path.join(REPORT_OUTPUT_DIR, f"{clean_proj}_design_report.pdf")

    all_components = [host_mcu] + [p for p in peripherals if p != host_mcu]
    validation = validate_circuit_compatibility(all_components)
    wiring = generate_wiring_plan(host_mcu, peripherals)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "ReportSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    story = []

    # Title & Header
    story.append(Paragraph(f"Hardware Design Report: {project_name}", title_style))
    story.append(Paragraph(f"Datasheet Engineering Intelligence Suite | Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=12))

    # Section 1: Bill of Materials (BOM)
    story.append(Paragraph("1. Bill of Materials (BOM)", h2_style))
    bom_headers = ["Item", "Part Name", "Type / Role", "Logic Voltage", "Max Current", "Bus Interface"]
    bom_rows = [bom_headers]

    for idx, comp in enumerate(all_components, start=1):
        meta = COMPONENT_REGISTRY.get(comp, {})
        bom_rows.append([
            str(idx),
            comp,
            meta.get("family", "N/A"),
            f"{meta.get('voltage', 'N/A')} V",
            f"{meta.get('current_ma', meta.get('max_gpio_current_ma', 'N/A'))} mA",
            meta.get("interface", "Direct GPIO"),
        ])

    bom_table = Table(bom_rows, colWidths=[35, 95, 130, 85, 85, 110])
    bom_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 0), (4, -1), "CENTER"),
    ]))
    story.append(bom_table)
    story.append(Spacer(1, 12))

    # Section 2: Circuit Compatibility & Electrical Clearance
    story.append(Paragraph("2. Circuit Compatibility & Electrical Clearance", h2_style))
    status_text = "✅ <b>PASSED: All electrical and bus interfaces are compatible.</b>" if validation["status"] == "pass" else "⚠️ <b>WARNING: Issues or special strapping required.</b>"
    story.append(Paragraph(status_text, body_style))
    story.append(Paragraph(f"• <b>Total Estimated Current Load:</b> {validation['total_estimated_current_ma']} mA", body_style))
    story.append(Paragraph(f"• <b>I2C Devices on Shared Bus:</b> {len(validation['i2c_bus_allocation'])} ({', '.join([f'{k}: {v}' for k, v in validation['i2c_bus_allocation'].items()]) if validation['i2c_bus_allocation'] else 'None'})", body_style))

    if validation["critical_errors"]:
        for err in validation["critical_errors"]:
            story.append(Paragraph(f"<font color='red'><b>CRITICAL ERROR — {err['type']}:</b> {err['details']}<br/><i>Recommendation: {err['recommendation']}</i></font>", body_style))

    if validation["compatibility_warnings"]:
        for w in validation["compatibility_warnings"]:
            story.append(Paragraph(f"<font color='#D97706'><b>WARNING — {w['type']}:</b> {w['details']}<br/><i>Action: {w['recommendation']}</i></font>", body_style))

    story.append(Spacer(1, 12))

    # Section 3: Grounded Pin-to-Pin Wiring Schedule
    story.append(Paragraph("3. Grounded Pin-to-Pin Wiring Schedule", h2_style))
    wire_headers = ["Source (Host)", "Source Pin", "Target (Module)", "Target Pin", "Signal Bus", "Wiring Guidance"]
    wire_rows = [wire_headers]

    for w in wiring.get("wiring_table", []):
        wire_rows.append([
            w["Source Component"],
            w["Source Pin"],
            w["Target Component"],
            w["Target Pin"],
            w["Signal Type"],
            w["Notes"],
        ])

    wire_table = Table(wire_rows, colWidths=[75, 80, 85, 95, 85, 120])
    wire_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.5),
    ]))
    story.append(wire_table)

    doc.build(story)
    return output_path
