from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO

from ..database import get_db
from ..models.models import Transaction
from ..schemas.schemas import TransactionSchema, UploadResponse
from ..utils.validators import validate_transaction_csv

router = APIRouter(prefix="/api", tags=["transactions"])


@router.post("/upload/transactions", response_model=UploadResponse)
async def upload_transactions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload transaction CSV file."""
    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        df = pd.read_csv(StringIO(decoded))

        is_valid, errors, cleaned_df = validate_transaction_csv(df)

        if not is_valid:
            return UploadResponse(
                success=False,
                message="Validation failed",
                count=0,
                errors=errors
            )

        count = 0
        row_errors = []
        for idx, row in cleaned_df.iterrows():
            try:
                txn = Transaction(
                    transaction_id=str(row["transaction_id"]),
                    amount=str(row["amount"]),
                    currency=str(row.get("currency", "INR")) if "currency" in row.index else "INR",
                    transaction_date=pd.to_datetime(row["transaction_date"]).date(),
                    description=str(row["description"]),
                    status=str(row.get("status", "COMPLETED")) if "status" in row.index else "COMPLETED"
                )
                db.add(txn)
                count += 1
            except Exception as e:
                row_errors.append(f"Row {idx + 1}: {str(e)}")

        db.commit()

        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {count} transactions",
            count=count,
            errors=row_errors
        )
    except Exception as e:
        db.rollback()
        return UploadResponse(
            success=False,
            message=f"Upload failed: {str(e)}",
            count=0,
            errors=[str(e)]
        )


@router.get("/transactions", response_model=list[TransactionSchema])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all transactions with pagination."""
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions
