from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from .database import engine, Base, get_db, SessionLocal
from .routers import transactions, settlements, reconciliation, reports
from .services.sample_data_generator import generate_sample_data
from .models.models import Transaction, Settlement
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
from datetime import date

app = FastAPI(
    title="ReconAI API",
    description="AI-Powered Payment Reconciliation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(transactions.router)
app.include_router(settlements.router)
app.include_router(reconciliation.router)
app.include_router(reports.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "ReconAI", "version": "1.0.0"}


@app.post("/api/sample-data/generate")
def generate_sample():
    """Generate sample transaction and settlement data."""
    data = generate_sample_data()

    # Store in database
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Transaction).delete()
        db.query(Settlement).delete()

        # Parse and store transactions
        txn_df = pd.read_csv(StringIO(data["transactions_csv"]))
        for _, row in txn_df.iterrows():
            txn = Transaction(
                transaction_id=str(row["transaction_id"]),
                amount=str(row["amount"]),
                currency=str(row.get("currency", "INR")),
                transaction_date=pd.to_datetime(row["transaction_date"]).date(),
                description=str(row["description"]),
                status=str(row.get("status", "COMPLETED"))
            )
            db.add(txn)

        # Parse and store settlements
        stl_df = pd.read_csv(StringIO(data["settlements_csv"]))
        for _, row in stl_df.iterrows():
            stl = Settlement(
                settlement_id=str(row["settlement_id"]),
                transaction_ref=str(row["transaction_ref"]),
                amount=str(row["amount"]),
                settlement_date=pd.to_datetime(row["settlement_date"]).date(),
                bank_reference=str(row.get("bank_reference", "")),
                status=str(row.get("status", "SETTLED"))
            )
            db.add(stl)

        db.commit()

        return {
            "success": True,
            "transaction_count": len(txn_df),
            "settlement_count": len(stl_df),
            "message": "Sample data generated successfully with all discrepancy types",
            "transactions_csv": data["transactions_csv"],
            "settlements_csv": data["settlements_csv"]
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


@app.get("/api/sample-data/download/transactions")
def download_sample_transactions():
    data = generate_sample_data()
    return StreamingResponse(
        iter([data["transactions_csv"]]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sample_transactions.csv"}
    )


@app.get("/api/sample-data/download/settlements")
def download_sample_settlements():
    data = generate_sample_data()
    return StreamingResponse(
        iter([data["settlements_csv"]]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sample_settlements.csv"}
    )
