import csv
import io
from datetime import date, datetime
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def generate_csv_report(results: list, report_type: str = "full") -> str:
    """Generate CSV report string from reconciliation results.
    
    Args:
        results: List of reconciliation result dicts.
        report_type: 'full' (all), 'exceptions' (non-MATCHED only), 'monthly' (with summary header).
    
    Returns:
        CSV string.
    """
    output = io.StringIO()
    
    if report_type == "exceptions":
        filtered = [r for r in results if r.get("status") != "MATCHED"]
    else:
        filtered = results
    
    if not filtered:
        return "No results to export.\n"
    
    fieldnames = [
        "transaction_id", "settlement_id", "status",
        "transaction_amount", "settlement_amount", "variance",
        "explanation", "reconciliation_date", "month_year"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    
    if report_type == "monthly":
        # Add summary header
        output.write("# ReconAI Monthly Reconciliation Report\n")
        output.write(f"# Generated: {datetime.now().isoformat()}\n")
        output.write(f"# Total Records: {len(filtered)}\n")
        output.write("\n")
    
    writer.writeheader()
    for row in filtered:
        writer.writerow(row)
    
    return output.getvalue()


def generate_pdf_report(results: list, summary: dict) -> bytes:
    """Generate PDF report from reconciliation results and summary.
    
    Args:
        results: List of reconciliation result dicts.
        summary: Reconciliation summary dict.
    
    Returns:
        PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("ReconAI Reconciliation Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Summary section
    elements.append(Paragraph("Summary", subtitle_style))
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Transactions", str(summary.get("total_transactions", 0))],
        ["Total Settlements", str(summary.get("total_settlements", 0))],
        ["Total Transaction Amount", summary.get("total_transaction_amount", "0")],
        ["Total Settlement Amount", summary.get("total_settlement_amount", "0")],
        ["Matched Count", str(summary.get("matched_count", 0))],
        ["Unmatched Count", str(summary.get("unmatched_count", 0))],
        ["Timing Differences", str(summary.get("timing_differences", 0))],
        ["Rounding Differences", str(summary.get("rounding_differences", 0))],
        ["Duplicates", str(summary.get("duplicates", 0))],
        ["Orphan Refunds", str(summary.get("orphan_refunds", 0))],
        ["Unmatched Settlements", str(summary.get("unmatched_settlements", 0))],
        ["Total Variance", summary.get("total_variance", "0")],
        ["Reconciliation Rate", f"{summary.get('reconciliation_rate', 0)}%"],
    ]
    
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 25))
    
    # Results section
    elements.append(Paragraph("Reconciliation Details", subtitle_style))
    
    if results:
        result_data = [["Txn ID", "Stl ID", "Status", "Txn Amount", "Stl Amount", "Variance", "Explanation"]]
        
        for r in results:
            # Truncate explanation for PDF readability
            explanation = str(r.get("explanation", ""))
            if len(explanation) > 60:
                explanation = explanation[:57] + "..."
            
            result_data.append([
                str(r.get("transaction_id", "") or ""),
                str(r.get("settlement_id", "") or ""),
                str(r.get("status", "")),
                str(r.get("transaction_amount", "") or ""),
                str(r.get("settlement_amount", "") or ""),
                str(r.get("variance", "") or ""),
                explanation
            ])
        
        col_widths = [70, 70, 90, 70, 70, 60, 250]
        result_table = Table(result_data, colWidths=col_widths, repeatRows=1)
        
        # Color-code status rows
        status_colors = {
            "MATCHED": colors.HexColor('#e8f5e9'),
            "TIMING_DIFFERENCE": colors.HexColor('#fff3e0'),
            "ROUNDING_DIFFERENCE": colors.HexColor('#fff9c4'),
            "DUPLICATE": colors.HexColor('#ffebee'),
            "MISSING_SETTLEMENT": colors.HexColor('#fce4ec'),
            "ORPHAN_REFUND": colors.HexColor('#f3e5f5'),
            "UNMATCHED_SETTLEMENT": colors.HexColor('#e8eaf6'),
        }
        
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]
        
        for i, r in enumerate(results, 1):
            status = r.get("status", "")
            bg = status_colors.get(status, colors.white)
            style_commands.append(('BACKGROUND', (0, i), (-1, i), bg))
        
        result_table.setStyle(TableStyle(style_commands))
        elements.append(result_table)
    else:
        elements.append(Paragraph("No reconciliation results available.", styles['Normal']))
    
    doc.build(elements)
    return buffer.getvalue()
