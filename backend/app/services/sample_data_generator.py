import pandas as pd
import random
from datetime import date, timedelta


def generate_sample_data() -> dict:
    """Generate deterministic sample transaction and settlement data with all discrepancy types.
    
    Uses seed=42 for deterministic random parts.
    Returns dict with transactions_csv, settlements_csv strings and DataFrames.
    """
    random.seed(42)

    transactions = []
    settlements = []

    # --- Special cases ---

    # TXN1001: next-month settlement case
    transactions.append({
        "transaction_id": "TXN1001",
        "amount": "5000.00",
        "currency": "INR",
        "transaction_date": "2026-10-31",
        "description": "Payment for Order #1001",
        "status": "COMPLETED"
    })
    settlements.append({
        "settlement_id": "STL-1001",
        "transaction_ref": "TXN1001",
        "amount": "5000.00",
        "settlement_date": "2026-11-01",
        "bank_reference": "BANK-1001",
        "status": "SETTLED"
    })

    # TXN1002: rounding case (1000.005 -> 1000.00)
    transactions.append({
        "transaction_id": "TXN1002",
        "amount": "1000.005",
        "currency": "INR",
        "transaction_date": "2026-10-15",
        "description": "Payment for Order #1002",
        "status": "COMPLETED"
    })
    settlements.append({
        "settlement_id": "STL-1002",
        "transaction_ref": "TXN1002",
        "amount": "1000.00",
        "settlement_date": "2026-10-17",
        "bank_reference": "BANK-1002",
        "status": "SETTLED"
    })

    # TXN1003: duplicate settlement case
    transactions.append({
        "transaction_id": "TXN1003",
        "amount": "2500.00",
        "currency": "INR",
        "transaction_date": "2026-10-10",
        "description": "Payment for Order #1003",
        "status": "COMPLETED"
    })
    settlements.append({
        "settlement_id": "STL-1003A",
        "transaction_ref": "TXN1003",
        "amount": "2500.00",
        "settlement_date": "2026-10-12",
        "bank_reference": "BANK-1003A",
        "status": "SETTLED"
    })
    settlements.append({
        "settlement_id": "STL-1003B",
        "transaction_ref": "TXN1003",
        "amount": "2500.00",
        "settlement_date": "2026-10-12",
        "bank_reference": "BANK-1003B",
        "status": "SETTLED"
    })

    # TXN1004-TXN1008: aggregate rounding cases
    rounding_amounts = ["1500.005", "2200.003", "870.005", "3100.005", "1450.003"]
    for i, amt in enumerate(rounding_amounts, start=4):
        txn_id = f"TXN100{i}"
        txn_date = date(2026, 10, 10 + i)
        transactions.append({
            "transaction_id": txn_id,
            "amount": amt,
            "currency": "INR",
            "transaction_date": str(txn_date),
            "description": f"Payment for Order #100{i}",
            "status": "COMPLETED"
        })
        # Settlement rounds down (drops sub-cent)
        from decimal import Decimal, ROUND_DOWN
        rounded_amt = str(Decimal(amt).quantize(Decimal("0.01"), rounding=ROUND_DOWN))
        stl_date = txn_date + timedelta(days=1)
        settlements.append({
            "settlement_id": f"STL-100{i}",
            "transaction_ref": txn_id,
            "amount": rounded_amt,
            "settlement_date": str(stl_date),
            "bank_reference": f"BANK-100{i}",
            "status": "SETTLED"
        })

    # Orphan refund: REF1004 references TXN9999 which does NOT exist
    settlements.append({
        "settlement_id": "REF1004",
        "transaction_ref": "TXN9999",
        "amount": "-750.00",
        "settlement_date": "2026-10-18",
        "bank_reference": "BANK-REF1004",
        "status": "SETTLED"
    })

    # TXN1010-TXN1040: Normal transactions (31 records)
    base_amounts = [
        500, 750, 1200, 1500, 2000, 2500, 3000, 3500, 4000, 4500,
        5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500,
        10000, 10500, 11000, 11500, 12000, 12500, 13000, 13500, 14000, 14500,
        15000
    ]
    random.shuffle(base_amounts)

    for i, base_amt in enumerate(range(10, 41)):
        txn_id = f"TXN10{base_amt:02d}" if base_amt < 100 else f"TXN1{base_amt}"
        txn_id = f"TXN10{base_amt}"
        amt_val = base_amounts[i] + random.randint(0, 99) / 100
        # Use Decimal string to avoid float
        from decimal import Decimal
        amt_str = str(Decimal(str(amt_val)).quantize(Decimal("0.01")))
        day = random.randint(1, 28)
        txn_date = date(2026, 10, day)
        transactions.append({
            "transaction_id": txn_id,
            "amount": amt_str,
            "currency": "INR",
            "transaction_date": str(txn_date),
            "description": f"Payment for Order #{base_amt}",
            "status": "COMPLETED"
        })
        # Settlement 1-2 days after
        delay = random.choice([1, 2])
        stl_date = txn_date + timedelta(days=delay)
        settlements.append({
            "settlement_id": f"STL-10{base_amt}",
            "transaction_ref": txn_id,
            "amount": amt_str,
            "settlement_date": str(stl_date),
            "bank_reference": f"BANK-10{base_amt}",
            "status": "SETTLED"
        })

    # TXN1041: missing settlement case
    transactions.append({
        "transaction_id": "TXN1041",
        "amount": "3000.00",
        "currency": "INR",
        "transaction_date": "2026-10-20",
        "description": "Payment for Order #1041 - No settlement",
        "status": "COMPLETED"
    })
    # NO settlement for TXN1041

    # STL-9050: unmatched settlement (no matching transaction)
    settlements.append({
        "settlement_id": "STL-9050",
        "transaction_ref": "TXN9050",
        "amount": "1200.00",
        "settlement_date": "2026-10-25",
        "bank_reference": "BANK-9050",
        "status": "SETTLED"
    })

    # Build DataFrames
    txn_df = pd.DataFrame(transactions)
    stl_df = pd.DataFrame(settlements)

    # Build CSV strings
    transactions_csv = txn_df.to_csv(index=False)
    settlements_csv = stl_df.to_csv(index=False)

    return {
        "transactions_csv": transactions_csv,
        "settlements_csv": settlements_csv,
        "transactions_df": txn_df,
        "settlements_df": stl_df
    }
