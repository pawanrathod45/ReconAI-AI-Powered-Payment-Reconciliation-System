from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    amount: str
    currency: str
    transaction_date: date
    description: str
    status: str


class SettlementSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    settlement_id: str
    transaction_ref: str
    amount: str
    settlement_date: date
    bank_reference: Optional[str] = None
    status: str


class ReconciliationResultSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: Optional[str] = None
    settlement_id: Optional[str] = None
    status: str
    transaction_amount: Optional[str] = None
    settlement_amount: Optional[str] = None
    variance: Optional[str] = None
    explanation: str
    reconciliation_date: Optional[date] = None
    month_year: Optional[str] = None


class ReconciliationSummary(BaseModel):
    total_transactions: int
    total_settlements: int
    total_transaction_amount: str
    total_settlement_amount: str
    matched_count: int
    unmatched_count: int
    timing_differences: int
    rounding_differences: int
    duplicates: int
    orphan_refunds: int
    unmatched_settlements: int
    total_variance: str
    reconciliation_rate: float


class UploadResponse(BaseModel):
    success: bool
    message: str
    count: int
    errors: list[str]


class MonthlyReconciliation(BaseModel):
    month: int
    year: int
    opening_balance: str
    total_transactions: str
    total_settlements: str
    next_month_settlements: str
    unresolved_differences: str
    reconciled_amount: str
    closing_status: str
    details: list[ReconciliationResultSchema]


class SampleDataResponse(BaseModel):
    success: bool
    transaction_count: int
    settlement_count: int
    message: str


class ExportRequest(BaseModel):
    format: str = "csv"
    report_type: str = "full"
