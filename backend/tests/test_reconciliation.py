import pytest
import pandas as pd
from decimal import Decimal
from io import StringIO
from app.services.reconciliation_engine import ReconciliationEngine
from app.services.discrepancy_detector import detect_duplicates, detect_orphan_refunds
from app.utils.money import parse_money, compare_amounts
from app.utils.validators import validate_transaction_csv, validate_settlement_csv
from tests.conftest import make_txn_df, make_stl_df


class TestReconciliation:
    """TC01-TC18: Comprehensive reconciliation test suite."""

    def test_tc01_exact_match(self, engine):
        """TC01: Exact successful transaction matching."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN001", "amount": "1000.00",
            "transaction_date": "2026-10-15", "description": "Test payment"
        }])
        stl_df = make_stl_df([{
            "settlement_id": "STL001", "transaction_ref": "TXN001",
            "amount": "1000.00", "settlement_date": "2026-10-16"
        }])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        matched = [r for r in result["results"] if r["status"] == "MATCHED"]
        assert len(matched) == 1
        assert matched[0]["transaction_id"] == "TXN001"

    def test_tc02_one_day_delay(self, engine):
        """TC02: Transaction settled one day later."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN002", "amount": "2000.00",
            "transaction_date": "2026-10-15", "description": "Test"
        }])
        stl_df = make_stl_df([{
            "settlement_id": "STL002", "transaction_ref": "TXN002",
            "amount": "2000.00", "settlement_date": "2026-10-16"
        }])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        matched = [r for r in result["results"] if r["status"] == "MATCHED"]
        assert len(matched) == 1

    def test_tc03_two_day_delay(self, engine):
        """TC03: Transaction settled two days later."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN003", "amount": "3000.00",
            "transaction_date": "2026-10-15", "description": "Test"
        }])
        stl_df = make_stl_df([{
            "settlement_id": "STL003", "transaction_ref": "TXN003",
            "amount": "3000.00", "settlement_date": "2026-10-17"
        }])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        matched = [r for r in result["results"] if r["status"] == "MATCHED"]
        assert len(matched) == 1

    def test_tc04_next_month_settlement(self, engine):
        """TC04: Transaction settled in the following month (Oct 31 -> Nov 1)."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN1001", "amount": "5000.00",
            "transaction_date": "2026-10-31", "description": "Month-end payment"
        }])
        stl_df = make_stl_df([{
            "settlement_id": "STL1001", "transaction_ref": "TXN1001",
            "amount": "5000.00", "settlement_date": "2026-11-01"
        }])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        timing = [r for r in result["results"] if r["status"] == "TIMING_DIFFERENCE"]
        assert len(timing) == 1
        assert timing[0]["transaction_id"] == "TXN1001"
        assert parse_money(timing[0]["variance"]) == Decimal("0")

    def test_tc05_individual_rounding(self, engine):
        """TC05: Individual rounding difference."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN005", "amount": "1000.005",
            "transaction_date": "2026-10-15", "description": "Test"
        }])
        stl_df = make_stl_df([{
            "settlement_id": "STL005", "transaction_ref": "TXN005",
            "amount": "1000.00", "settlement_date": "2026-10-17"
        }])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        rounding = [r for r in result["results"] if r["status"] == "ROUNDING_DIFFERENCE"]
        assert len(rounding) == 1
        assert parse_money(rounding[0]["variance"]) == Decimal("0.005")

    def test_tc06_aggregate_rounding(self, engine):
        """TC06: Aggregate rounding difference visible only after summation."""
        txn_df = make_txn_df([
            {"transaction_id": f"TXN00{i}", "amount": "1000.005",
             "transaction_date": "2026-10-15", "description": "Test"}
            for i in range(1, 6)
        ])
        stl_df = make_stl_df([
            {"settlement_id": f"STL00{i}", "transaction_ref": f"TXN00{i}",
             "amount": "1000.00", "settlement_date": "2026-10-17"}
            for i in range(1, 6)
        ])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        # Each has 0.005 rounding, aggregate = 0.025
        total_variance = sum(parse_money(r["variance"]) for r in result["results"])
        assert total_variance == Decimal("0.025")
        rounding = [r for r in result["results"] if r["status"] == "ROUNDING_DIFFERENCE"]
        assert len(rounding) == 5

    def test_tc07_duplicate_settlement(self, engine):
        """TC07: Duplicate settlement detection."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN1003", "amount": "2500.00",
            "transaction_date": "2026-10-10", "description": "Test"
        }])
        stl_df = make_stl_df([
            {"settlement_id": "STL1003A", "transaction_ref": "TXN1003",
             "amount": "2500.00", "settlement_date": "2026-10-12"},
            {"settlement_id": "STL1003B", "transaction_ref": "TXN1003",
             "amount": "2500.00", "settlement_date": "2026-10-12"}
        ])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        dupes = [r for r in result["results"] if r["status"] == "DUPLICATE"]
        assert len(dupes) == 1
        assert dupes[0]["settlement_id"] == "STL1003B"

    def test_tc08_orphan_refund(self, engine):
        """TC08: Orphan refund detection."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN001", "amount": "1000.00",
            "transaction_date": "2026-10-15", "description": "Test"
        }])
        stl_df = make_stl_df([
            {"settlement_id": "STL001", "transaction_ref": "TXN001",
             "amount": "1000.00", "settlement_date": "2026-10-16"},
            {"settlement_id": "REF1004", "transaction_ref": "TXN9999",
             "amount": "-750.00", "settlement_date": "2026-10-18"}
        ])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        orphans = [r for r in result["results"] if r["status"] == "ORPHAN_REFUND"]
        assert len(orphans) == 1
        assert orphans[0]["settlement_id"] == "REF1004"

    def test_tc09_missing_settlement(self, engine):
        """TC09: Missing bank settlement."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN041", "amount": "3000.00",
            "transaction_date": "2026-10-20", "description": "No settlement"
        }])
        stl_df = make_stl_df([{
            "settlement_id": "STL999", "transaction_ref": "TXN999",
            "amount": "500.00", "settlement_date": "2026-10-21"
        }])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        missing = [r for r in result["results"] if r["status"] == "MISSING_SETTLEMENT"]
        assert len(missing) == 1
        assert missing[0]["transaction_id"] == "TXN041"

    def test_tc10_unmatched_settlement(self, engine):
        """TC10: Unmatched bank settlement."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN001", "amount": "1000.00",
            "transaction_date": "2026-10-15", "description": "Test"
        }])
        stl_df = make_stl_df([
            {"settlement_id": "STL001", "transaction_ref": "TXN001",
             "amount": "1000.00", "settlement_date": "2026-10-16"},
            {"settlement_id": "STL9050", "transaction_ref": "TXN9050",
             "amount": "1200.00", "settlement_date": "2026-10-25"}
        ])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        unmatched = [r for r in result["results"] if r["status"] == "UNMATCHED_SETTLEMENT"]
        assert len(unmatched) == 1
        assert unmatched[0]["settlement_id"] == "STL9050"

    def test_tc11_invalid_csv(self):
        """TC11: Invalid CSV upload."""
        df = pd.DataFrame({"bad_col": ["data"]})
        is_valid, errors, _ = validate_transaction_csv(df)
        assert not is_valid
        assert any("Missing required columns" in e for e in errors)

    def test_tc12_missing_columns(self):
        """TC12: Missing required columns."""
        df = pd.DataFrame({"transaction_id": ["T1"], "amount": ["100"]})
        is_valid, errors, _ = validate_transaction_csv(df)
        assert not is_valid
        assert any("Missing required columns" in e for e in errors)

    def test_tc13_invalid_amount(self):
        """TC13: Invalid transaction amount."""
        df = pd.DataFrame({
            "transaction_id": ["T1"], "amount": ["not_a_number"],
            "transaction_date": ["2026-10-15"], "description": ["Test"]
        })
        is_valid, errors, _ = validate_transaction_csv(df)
        assert not is_valid
        assert any("Invalid amount" in e for e in errors)

    def test_tc14_duplicate_transaction_ids(self):
        """TC14: Duplicate transaction IDs."""
        df = pd.DataFrame({
            "transaction_id": ["T1", "T1"], "amount": ["100", "200"],
            "transaction_date": ["2026-10-15", "2026-10-16"],
            "description": ["Test1", "Test2"]
        })
        is_valid, errors, _ = validate_transaction_csv(df)
        assert not is_valid
        assert any("Duplicate" in e for e in errors)

    def test_tc15_month_end_reconciliation(self, engine):
        """TC15: Month-end reconciliation calculations."""
        txn_df = make_txn_df([
            {"transaction_id": "TXN001", "amount": "1000.00",
             "transaction_date": "2026-10-15", "description": "Test"},
            {"transaction_id": "TXN002", "amount": "2000.00",
             "transaction_date": "2026-10-31", "description": "Month-end"}
        ])
        stl_df = make_stl_df([
            {"settlement_id": "STL001", "transaction_ref": "TXN001",
             "amount": "1000.00", "settlement_date": "2026-10-17"},
            {"settlement_id": "STL002", "transaction_ref": "TXN002",
             "amount": "2000.00", "settlement_date": "2026-11-02"}
        ])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        assert result["summary"]["total_transactions"] == 2
        timing = [r for r in result["results"] if r["status"] == "TIMING_DIFFERENCE"]
        assert len(timing) == 1  # TXN002 settled next month

    def test_tc16_empty_datasets(self, engine):
        """TC16: Empty datasets."""
        txn_df = pd.DataFrame(columns=["transaction_id", "amount", "transaction_date", "description"])
        stl_df = pd.DataFrame(columns=["settlement_id", "transaction_ref", "amount", "settlement_date"])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        assert result["summary"]["total_transactions"] == 0
        assert result["summary"]["total_settlements"] == 0
        assert len(result["results"]) == 0

    def test_tc17_non_inr_currency_rejected(self):
        """TC17: Multiple currencies should be rejected."""
        df = pd.DataFrame({
            "transaction_id": ["T1"], "amount": ["100.00"],
            "transaction_date": ["2026-10-15"], "description": ["Test"],
            "currency": ["USD"]
        })
        is_valid, errors, _ = validate_transaction_csv(df)
        assert not is_valid
        assert any("Non-INR" in e for e in errors)

    def test_tc18_duplicate_not_counted_twice(self, engine):
        """TC18: Verify that a duplicate is not counted twice in totals."""
        txn_df = make_txn_df([{
            "transaction_id": "TXN1003", "amount": "2500.00",
            "transaction_date": "2026-10-10", "description": "Test"
        }])
        stl_df = make_stl_df([
            {"settlement_id": "STL1003A", "transaction_ref": "TXN1003",
             "amount": "2500.00", "settlement_date": "2026-10-12"},
            {"settlement_id": "STL1003B", "transaction_ref": "TXN1003",
             "amount": "2500.00", "settlement_date": "2026-10-12"}
        ])
        result = engine.run(txn_df, stl_df, month=10, year=2026)
        # Should have 1 MATCHED and 1 DUPLICATE, not 2 MATCHED
        matched = [r for r in result["results"] if r["status"] == "MATCHED"]
        dupes = [r for r in result["results"] if r["status"] == "DUPLICATE"]
        assert len(matched) == 1
        assert len(dupes) == 1
        # Matched amount should be 2500, not 5000
        assert parse_money(matched[0]["settlement_amount"]) == Decimal("2500.00")
