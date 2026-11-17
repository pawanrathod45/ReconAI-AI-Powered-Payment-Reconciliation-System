from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO

from ..database import get_db
from ..models.models import Settlement
from ..schemas.schemas import SettlementSchema, UploadResponse
from ..utils.validators import validate_settlement_csv

router = APIRouter(prefix="/api", tags=["settlements"])


@router.post("/upload/settlements", response_model=UploadResponse)
async def upload_settlements(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload settlement CSV file."""
    try:
        contents = await file.read()
        decoded = contents.decode("utf-8")
        df = pd.read_csv(StringIO(decoded))

        is_valid, errors, cleaned_df = validate_settlement_csv(df)

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
                stl = Settlement(
                    settlement_id=str(row["settlement_id"]),
                    transaction_ref=str(row["transaction_ref"]),
                    amount=str(row["amount"]),
                    settlement_date=pd.to_datetime(row["settlement_date"]).date(),
                    bank_reference=str(row.get("bank_reference", "")) if "bank_reference" in row.index else "",
                    status=str(row.get("status", "SETTLED")) if "status" in row.index else "SETTLED"
                )
                db.add(stl)
                count += 1
            except Exception as e:
                row_errors.append(f"Row {idx + 1}: {str(e)}")

        db.commit()

        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {count} settlements",
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


@router.get("/settlements", response_model=list[SettlementSchema])
def get_settlements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all settlements with pagination."""
    settlements = db.query(Settlement).offset(skip).limit(limit).all()
    return settlements
