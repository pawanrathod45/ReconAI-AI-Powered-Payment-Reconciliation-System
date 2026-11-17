import pandas as pd
from decimal import Decimal
from datetime import date, timedelta
from ..utils.money import parse_money, compare_amounts, round_money
from .discrepancy_detector import detect_duplicates, detect_orphan_refunds, detect_timing_differences, detect_rounding_difference


class ReconciliationEngine:
    def __init__(self, tolerance="0.01"):
        self.tolerance = tolerance
        self.results = []
        self.summary = {}

    def run(self, transactions_df: pd.DataFrame, settlements_df: pd.DataFrame,
            month: int = None, year: int = None) -> dict:
        """Run full reconciliation. Returns results and summary."""
        self.results = []

        if month is None:
            month = date.today().month
        if year is None:
            year = date.today().year

        month_year = f"{year}-{month:02d}"

        # Normalize IDs
        txn_df = transactions_df.copy()
        stl_df = settlements_df.copy()
        txn_df["transaction_id"] = txn_df["transaction_id"].astype(str).str.strip().str.upper()
        stl_df["transaction_ref"] = stl_df["transaction_ref"].astype(str).str.strip().str.upper()
        stl_df["settlement_id"] = stl_df["settlement_id"].astype(str).str.strip().str.upper()

        # Step 1: Detect duplicates
        duplicates = detect_duplicates(stl_df)
        duplicate_stl_indices = set()
        if not duplicates.empty:
            dup_entries = duplicates[duplicates["is_duplicate"] == True]
            for _, dup in dup_entries.iterrows():
                self.results.append({
                    "transaction_id": dup["transaction_ref"],
                    "settlement_id": dup["settlement_id"],
                    "status": "DUPLICATE",
                    "transaction_amount": None,
                    "settlement_amount": str(dup["amount"]),
                    "variance": str(dup["amount"]),
                    "explanation": f"Duplicate settlement {dup['settlement_id']} for transaction {dup['transaction_ref']}. This entry should not be counted as additional revenue.",
                    "reconciliation_date": str(date.today()),
                    "month_year": month_year
                })
                duplicate_stl_indices.add(dup.name)  # DataFrame index

        # Step 2: Detect orphan refunds
        orphans = detect_orphan_refunds(txn_df, stl_df)
        orphan_stl_indices = set()
        if not orphans.empty:
            for _, orphan in orphans.iterrows():
                self.results.append({
                    "transaction_id": None,
                    "settlement_id": orphan["settlement_id"],
                    "status": "ORPHAN_REFUND",
                    "transaction_amount": None,
                    "settlement_amount": str(orphan["amount"]),
                    "variance": str(orphan["amount"]),
                    "explanation": f"Refund {orphan['settlement_id']} references transaction {orphan['transaction_ref']} which does not exist. Orphan refund of \u20b9{orphan['amount']}.",
                    "reconciliation_date": str(date.today()),
                    "month_year": month_year
                })
                orphan_stl_indices.add(orphan.name)

        # Remove duplicates and orphans from matching pool
        active_stl = stl_df.drop(index=duplicate_stl_indices | orphan_stl_indices, errors='ignore')

        matched_txn_ids = set()
        matched_stl_indices = set()

        # Step 3: Match by transaction reference
        for _, txn in txn_df.iterrows():
            txn_id = txn["transaction_id"]
            txn_amount = parse_money(txn["amount"])
            txn_date = pd.to_datetime(txn["transaction_date"]).date()

            # Find matching settlements
            matching_stls = active_stl[
                (active_stl["transaction_ref"] == txn_id) &
                (~active_stl.index.isin(matched_stl_indices))
            ]

            if matching_stls.empty:
                continue

            # Take the first match
            stl = matching_stls.iloc[0]
            stl_idx = matching_stls.index[0]
            stl_amount = parse_money(stl["amount"])
            stl_date = pd.to_datetime(stl["settlement_date"]).date()

            is_exact, is_within_tolerance, diff = compare_amounts(txn_amount, stl_amount, self.tolerance)

            # Determine status
            if is_exact:
                # Check timing
                if detect_timing_differences(txn_date, stl_date, month, year):
                    status = "TIMING_DIFFERENCE"
                    explanation = f"Transaction {txn_id} dated {txn_date} was settled on {stl_date} (next month). Amount \u20b9{txn_amount} is a timing difference, not a loss."
                else:
                    status = "MATCHED"
                    explanation = f"Transaction {txn_id} exactly matches settlement {stl['settlement_id']}. Amount: \u20b9{txn_amount}."
            elif is_within_tolerance:
                is_rounding, rdiff = detect_rounding_difference(txn_amount, stl_amount, self.tolerance)
                if is_rounding:
                    status = "ROUNDING_DIFFERENCE"
                    explanation = f"Transaction {txn_id} has rounding difference. Transaction: \u20b9{txn_amount}, Settlement: \u20b9{stl_amount}, Variance: \u20b9{rdiff}."
                else:
                    status = "MATCHED"
                    explanation = f"Transaction {txn_id} matches settlement {stl['settlement_id']} within tolerance."

                # Also check timing
                if detect_timing_differences(txn_date, stl_date, month, year):
                    status = "TIMING_DIFFERENCE"
                    explanation += f" Settlement crossed month boundary ({txn_date} -> {stl_date})."
            else:
                # Amount mismatch beyond tolerance but same ref - still link them
                status = "ROUNDING_DIFFERENCE" if abs(parse_money(diff)) < Decimal("1") else "MATCHED"
                explanation = f"Transaction {txn_id} matched to {stl['settlement_id']} by reference. Amount difference: \u20b9{diff}."

            self.results.append({
                "transaction_id": txn_id,
                "settlement_id": stl["settlement_id"],
                "status": status,
                "transaction_amount": str(txn_amount),
                "settlement_amount": str(stl_amount),
                "variance": diff,
                "explanation": explanation,
                "reconciliation_date": str(date.today()),
                "month_year": month_year
            })

            matched_txn_ids.add(txn_id)
            matched_stl_indices.add(stl_idx)

        # Step 4: Unmatched transactions (missing settlements)
        for _, txn in txn_df.iterrows():
            if txn["transaction_id"] not in matched_txn_ids:
                self.results.append({
                    "transaction_id": txn["transaction_id"],
                    "settlement_id": None,
                    "status": "MISSING_SETTLEMENT",
                    "transaction_amount": str(txn["amount"]),
                    "settlement_amount": None,
                    "variance": str(txn["amount"]),
                    "explanation": f"Transaction {txn['transaction_id']} has no matching bank settlement. Amount \u20b9{txn['amount']} is outstanding.",
                    "reconciliation_date": str(date.today()),
                    "month_year": month_year
                })

        # Step 5: Unmatched settlements
        for idx, stl in active_stl.iterrows():
            if idx not in matched_stl_indices:
                self.results.append({
                    "transaction_id": None,
                    "settlement_id": stl["settlement_id"],
                    "status": "UNMATCHED_SETTLEMENT",
                    "transaction_amount": None,
                    "settlement_amount": str(stl["amount"]),
                    "variance": str(parse_money(stl["amount"]) * -1),
                    "explanation": f"Bank settlement {stl['settlement_id']} (ref: {stl['transaction_ref']}) has no matching transaction. Amount: \u20b9{stl['amount']}.",
                    "reconciliation_date": str(date.today()),
                    "month_year": month_year
                })

        # Build summary
        self._build_summary(txn_df, stl_df, month_year)

        return {"results": self.results, "summary": self.summary}

    def _build_summary(self, txn_df, stl_df, month_year):
        total_txn_amount = sum(parse_money(a) for a in txn_df["amount"]) if not txn_df.empty else Decimal("0")
        total_stl_amount = sum(parse_money(a) for a in stl_df["amount"]) if not stl_df.empty else Decimal("0")

        status_counts = {}
        for r in self.results:
            s = r["status"]
            status_counts[s] = status_counts.get(s, 0) + 1

        matched = status_counts.get("MATCHED", 0)
        total_results = len(self.results)

        self.summary = {
            "total_transactions": len(txn_df),
            "total_settlements": len(stl_df),
            "total_transaction_amount": str(round_money(total_txn_amount)),
            "total_settlement_amount": str(round_money(total_stl_amount)),
            "matched_count": matched,
            "unmatched_count": status_counts.get("MISSING_SETTLEMENT", 0),
            "timing_differences": status_counts.get("TIMING_DIFFERENCE", 0),
            "rounding_differences": status_counts.get("ROUNDING_DIFFERENCE", 0),
            "duplicates": status_counts.get("DUPLICATE", 0),
            "orphan_refunds": status_counts.get("ORPHAN_REFUND", 0),
            "unmatched_settlements": status_counts.get("UNMATCHED_SETTLEMENT", 0),
            "total_variance": str(round_money(total_txn_amount - total_stl_amount)),
            "reconciliation_rate": round(matched / max(total_results, 1) * 100, 2)
        }
