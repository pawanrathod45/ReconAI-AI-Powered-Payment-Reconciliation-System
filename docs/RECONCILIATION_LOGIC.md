# Reconciliation Logic

This document describes the reconciliation algorithm implemented in ReconAI's `ReconciliationEngine`, including the step-by-step matching process, priority order, rounding tolerance mechanism, and examples for every discrepancy type.

---

## Algorithm Overview

The reconciliation engine processes transactions and settlements in a **strict priority order** to ensure deterministic, correct classification. Each step runs fully before the next begins.

### Matching Priority Order

```
1. Data Normalization
2. Duplicate Detection (settlements)
3. Orphan Refund Detection
4. Exact Match by Reference + Amount
5. Rounding Tolerance Match
6. Timing Difference Detection
7. Missing Settlement Identification
8. Unmatched Settlement Identification
9. Summary Calculation
```

This ordering matters. Duplicates and orphan refunds are removed from the matching pool first, so they cannot interfere with legitimate matching in later steps.

---

## Step-by-Step Algorithm

### Step 1: Data Normalization

Before any matching, all IDs are normalized:

```python
transaction_id = transaction_id.strip().upper()
transaction_ref = transaction_ref.strip().upper()
settlement_id = settlement_id.strip().upper()
```

**Why**: Prevents mismatches caused by leading/trailing whitespace or inconsistent casing (e.g., `txn001` vs `TXN001`).

---

### Step 2: Duplicate Detection

The engine groups settlements by `transaction_ref` and counts occurrences. If multiple settlements reference the same transaction:

- The **first** settlement is kept for matching
- All **subsequent** settlements are flagged as `DUPLICATE`

```
Settlements:
  STL001 → transaction_ref: TXN001, amount: ₹1,000.00
  STL002 → transaction_ref: TXN001, amount: ₹1,000.00  ← DUPLICATE

Result:
  STL001 → proceeds to matching
  STL002 → classified as DUPLICATE
```

**Example**:

| Settlement ID | Transaction Ref | Amount     | Classification |
|---------------|----------------|------------|----------------|
| STL-001       | TXN001         | ₹5,000.00  | Proceeds to matching |
| STL-002       | TXN001         | ₹5,000.00  | **DUPLICATE** |

---

### Step 3: Orphan Refund Detection

Settlements whose `transaction_ref` starts with `REF-` are refund entries. The engine strips the prefix and checks whether the referenced original transaction exists:

```python
if transaction_ref.startswith("REF-"):
    original_id = transaction_ref[4:]  # Remove "REF-" prefix
    if original_id not in transaction_map:
        classify_as("ORPHAN_REFUND")
```

**Example**:

| Settlement ID | Transaction Ref | Original TXN Exists? | Classification |
|---------------|----------------|-----------------------|----------------|
| STL-010       | REF-TXN005     | Yes (TXN005 found)    | Proceeds to matching |
| STL-011       | REF-TXN999     | No (TXN999 not found) | **ORPHAN_REFUND** |

---

### Step 4: Exact Match by Reference + Amount

For each remaining settlement, the engine looks up the transaction by reference. If found and amounts are **exactly equal**:

```python
txn_amount = parse_money(transaction.amount)      # Decimal
stl_amount = parse_money(settlement.amount)        # Decimal

if txn_amount == stl_amount:
    classify_as("MATCHED")
```

The settlement and transaction are both removed from the unmatched pools.

**Example**:

| Transaction ID | Amount     | Settlement Ref | Settlement Amount | Classification |
|---------------|------------|----------------|-------------------|----------------|
| TXN001        | ₹1,000.00 | TXN001         | ₹1,000.00         | **MATCHED** |

---

### Step 5: Rounding Tolerance Match

If amounts are **not exactly equal**, the engine checks whether the difference falls within the configured rounding tolerance:

```python
ROUNDING_TOLERANCE = Decimal("0.01")  # Configurable

variance = abs(txn_amount - stl_amount)
if variance <= ROUNDING_TOLERANCE:
    classify_as("ROUNDING_DIFFERENCE")
```

**Why a tolerance?**: Banks and payment companies may apply slightly different rounding rules. A one-paisa difference (₹0.01) is commercially insignificant but would cause a false mismatch without tolerance.

**Example**:

| Transaction | Settlement | Variance | Within Tolerance? | Classification |
|-------------|------------|----------|-------------------|----------------|
| ₹1,000.00   | ₹999.99    | ₹0.01    | Yes (≤ 0.01)      | **ROUNDING_DIFFERENCE** |
| ₹1,000.00   | ₹999.50    | ₹0.50    | No (> 0.01)       | Proceeds to Step 6 |

---

### Step 6: Timing Difference Detection

If a transaction and settlement match by reference (and amount, with or without tolerance), but their dates fall in **different calendar months**, the record is classified as a timing difference:

```python
txn_month = transaction.transaction_date.month
stl_month = settlement.settlement_date.month

if txn_month != stl_month:
    classify_as("TIMING_DIFFERENCE")
```

**Example**:

| Transaction Date | Settlement Date | Same Month? | Classification |
|-----------------|-----------------|-------------|----------------|
| 2024-10-30      | 2024-10-31      | Yes         | MATCHED |
| 2024-10-31      | 2024-11-01      | No          | **TIMING_DIFFERENCE** |
| 2024-10-15      | 2024-10-17      | Yes         | MATCHED |

---

### Step 7: Missing Settlement Identification

After all matching steps, any **transactions** that remain unmatched — with no corresponding settlement found — are classified as missing settlements:

```python
for txn_id in unmatched_transactions:
    classify_as("MISSING_SETTLEMENT")
```

**Example**:

| Transaction ID | Amount     | Settlement Found? | Classification |
|---------------|------------|-------------------|----------------|
| TXN050        | ₹2,500.00 | No                | **MISSING_SETTLEMENT** |

---

### Step 8: Unmatched Settlement Identification

Any **settlements** that remain unmatched — with a `transaction_ref` that doesn't correspond to any uploaded transaction (and not a refund) — are classified as unmatched:

```python
for stl_id in unmatched_settlements:
    classify_as("UNMATCHED_SETTLEMENT")
```

**Example**:

| Settlement ID | Transaction Ref | Transaction Found? | Classification |
|---------------|----------------|--------------------|----------------|
| STL-099       | TXN999         | No                 | **UNMATCHED_SETTLEMENT** |

---

### Step 9: Summary Calculation

The engine calculates aggregate statistics across all classified records:

```python
summary = {
    "total_transactions": count(all_transactions),
    "total_settlements": count(all_settlements),
    "total_transaction_amount": sum(all_transaction_amounts),
    "total_settlement_amount": sum(all_settlement_amounts),
    "matched_count": count(MATCHED),
    "unmatched_count": count(MISSING_SETTLEMENT) + count(UNMATCHED_SETTLEMENT),
    "timing_differences": count(TIMING_DIFFERENCE),
    "rounding_differences": count(ROUNDING_DIFFERENCE),
    "duplicates": count(DUPLICATE),
    "orphan_refunds": count(ORPHAN_REFUND),
    "unmatched_settlements": count(UNMATCHED_SETTLEMENT),
    "total_variance": sum(all_variances),
    "reconciliation_rate": matched / total * 100
}
```

---

## Why Decimal Instead of Float?

IEEE 754 floating-point numbers **cannot represent all decimal fractions exactly**. This is catastrophic for financial calculations:

```python
# Float arithmetic — WRONG
>>> 0.1 + 0.2
0.30000000000000004

>>> 1000.00 - 999.99
0.010000000000047748  # Not 0.01!

# Decimal arithmetic — CORRECT
>>> Decimal("0.1") + Decimal("0.2")
Decimal('0.3')

>>> Decimal("1000.00") - Decimal("999.99")
Decimal('0.01')  # Exactly 0.01
```

In a reconciliation system, even a tiny floating-point error can cause:
- A matched transaction to be classified as a rounding difference
- A rounding difference to be classified as a mismatch
- Variance totals that don't add up

ReconAI stores all amounts as **strings** in the database and converts to `Decimal` using `parse_money()` at the point of calculation. This guarantees exact arithmetic throughout the reconciliation pipeline.

---

## Rounding Tolerance Mechanism

The rounding tolerance is defined in `backend/app/utils/money.py`:

```python
ROUNDING_TOLERANCE = Decimal("0.01")

def is_within_tolerance(amount1: Decimal, amount2: Decimal, tolerance: Decimal = ROUNDING_TOLERANCE) -> bool:
    return abs(amount1 - amount2) <= tolerance
```

### Configuring the Tolerance

The default tolerance of ₹0.01 (one paisa) can be adjusted by modifying the `ROUNDING_TOLERANCE` constant. Common configurations:

| Tolerance | Use Case |
|-----------|----------|
| `0.00`    | Require exact matches only (no rounding tolerance) |
| `0.01`    | Default — accounts for one-paisa rounding differences |
| `0.50`    | Lenient — for systems with known rounding to nearest 50 paise |
| `1.00`    | Very lenient — for systems that round to nearest rupee |

---

## Complete Discrepancy Type Reference

| Type | Condition | Example |
|------|-----------|---------|
| **MATCHED** | Reference matches, amounts equal, same month | TXN ₹1,000 → STL ₹1,000, both October |
| **TIMING_DIFFERENCE** | Reference + amount match, different months | TXN 31 Oct → STL 1 Nov |
| **ROUNDING_DIFFERENCE** | Reference matches, amount differs ≤ tolerance | TXN ₹1,000.00 → STL ₹999.99 |
| **DUPLICATE** | Multiple settlements reference same transaction | STL-A and STL-B both ref TXN001 |
| **MISSING_SETTLEMENT** | Transaction has no corresponding settlement | TXN050 exists, no STL with ref TXN050 |
| **ORPHAN_REFUND** | Refund settlement references non-existent transaction | STL ref REF-TXN999, TXN999 not found |
| **UNMATCHED_SETTLEMENT** | Settlement references non-existent transaction (not refund) | STL ref TXN999, TXN999 not found |
