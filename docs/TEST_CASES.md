# Comprehensive Test Cases Suite (TC01 – TC18)

This document provides the full test specification and verification results for the ReconAI automated reconciliation test suite. All tests are implemented in `backend/tests/test_reconciliation.py` using `pytest`.

To execute the test suite:
```bash
cd backend
python -m pytest tests/ -v
```

---

## 1. Test Summary & Status Matrix

| Test ID | Test Description | Input Data Summary | Expected Result | Pass/Fail |
|---------|------------------|--------------------|-----------------|-----------|
| **TC01** | Exact successful transaction matching | `TXN001` (₹1000.00, Oct 15) vs `STL001` (₹1000.00, Oct 16) | Status: `MATCHED`, Variance: `₹0.00` | ✅ PASS |
| **TC02** | Transaction settled one day later | `TXN002` (₹2000.00, Oct 15) vs `STL002` (₹2000.00, Oct 16) | Status: `MATCHED` (T+1 valid settlement) | ✅ PASS |
| **TC03** | Transaction settled two days later | `TXN003` (₹3000.00, Oct 15) vs `STL003` (₹3000.00, Oct 17) | Status: `MATCHED` (T+2 valid settlement) | ✅ PASS |
| **TC04** | Transaction settled in following month | `TXN1001` (₹5000.00, Oct 31) vs `STL1001` (₹5000.00, Nov 01) | Status: `TIMING_DIFFERENCE`, Not a loss | ✅ PASS |
| **TC05** | Individual rounding difference | `TXN005` (₹1000.005) vs `STL005` (₹1000.00) | Status: `ROUNDING_DIFFERENCE`, Variance: `0.005` | ✅ PASS |
| **TC06** | Aggregate rounding difference | 5 txns with fractional `0.005` summed vs rounded settlements | Total aggregate variance = `0.025` Decimal | ✅ PASS |
| **TC07** | Duplicate settlement detection | `TXN1003` matched to two identical settlements `STL1003A` & `STL1003B` | `STL1003B` flagged as `DUPLICATE` exception | ✅ PASS |
| **TC08** | Orphan refund detection | `REF1004` (₹-750.00) referencing nonexistent `TXN9999` | Status: `ORPHAN_REFUND`, Unmapped parent | ✅ PASS |
| **TC09** | Missing bank settlement | `TXN041` (₹3000.00) with zero matching bank credits | Status: `MISSING_SETTLEMENT`, Outstanding | ✅ PASS |
| **TC10** | Unmatched bank settlement | `STL9050` (₹1200.00) with no matching ledger transaction | Status: `UNMATCHED_SETTLEMENT`, Unclaimed | ✅ PASS |
| **TC11** | Invalid CSV upload | CSV file missing mandatory headers or containing invalid schema | Upload rejected with descriptive errors | ✅ PASS |
| **TC12** | Missing required columns | CSV missing `transaction_id` or `amount` headers | Validation error: "Missing required columns" | ✅ PASS |
| **TC13** | Invalid transaction amount | Amount containing non-numeric strings (e.g., `not_a_number`) | Validation error: "Invalid amount" | ✅ PASS |
| **TC14** | Duplicate transaction IDs in input | CSV with duplicate `transaction_id` entries | Validation error: Duplicate transaction IDs rejected | ✅ PASS |
| **TC15** | Month-end reconciliation calculations | Two transactions (one intra-month, one cross-month) | `total_transactions: 2`, `TIMING_DIFFERENCE: 1` | ✅ PASS |
| **TC16** | Empty datasets | Empty DataFrame inputs | Handled gracefully: 0 records, empty results | ✅ PASS |
| **TC17** | Multiple currencies rejected | Upload containing non-INR transactions (e.g. `USD`) | Validation error: Only INR is supported | ✅ PASS |
| **TC18** | Verify duplicate not counted twice | Duplicate settlement present in bank statements | Legitimate revenue counted once, not inflated | ✅ PASS |

---

## 2. Detailed Test Specifications

### TC01: Exact Successful Transaction Matching
- **Objective**: Confirm standard matching when reference, date, and amount align perfectly.
- **Input**: `TXN001` (₹1,000.00, 2026-10-15) vs `STL001` (₹1,000.00, 2026-10-16).
- **Assertion**: Record status is `MATCHED`, variance is `0.00`.

### TC02: Transaction Settled One Day Later
- **Objective**: Verify standard T+1 batch settlement window.
- **Input**: `TXN002` (₹2,000.00, 2026-10-15) vs `STL002` (₹2,000.00, 2026-10-16).
- **Assertion**: Matched successfully without exception.

### TC03: Transaction Settled Two Days Later
- **Objective**: Verify standard T+2 batch settlement window.
- **Input**: `TXN003` (₹3,000.00, 2026-10-15) vs `STL003` (₹3,000.00, 2026-10-17).
- **Assertion**: Matched successfully within the 2-day grace window.

### TC04: Transaction Settled in Following Month (Mandatory Case 1)
- **Objective**: Verify next-month settlement is classified as a timing difference, not a loss.
- **Input**: `TXN1001` (₹5,000.00, 2026-10-31) vs `STL1001` (₹5,000.00, 2026-11-01).
- **Assertion**: Status is `TIMING_DIFFERENCE`, variance is `0`, audit explanation clarifies cross-period settlement.

### TC05: Individual Rounding Difference (Mandatory Case 2A)
- **Objective**: Verify detection of sub-paisa rounding variances using Python `Decimal`.
- **Input**: `TXN005` (₹1,000.005) vs `STL005` (₹1,000.00).
- **Assertion**: Status is `ROUNDING_DIFFERENCE`, variance is precisely `0.005`.

### TC06: Aggregate Rounding Difference (Mandatory Case 2B)
- **Objective**: Verify that multiple rounding differences aggregate into a measurable cumulative variance.
- **Input**: 5 transactions each with ₹1,000.005 settled at ₹1,000.00.
- **Assertion**: All 5 flagged as `ROUNDING_DIFFERENCE`, total cumulative variance equals `0.025`.

### TC07: Duplicate Settlement Detection (Mandatory Case 3)
- **Objective**: Ensure duplicate settlement records are detected and segregated.
- **Input**: `TXN1003` (₹2,500.00) with two bank settlements: `STL1003A` and `STL1003B`.
- **Assertion**: `STL1003A` matches legitimately, `STL1003B` is quarantined as `DUPLICATE`.

### TC08: Orphan Refund Detection (Mandatory Case 4)
- **Objective**: Detect refunds that lack an underlying original transaction.
- **Input**: `REF1004` (₹-750.00) referencing non-existent transaction `TXN9999`.
- **Assertion**: Flagged as `ORPHAN_REFUND` in exceptions view.

### TC09: Missing Bank Settlement
- **Objective**: Identify customer payments recorded in ledger with no corresponding bank credit.
- **Input**: `TXN041` (₹3,000.00) with no bank settlement.
- **Assertion**: Status is `MISSING_SETTLEMENT`, outstanding balance correctly computed.

### TC10: Unmatched Bank Settlement
- **Objective**: Identify mysterious bank deposits without an internal transaction reference.
- **Input**: `STL9050` (₹1,200.00) with non-existent transaction reference.
- **Assertion**: Status is `UNMATCHED_SETTLEMENT`.

### TC11 – TC14: Input & CSV Validation
- **Objective**: Enforce strict data sanitization on user uploads.
- **Coverage**: Missing headers, corrupt data types, non-numeric amounts, and duplicate primary keys.
- **Assertion**: Rejected with user-friendly error messages before ingestion.

### TC15 – TC18: Financial Integrity & Month-End Calculations
- **Objective**: Verify period boundary totals, empty state handling, currency enforcement, and revenue non-duplication.
- **Assertion**: Duplicates never inflate revenue; non-INR currencies are rejected; empty inputs yield safe zero states.
