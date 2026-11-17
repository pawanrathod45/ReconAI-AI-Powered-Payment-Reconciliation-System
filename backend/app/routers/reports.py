from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from io import StringIO

from ..database import get_db
from ..models.models import ReconciliationResult
from ..services.report_generator import generate_csv_report, generate_pdf_report
from ..utils.money import parse_money, round_money
from decimal import Decimal

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/export")
def export_report(
    format: str = Query("csv", regex="^(csv|pdf)$"),
    type: str = Query("full", regex="^(full|exceptions|monthly)$"),
    db: Session = Depends(get_db)
):
    """Export reconciliation report in CSV or PDF format."""
    results_db = db.query(ReconciliationResult).all()

    # Convert DB models to dicts
    results = []
    for r in results_db:
        results.append({
            "transaction_id": r.transaction_id,
            "settlement_id": r.settlement_id,
            "status": r.status,
            "transaction_amount": r.transaction_amount,
            "settlement_amount": r.settlement_amount,
            "variance": r.variance,
            "explanation": r.explanation,
            "reconciliation_date": str(r.reconciliation_date) if r.reconciliation_date else None,
            "month_year": r.month_year
        })

    if format == "pdf":
        # Build summary for PDF
        status_counts = {}
        total_txn = Decimal("0")
        total_stl = Decimal("0")
        for r in results:
            s = r["status"]
            status_counts[s] = status_counts.get(s, 0) + 1
            if r["transaction_amount"]:
                total_txn += parse_money(r["transaction_amount"])
            if r["settlement_amount"]:
                total_stl += parse_money(r["settlement_amount"])

        matched = status_counts.get("MATCHED", 0)
        total = len(results)

        summary = {
            "total_transactions": sum(1 for r in results if r["transaction_id"]),
            "total_settlements": sum(1 for r in results if r["settlement_id"]),
            "total_transaction_amount": str(round_money(total_txn)),
            "total_settlement_amount": str(round_money(total_stl)),
            "matched_count": matched,
            "unmatched_count": status_counts.get("MISSING_SETTLEMENT", 0),
            "timing_differences": status_counts.get("TIMING_DIFFERENCE", 0),
            "rounding_differences": status_counts.get("ROUNDING_DIFFERENCE", 0),
            "duplicates": status_counts.get("DUPLICATE", 0),
            "orphan_refunds": status_counts.get("ORPHAN_REFUND", 0),
            "unmatched_settlements": status_counts.get("UNMATCHED_SETTLEMENT", 0),
            "total_variance": str(round_money(total_txn - total_stl)),
            "reconciliation_rate": round(matched / max(total, 1) * 100, 2)
        }

        pdf_bytes = generate_pdf_report(results, summary)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=reconciliation_report.pdf"}
        )
    else:
        csv_content = generate_csv_report(results, report_type=type)
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=reconciliation_report.csv"}
        )
