# Assumptions

This document details the assumptions made in the design and implementation of ReconAI. These assumptions scope the system's behaviour and define the boundaries of the reconciliation logic.

---

## 1. Currency is INR (₹)

All monetary values throughout the system are denominated in **Indian Rupees (INR)**. The system does not support multi-currency transactions or foreign exchange conversions. Currency symbols (`₹`) and commas in uploaded data are stripped during parsing, but all amounts are assumed to represent INR values.

**Impact**: No exchange rate lookups, no currency conversion logic, and all reports display amounts in ₹.

## 2. Each Transaction Has a Unique Transaction ID

Every transaction record is assumed to have a globally unique `transaction_id` (e.g., `TXN001`, `TXN002`). This ID serves as the **primary key** for matching transactions to their corresponding bank settlements.

**Impact**: The reconciliation engine relies on this uniqueness. If duplicate transaction IDs exist in the uploaded data, behaviour is undefined and results may be inaccurate.

## 3. Bank Settlements Contain Transaction References

Each bank settlement record includes a `transaction_ref` field that maps back to exactly one transaction's `transaction_id`. This reference is the **sole mechanism** for linking a settlement to its originating transaction.

**Impact**: If a settlement lacks a valid `transaction_ref`, it will be classified as an **Unmatched Bank Settlement**. The system does not perform fuzzy matching on amount, date, or description.

## 4. Settlement Takes 1–2 Calendar Days

Bank settlements are expected to occur **1 to 2 calendar days** after the original transaction date. The reconciliation engine uses this window when determining whether a settlement date is within the expected range.

**Impact**: Settlements arriving more than 2 days after the transaction are still matched (by reference), but those crossing a month boundary are flagged as **Timing Differences**.

## 5. Same Timezone for All Dates

All dates — transaction dates and settlement dates — are assumed to be in the **same timezone**. The system does not perform timezone conversions or UTC normalisation.

**Impact**: No timezone-aware date parsing is needed. Date comparisons (e.g., for month-end timing differences) operate directly on the stored date values.

## 6. Refunds Reference Original Transactions

Refund transactions follow a naming convention: the `transaction_ref` in the settlement data uses a `REF-` prefix followed by the original transaction ID (e.g., `REF-TXN005` references `TXN005`).

**Impact**: The reconciliation engine strips the `REF-` prefix to locate the original transaction. If the original transaction does not exist, the settlement is classified as an **Orphan Refund**.

## 7. Decimal Arithmetic for Money (Never Float)

All monetary calculations use Python's `decimal.Decimal` type, **never** `float`. Amounts are stored as strings in the database and parsed to `Decimal` for computation.

**Impact**: This eliminates floating-point precision errors (e.g., `0.1 + 0.2 ≠ 0.3` in IEEE 754). All comparisons, summations, and variance calculations are exact to the specified precision.

**Example**:
```python
# ❌ float — introduces rounding errors
>>> 0.1 + 0.2
0.30000000000000004

# ✅ Decimal — exact arithmetic
>>> Decimal("0.1") + Decimal("0.2")
Decimal('0.3')
```

## 8. Next-Month Settlement = Timing Difference

When a transaction is recorded near the **end of a month** and the corresponding settlement arrives in the **following month**, the system classifies this as a **Timing Difference** rather than a mismatch.

**Impact**: This prevents false-positive mismatches for transactions at month boundaries. For example, a transaction on 31 October that settles on 1 November is a timing difference, not a missing settlement.

## 9. Rounding Tolerance Is Configurable (Default ₹0.01)

The reconciliation engine applies a configurable **rounding tolerance** when comparing transaction and settlement amounts. The default tolerance is ₹0.01 (one paisa).

**Impact**: If `|transaction_amount - settlement_amount| ≤ 0.01`, the record is classified as a **Rounding Difference** rather than a mismatch. This accounts for minor rounding variations between the payment company's system and the bank's system.

**Example**:
- Transaction: ₹1,000.00 → Settlement: ₹999.99 → **Rounding Difference** (variance = ₹0.01)
- Transaction: ₹1,000.00 → Settlement: ₹999.50 → **Mismatch** (variance = ₹0.50 exceeds tolerance)

## 10. Duplicates Are Not Legitimate Additional Payments

If multiple settlement records reference the **same transaction ID**, they are flagged as **Duplicates**. The system does not treat them as legitimate additional payments or partial settlements.

**Impact**: Only the first settlement for a given transaction reference is matched. Subsequent settlements with the same reference are classified as duplicates and flagged for manual review.

## 11. Original Records Are Never Deleted

The reconciliation engine **never modifies or deletes** the original uploaded transaction and settlement records. Reconciliation results are stored in a separate table (`ReconciliationResult`), preserving the raw data for audit purposes.

**Impact**: Users can re-run reconciliation multiple times without losing original data. This supports auditability and allows results to be compared across different runs.

---

## Discrepancy Classification Reference

The reconciliation engine classifies every record into one of the following categories:

| Status | Description |
|--------|-------------|
| **Reconciled (MATCHED)** | Transaction and settlement match by reference with identical amounts (or amounts within rounding tolerance, with the same settlement month). |
| **Timing Difference** | Transaction and settlement match by reference and amount, but the settlement occurs in a different calendar month than the transaction. |
| **Rounding Difference** | Transaction and settlement match by reference, but the amounts differ by no more than the configured rounding tolerance (default ₹0.01). |
| **Duplicate** | Multiple settlements reference the same transaction ID. The first match is reconciled; subsequent entries are flagged as duplicates. |
| **Missing Settlement** | A transaction exists with no corresponding settlement record. The bank has not yet settled this transaction. |
| **Orphan Refund** | A settlement references a refund (`REF-` prefix) for a transaction that does not exist in the system. |
| **Unmatched Bank Settlement** | A settlement exists with a `transaction_ref` that does not correspond to any uploaded transaction (and is not a refund reference). |
