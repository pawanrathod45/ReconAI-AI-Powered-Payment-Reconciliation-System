import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime

REQUIRED_TRANSACTION_COLUMNS = ["transaction_id", "amount", "transaction_date", "description"]
REQUIRED_SETTLEMENT_COLUMNS = ["settlement_id", "transaction_ref", "amount", "settlement_date"]


def validate_transaction_csv(df: pd.DataFrame) -> tuple:
    """Validate transaction CSV. Returns (is_valid, errors, cleaned_df)."""
    errors = []

    # Check required columns
    missing_cols = [c for c in REQUIRED_TRANSACTION_COLUMNS if c not in df.columns]
    if missing_cols:
        return False, [f"Missing required columns: {', '.join(missing_cols)}"], df

    # Check empty dataframe
    if df.empty:
        return False, ["CSV file contains no data rows"], df

    # Validate transaction_id uniqueness
    dupes = df[df.duplicated(subset=["transaction_id"], keep=False)]
    if not dupes.empty:
        dupe_ids = dupes["transaction_id"].unique().tolist()
        errors.append(f"Duplicate transaction IDs found: {', '.join(str(x) for x in dupe_ids)}")

    # Validate amounts
    for idx, row in df.iterrows():
        try:
            val = str(row["amount"]).replace("₹", "").replace(",", "").strip()
            Decimal(val)
        except (InvalidOperation, ValueError):
            errors.append(f"Row {idx+1}: Invalid amount '{row['amount']}'")

    # Validate dates
    for idx, row in df.iterrows():
        try:
            pd.to_datetime(row["transaction_date"])
        except Exception:
            errors.append(f"Row {idx+1}: Invalid date '{row['transaction_date']}'")

    # Check currency if column exists
    if "currency" in df.columns:
        non_inr = df[df["currency"].str.upper() != "INR"]
        if not non_inr.empty:
            errors.append(f"Non-INR currencies found. Only INR is supported. Rows: {non_inr.index.tolist()}")

    # Validate no missing required values
    for col in REQUIRED_TRANSACTION_COLUMNS:
        nulls = df[df[col].isna()]
        if not nulls.empty:
            errors.append(f"Missing values in '{col}' at rows: {(nulls.index + 1).tolist()}")

    return len(errors) == 0, errors, df


def validate_settlement_csv(df: pd.DataFrame) -> tuple:
    """Validate settlement CSV. Returns (is_valid, errors, cleaned_df)."""
    errors = []

    missing_cols = [c for c in REQUIRED_SETTLEMENT_COLUMNS if c not in df.columns]
    if missing_cols:
        return False, [f"Missing required columns: {', '.join(missing_cols)}"], df

    if df.empty:
        return False, ["CSV file contains no data rows"], df

    # Validate amounts
    for idx, row in df.iterrows():
        try:
            val = str(row["amount"]).replace("₹", "").replace(",", "").strip()
            Decimal(val)
        except (InvalidOperation, ValueError):
            errors.append(f"Row {idx+1}: Invalid amount '{row['amount']}'")

    # Validate dates
    for idx, row in df.iterrows():
        try:
            pd.to_datetime(row["settlement_date"])
        except Exception:
            errors.append(f"Row {idx+1}: Invalid date '{row['settlement_date']}'")

    for col in REQUIRED_SETTLEMENT_COLUMNS:
        nulls = df[df[col].isna()]
        if not nulls.empty:
            errors.append(f"Missing values in '{col}' at rows: {(nulls.index + 1).tolist()}")

    return len(errors) == 0, errors, df
