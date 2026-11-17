from decimal import Decimal
from datetime import date
from ..utils.money import parse_money, compare_amounts
import pandas as pd


def detect_duplicates(settlements_df: pd.DataFrame) -> pd.DataFrame:
    """Find duplicate settlements by transaction_ref (same ref appearing more than once)."""
    if settlements_df.empty:
        return pd.DataFrame()
    # Group by transaction_ref, find refs with >1 settlement
    ref_counts = settlements_df.groupby("transaction_ref").size().reset_index(name="count")
    dup_refs = ref_counts[ref_counts["count"] > 1]["transaction_ref"].tolist()
    if not dup_refs:
        return pd.DataFrame()
    # Return all settlements for duplicate refs, mark first as ORIGINAL and rest as DUPLICATE
    dups = settlements_df[settlements_df["transaction_ref"].isin(dup_refs)].copy()
    dups["is_duplicate"] = dups.duplicated(subset=["transaction_ref"], keep="first")
    return dups


def detect_orphan_refunds(transactions_df: pd.DataFrame, settlements_df: pd.DataFrame) -> pd.DataFrame:
    """Find refunds (negative amounts or REF/REFUND prefixed IDs) referencing non-existent transactions."""
    if settlements_df.empty:
        return pd.DataFrame()

    # Identify refund records: settlement_id starts with REF or amount is negative
    refunds = settlements_df[
        settlements_df["settlement_id"].str.upper().str.startswith(("REF", "REFUND")) |
        (settlements_df["amount"].apply(lambda x: parse_money(x) < 0))
    ].copy()

    if refunds.empty or transactions_df.empty:
        return refunds

    # Check if the referenced transaction exists
    txn_ids = set(transactions_df["transaction_id"].str.strip().str.upper())
    orphans = refunds[~refunds["transaction_ref"].str.strip().str.upper().isin(txn_ids)]
    return orphans


def detect_timing_differences(transaction_date, settlement_date, month: int, year: int) -> bool:
    """Check if a settlement crosses month boundary."""
    if transaction_date is None or settlement_date is None:
        return False
    t_date = pd.to_datetime(transaction_date).date() if not isinstance(transaction_date, date) else transaction_date
    s_date = pd.to_datetime(settlement_date).date() if not isinstance(settlement_date, date) else settlement_date
    # Transaction is in the target month but settlement is in the next month
    return (t_date.month == month and t_date.year == year and
            (s_date.month != month or s_date.year != year))


def detect_rounding_difference(txn_amount, stl_amount, tolerance="0.01") -> tuple:
    """Check if difference is a rounding issue. Returns (is_rounding, difference)."""
    is_exact, is_within_tolerance, diff = compare_amounts(txn_amount, stl_amount, tolerance)
    if not is_exact and is_within_tolerance:
        return True, diff
    return False, diff
