from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from .database import engine, Base, get_db, SessionLocal
from .routers import transactions, settlements, reconciliation, reports
from .services.sample_data_generator import generate_sample_data
from .services.reconciliation_engine import ReconciliationEngine
from .models.models import Transaction, Settlement, ReconciliationResult
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO
from datetime import date
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reconai")

app = FastAPI(
    title="ReconAI API",
    description="AI-Powered Payment Reconciliation System",
    version="1.0.0"
)

# Robust CORS configuration allowing all origins (Vercel, localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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


def seed_sample_data_in_db():
    """Seed sample data and run reconciliation so results exist immediately."""
    db = SessionLocal()
    try:
        data = generate_sample_data()

        # Clear existing
        db.query(ReconciliationResult).delete()
        db.query(Transaction).delete()
        db.query(Settlement).delete()

        # Insert transactions
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

        # Insert settlements
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

        # Run reconciliation engine immediately
        engine_instance = ReconciliationEngine()
        result = engine_instance.run(txn_df, stl_df, month=10, year=2026)

        for r in result["results"]:
            rec_date = r.get("reconciliation_date")
            if isinstance(rec_date, str):
                rec_date = date.fromisoformat(rec_date)
            elif rec_date is None:
                rec_date = date.today()

            db_result = ReconciliationResult(
                transaction_id=r.get("transaction_id"),
                settlement_id=r.get("settlement_id"),
                status=r["status"],
                transaction_amount=r.get("transaction_amount"),
                settlement_amount=r.get("settlement_amount"),
                variance=r.get("variance"),
                explanation=r["explanation"],
                reconciliation_date=rec_date,
                month_year=r.get("month_year", "2026-10")
            )
            db.add(db_result)

        db.commit()
        logger.info(f"Successfully seeded {len(txn_df)} txns, {len(stl_df)} stls, and {len(result['results'])} reconciliation results.")
        return len(txn_df), len(stl_df), data
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding sample data: {e}")
        raise e
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    """Auto-seed on startup if DB is empty so dashboard works out-of-the-box."""
    db = SessionLocal()
    try:
        count = db.query(Transaction).count()
        if count == 0:
            logger.info("Database is empty on startup. Auto-seeding initial sample data...")
            seed_sample_data_in_db()
    except Exception as e:
        logger.warning(f"Startup auto-seed check skipped or failed: {e}")
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "ReconAI", "version": "1.0.0"}


@app.post("/api/sample-data/generate")
def generate_sample():
    """Generate sample transaction and settlement data and run reconciliation."""
    txn_count, stl_count, data = seed_sample_data_in_db()
    return {
        "success": True,
        "transaction_count": txn_count,
        "settlement_count": stl_count,
        "message": f"Successfully generated {txn_count} transactions and {stl_count} settlements with all discrepancy cases.",
        "transactions_csv": data["transactions_csv"],
        "settlements_csv": data["settlements_csv"]
    }


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
