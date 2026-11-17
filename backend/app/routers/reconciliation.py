from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
import pandas as pd
from datetime import date
from decimal import Decimal

from ..database import get_db
from ..models.models import Transaction, Settlement, ReconciliationResult
from ..schemas.schemas import ReconciliationResultSchema, ReconciliationSummary, MonthlyReconciliation
from ..services.reconciliation_engine import ReconciliationEngine
from ..utils.money import parse_money, round_money

router = APIRouter(prefix="/api/reconciliation", tags=["reconciliation"])


@router.post("/run")
def run_reconciliation(
    month: int = Query(None, ge=1, le=12),
    year: int = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    """Run reconciliation on all transactions and settlements in DB."""
    # Fetch all data
    transactions = db.query(Transaction).all()
    settlements = db.query(Settlement).all()

    # Build DataFrames
    txn_data = [{
        "transaction_id": t.transaction_id,
        "amount": t.amount,
        "currency": t.currency,
        "transaction_date": str(t.transaction_date),
        "description": t.description,
        "status": t.status
    } for t in transactions]

    stl_data = [{
        "settlement_id": s.settlement_id,
        "transaction_ref": s.transaction_ref,
        "amount": s.amount,
        "settlement_date": str(s.settlement_date),
        "bank_reference": s.bank_reference,
        "status": s.status
    } for s in settlements]

    txn_df = pd.DataFrame(txn_data) if txn_data else pd.DataFrame(
        columns=["transaction_id", "amount", "currency", "transaction_date", "description", "status"]
    )
    stl_df = pd.DataFrame(stl_data) if stl_data else pd.DataFrame(
        columns=["settlement_id", "transaction_ref", "amount", "settlement_date", "bank_reference", "status"]
    )

    # Run engine
    engine = ReconciliationEngine()
    result = engine.run(txn_df, stl_df, month=month, year=year)

    # Clear old results and store new ones
    db.query(ReconciliationResult).delete()
    for r in result["results"]:
        rec_date = r.get("reconciliation_date")
        if isinstance(rec_date, str):
            rec_date = date.fromisoformat(rec_date)
        elif rec_date is None:
            rec_date = date.today()

        db_result = ReconciliationResult(
            transaction_id=r.get("transaction_id"),
            settlement_id=r.get("settlement_id"),
            status=r["status"],
            transaction_amount=r.get("transaction_amount"),
            settlement_amount=r.get("settlement_amount"),
            variance=r.get("variance"),
            explanation=r["explanation"],
            reconciliation_date=rec_date,
            month_year=r.get("month_year", "")
        )
        db.add(db_result)

    db.commit()

    return result["summary"]


@router.get("/summary", response_model=ReconciliationSummary)
def get_summary(db: Session = Depends(get_db)):
    """Get reconciliation summary from stored results."""
    results = db.query(ReconciliationResult).all()

    if not results:
        return ReconciliationSummary(
            total_transactions=0, total_settlements=0,
            total_transaction_amount="0", total_settlement_amount="0",
            matched_count=0, unmatched_count=0,
            timing_differences=0, rounding_differences=0,
            duplicates=0, orphan_refunds=0, unmatched_settlements=0,
            total_variance="0", reconciliation_rate=0.0
        )

    status_counts = {}
    total_txn = Decimal("0")
    total_stl = Decimal("0")
    for r in results:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1
        if r.transaction_amount:
            total_txn += parse_money(r.transaction_amount)
        if r.settlement_amount:
            total_stl += parse_money(r.settlement_amount)

    matched = status_counts.get("MATCHED", 0)
    total = len(results)

    return ReconciliationSummary(
        total_transactions=sum(1 for r in results if r.transaction_id),
        total_settlements=sum(1 for r in results if r.settlement_id),
        total_transaction_amount=str(round_money(total_txn)),
        total_settlement_amount=str(round_money(total_stl)),
        matched_count=matched,
        unmatched_count=status_counts.get("MISSING_SETTLEMENT", 0),
        timing_differences=status_counts.get("TIMING_DIFFERENCE", 0),
        rounding_differences=status_counts.get("ROUNDING_DIFFERENCE", 0),
        duplicates=status_counts.get("DUPLICATE", 0),
        orphan_refunds=status_counts.get("ORPHAN_REFUND", 0),
        unmatched_settlements=status_counts.get("UNMATCHED_SETTLEMENT", 0),
        total_variance=str(round_money(total_txn - total_stl)),
        reconciliation_rate=round(matched / max(total, 1) * 100, 2)
    )


@router.get("/results", response_model=list[ReconciliationResultSchema])
def get_results(
    status: str = Query(None),
    search: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
    db: Session = Depends(get_db)
):
    """Get all reconciliation results with optional filters."""
    query = db.query(ReconciliationResult)

    if status:
        query = query.filter(ReconciliationResult.status == status)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ReconciliationResult.transaction_id.ilike(search_term),
                ReconciliationResult.settlement_id.ilike(search_term),
                ReconciliationResult.explanation.ilike(search_term),
            )
        )

    # Sorting
    sort_column = getattr(ReconciliationResult, sort_by, ReconciliationResult.id)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    results = query.offset(skip).limit(limit).all()
    return results


@router.get("/exceptions", response_model=list[ReconciliationResultSchema])
def get_exceptions(db: Session = Depends(get_db)):
    """Get non-matched reconciliation results (exceptions only)."""
    results = db.query(ReconciliationResult).filter(
        ReconciliationResult.status != "MATCHED"
    ).all()
    return results


@router.get("/monthly", response_model=MonthlyReconciliation)
def get_monthly(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db)
):
    """Get monthly reconciliation report."""
    month_year = f"{year}-{month:02d}"

    results = db.query(ReconciliationResult).filter(
        ReconciliationResult.month_year == month_year
    ).all()

    # Calculate totals
    total_txn = Decimal("0")
    total_stl = Decimal("0")
    next_month_stl = Decimal("0")
    unresolved = Decimal("0")

    for r in results:
        if r.transaction_amount:
            total_txn += parse_money(r.transaction_amount)
        if r.settlement_amount:
            total_stl += parse_money(r.settlement_amount)
        if r.status == "TIMING_DIFFERENCE" and r.settlement_amount:
            next_month_stl += parse_money(r.settlement_amount)
        if r.status in ("MISSING_SETTLEMENT", "UNMATCHED_SETTLEMENT", "ORPHAN_REFUND"):
            if r.variance:
                unresolved += abs(parse_money(r.variance))

    reconciled = total_txn - unresolved
    closing = "RECONCILED" if unresolved == Decimal("0") else "PENDING_REVIEW"

    details = [ReconciliationResultSchema.model_validate(r) for r in results]

    return MonthlyReconciliation(
        month=month,
        year=year,
        opening_balance="0.00",
        total_transactions=str(round_money(total_txn)),
        total_settlements=str(round_money(total_stl)),
        next_month_settlements=str(round_money(next_month_stl)),
        unresolved_differences=str(round_money(unresolved)),
        reconciled_amount=str(round_money(reconciled)),
        closing_status=closing,
        details=details
    )
