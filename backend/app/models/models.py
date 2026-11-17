from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime, date
from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    amount = Column(String, nullable=False)  # Stored as string to preserve Decimal precision
    currency = Column(String, default="INR")
    transaction_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    settlement_id = Column(String, unique=True, index=True, nullable=False)
    transaction_ref = Column(String, index=True, nullable=False)
    amount = Column(String, nullable=False)
    settlement_date = Column(Date, nullable=False)
    bank_reference = Column(String, nullable=True)
    status = Column(String, default="SETTLED")
    created_at = Column(DateTime, default=datetime.utcnow)


class ReconciliationResult(Base):
    __tablename__ = "reconciliation_results"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=True)
    settlement_id = Column(String, nullable=True)
    status = Column(String, nullable=False)  # MATCHED, TIMING_DIFFERENCE, ROUNDING_DIFFERENCE, DUPLICATE, MISSING_SETTLEMENT, ORPHAN_REFUND, UNMATCHED_SETTLEMENT
    transaction_amount = Column(String, nullable=True)
    settlement_amount = Column(String, nullable=True)
    variance = Column(String, nullable=True)
    explanation = Column(String, nullable=False)
    reconciliation_date = Column(Date, nullable=False)
    month_year = Column(String, nullable=False)  # Format: "YYYY-MM"
