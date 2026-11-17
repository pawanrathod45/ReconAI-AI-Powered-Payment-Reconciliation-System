# ReconAI – AI-Powered Payment Reconciliation System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Tests](https://img.shields.io/badge/tests-18%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Node](https://img.shields.io/badge/node-18%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Problem Statement

Payment companies record customer transactions in real time, but banks settle these transactions in batches — typically 1–2 calendar days later. At month-end, the company's internal transaction records don't always match the bank's settlement records. Discrepancies arise from timing differences, rounding variations, duplicate entries, missing settlements, orphan refunds, and unmatched bank records.

**ReconAI** automates the reconciliation process, matching payment transactions against bank settlements, detecting discrepancies, and generating actionable reports — turning a manual, error-prone month-end task into an instant, auditable workflow.

## Key Features

- **📊 Dashboard** — Real-time overview of reconciliation status, summary statistics, and variance analysis
- **📤 Upload** — Drag-and-drop CSV upload for both transaction and settlement files with validation
- **⚙️ Reconciliation Engine** — Automated matching by transaction reference with configurable rounding tolerance, timing-difference detection, and duplicate identification
- **🔍 Exception Detection** — Identifies and categorises mismatches: timing differences, rounding differences, duplicates, missing settlements, orphan refunds, and unmatched bank settlements
- **📑 Reports** — Export reconciliation results as CSV or PDF; view monthly summaries with opening/closing balances

## Architecture Overview

ReconAI follows a **three-tier architecture**:

```
┌─────────────────────┐     HTTP/JSON     ┌─────────────────────┐     SQLAlchemy     ┌──────────┐
│   React Frontend    │ ◄──────────────► │   FastAPI Backend   │ ◄────────────────► │  SQLite  │
│  (Vite + Tailwind)  │                   │  (Python Services)  │                    │    DB    │
└─────────────────────┘                   └─────────────────────┘                    └──────────┘
```

- **Frontend** — React SPA built with Vite and styled with Tailwind CSS
- **Backend** — Python FastAPI application with a service layer for reconciliation logic
- **Database** — SQLite via SQLAlchemy ORM for zero-configuration persistence

For full architecture details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React 18 + Vite + Tailwind CSS    |
| Backend    | Python 3.10+ + FastAPI + Pandas   |
| Database   | SQLite + SQLAlchemy ORM           |
| Testing    | pytest                            |
| Deployment | Vercel (frontend) + Render (backend) |

## Prerequisites

- **Python** 3.10 or higher
- **Node.js** 18 or higher
- **npm** (bundled with Node.js)

## Installation & Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API server will start at **http://localhost:8000**.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The development server will start at **http://localhost:5173**.

### Environment Variables

| Variable        | Location | Default                   | Description               |
|-----------------|----------|---------------------------|---------------------------|
| `VITE_API_URL`  | Frontend | `http://localhost:8000`   | Backend API base URL      |
| `DATABASE_URL`  | Backend  | `sqlite:///reconai.db`    | Database connection string |

Create a `.env` file in the `frontend/` directory to override:

```env
VITE_API_URL=http://localhost:8000
```

## Usage

### 1. Generate Sample Data

Click the **"Generate Sample Data"** button on the Dashboard, or send a POST request:

```bash
curl -X POST http://localhost:8000/api/sample-data/generate
```

This creates realistic sample transactions and bank settlements with various discrepancy scenarios.

### 2. Upload CSV Files

Navigate to the **Upload** page and upload your files:

- **Transactions CSV** — columns: `transaction_id`, `amount`, `currency`, `transaction_date`, `description`, `status`
- **Settlements CSV** — columns: `settlement_id`, `transaction_ref`, `amount`, `settlement_date`, `bank_reference`, `status`

### 3. Run Reconciliation

Navigate to the **Reconciliation** page and click **"Run Reconciliation"**. The engine will:

1. Normalize all transaction and settlement IDs
2. Detect duplicates in settlement data
3. Identify orphan refunds
4. Match transactions to settlements by reference
5. Detect rounding and timing differences
6. Flag missing/unmatched records
7. Generate a comprehensive summary

### 4. View Reports

Navigate to the **Reports** page to view monthly reconciliation summaries and export results as CSV or PDF.

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

The test suite contains **18 test cases** covering all reconciliation scenarios. See [docs/TEST_CASES.md](docs/TEST_CASES.md) for the full test matrix.

## API Documentation

### Transactions

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| GET    | `/api/transactions/`              | List all transactions              |
| POST   | `/api/transactions/upload`        | Upload transactions CSV            |
| GET    | `/api/transactions/{id}`          | Get transaction by ID              |
| DELETE | `/api/transactions/`              | Delete all transactions            |

### Settlements

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| GET    | `/api/settlements/`               | List all settlements               |
| POST   | `/api/settlements/upload`         | Upload settlements CSV             |
| GET    | `/api/settlements/{id}`           | Get settlement by ID               |
| DELETE | `/api/settlements/`               | Delete all settlements             |

### Reconciliation

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/reconciliation/run`         | Run reconciliation engine          |
| GET    | `/api/reconciliation/results`     | Get reconciliation results         |
| GET    | `/api/reconciliation/summary`     | Get reconciliation summary         |
| GET    | `/api/reconciliation/monthly`     | Get monthly reconciliation report  |

### Reports

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| GET    | `/api/reports/export`             | Export report (CSV/PDF)            |
| GET    | `/api/reports/summary`            | Get report summary                 |

### Sample Data

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/sample-data/generate`       | Generate sample data               |
| DELETE | `/api/sample-data/clear`          | Clear all data                     |

### System

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| GET    | `/`                               | Health check / API info            |

Interactive API documentation is available at **http://localhost:8000/docs** (Swagger UI).

## Deployment

### Frontend — Vercel

The frontend is configured for deployment on [Vercel](https://vercel.com) with SPA routing via `vercel.json`.

1. Connect your repository to Vercel
2. Set the root directory to `frontend`
3. Set `VITE_API_URL` to your deployed backend URL
4. Deploy

### Backend — Render

The backend is configured for deployment on [Render](https://render.com) via `render.yaml`.

1. Connect your repository to Render
2. Render will auto-detect the `render.yaml` configuration
3. Deploy

## Assumptions

1. **Currency** — All monetary values are in Indian Rupees (INR / ₹)
2. **Unique Transaction IDs** — Each transaction has a globally unique transaction ID
3. **Bank Settlement References** — Bank settlements contain a `transaction_ref` field that maps back to a transaction ID
4. **Settlement Timing** — Bank settlements occur 1–2 calendar days after the transaction date
5. **Timezone Consistency** — All dates are in the same timezone; no cross-timezone conversions are needed
6. **Refund References** — Refund transactions use a `REF-` prefix followed by the original transaction ID
7. **Decimal Arithmetic** — All monetary calculations use Python's `Decimal` type (never `float`) to avoid floating-point precision errors
8. **Cross-Month Settlements** — Transactions near month-end that settle in the following month are classified as timing differences, not mismatches
9. **Rounding Tolerance** — A configurable tolerance (default ₹0.01) is applied when comparing transaction and settlement amounts
10. **Duplicate Detection** — Multiple settlements referencing the same transaction are flagged as duplicates, not legitimate additional payments
11. **Data Immutability** — Original uploaded records are never modified or deleted by the reconciliation engine; results are stored separately

For detailed explanations, see [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md).

## Project Structure

```
AI-Native Engineer Assesment/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic layer
│   │   ├── utils/           # Utility functions (money, validators)
│   │   ├── database.py      # Database configuration
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # pytest test suite
│   ├── requirements.txt     # Python dependencies
│   └── Procfile             # Render deployment
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   ├── pages/           # Page-level components
│   │   ├── services/        # API client layer
│   │   └── App.jsx          # Root component with routing
│   ├── vercel.json          # Vercel deployment config
│   └── package.json         # Node.js dependencies
├── docs/                    # Project documentation
│   ├── ARCHITECTURE.md
│   ├── ASSUMPTIONS.md
│   ├── RECONCILIATION_LOGIC.md
│   ├── TEST_CASES.md
│   └── PRODUCTION_LIMITATIONS.md
├── render.yaml              # Render deployment config
├── SUBMISSION_CHECKLIST.md  # Deliverables checklist
└── README.md                # This file
```

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
