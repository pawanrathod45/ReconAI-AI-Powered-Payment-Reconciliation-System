# FINAL SUBMISSION: ReconAI – AI-Powered Payment Reconciliation System
**Candidate: Pawan Rathod**  
**Role: AI Native Engineer Intern Assessment (November 2026)**  

---

## 1. BRAINSTORMING THREAD

### System & Architecture Design Thinking

#### 1. Core Financial Problem Decomposition
Payment processors capture transactions in real time (T+0). Commercial banks aggregate credits and debit adjustments in periodic batch clearing cycles (typically T+1 or T+2). At month-end closing, ledger entries and bank statement lines inevitably diverge across four key dimensions:
- **Timing / Period Asynchrony**: Transactions initiated on the last business day of the month (e.g., October 31) clear on the first business day of the subsequent month (e.g., November 1). Treating these as missing payments or write-offs distorts financial statements. They must be identified as timing deferrals.
- **Micro-Variance & Floating-Point Drift**: Currency amounts with sub-paisa precision (e.g., ₹1,000.005) or fractional interchange fees create rounding variances that compound across thousands of transactions. Standard IEEE 754 floating-point arithmetic (`0.1 + 0.2 = 0.30000000000000004`) causes false discrepancies. Python arbitrary-precision `Decimal` is mandatory.
- **Duplicate Bank Processing**: Gateway or bank retries occasionally record the same settlement reference multiple times. The system must isolate the primary settlement, link it to the transaction, and quarantine duplicate lines to prevent duplicate revenue recognition.
- **Unlinked / Orphan Adjustments**: Chargeback reversals and refund adjustments that arrive without an identifiable parent transaction ID cannot be auto-cleared and must be routed to an Exception Desk.

#### 2. Architecture & Technology Decisions
- **Backend**: Python FastAPI + SQLAlchemy + SQLite for zero-configuration, robust local and cloud deployment.
- **Matching Heuristics**: Multi-stage waterfall pipeline (Normalize IDs ➔ Deduplicate Settlements ➔ Detect Orphan Refunds ➔ Exact Reference + Exact Amount Match ➔ Exact Reference + Rounding Tolerance Match ➔ Timing Boundary Check ➔ Unmatched Ledger Entries ➔ Unmatched Bank Deposits).
- **Frontend**: React + Vite + Tailwind CSS + Lucide Icons + Recharts, styled with dark-navy sidebar and clean light-gray SaaS dashboard aesthetic.

---

## 2. PROMPT ARTIFACTS

### A. Raw Prompt (Mandatory)
```text
# PROJECT: ReconAI – AI-Powered Payment Reconciliation System

## 1. YOUR ROLE
Act as a Senior Full-Stack Developer, FinTech Software Architect, Data Engineer, QA Engineer, and UI/UX Designer.
Your task is to independently design, develop, test, and prepare a complete production-style application named ReconAI.
This project is for the Onelab AI Native Engineer Intern Assessment (November 2026).
Do not build just a prototype, static dashboard, or UI mockup. Build a fully functional application with real reconciliation logic, generated datasets, test cases, and documentation.
Work directly in the current project workspace. Create all required files and folders.

## 2. PROBLEM STATEMENT
A payments company records every transaction immediately when a customer makes a payment.
However, the bank settles the funds in batches, usually 1–2 days later.
At the end of the month, the payment company's transaction records and bank settlement records should reconcile.
Unfortunately, they do not always match.
Build a reconciliation system that:
1. Reads payment transaction data.
2. Reads bank settlement data.
3. Automatically matches transactions against settlements.
4. Identifies missing, delayed, duplicated, and mismatched records.
5. Explains why the books do not balance.
6. Displays a reconciliation summary.
7. Generates downloadable reports.
The system must deliberately demonstrate all four discrepancy types required by the assessment.

## 3. MANDATORY DISCREPANCY TYPES
Generate realistic sample datasets containing the following:
Case 1: Next-Month Settlement (TXN1001, Oct 31, ₹5000 -> Nov 1, ₹5000)
Case 2: Rounding Difference (₹1000.005 vs ₹1000.00)
Case 3: Duplicate Entry (TXN1003, ₹2500 -> duplicate settlement in bank statement)
Case 4: Orphan Refund (REF1004, ₹750 referencing non-existent TXN9999)
Use Python Decimal for financial calculations. Never use floating-point arithmetic for monetary matching.

## 4. TECHNOLOGY STACK
Frontend: React.js, Vite, Tailwind CSS, Recharts, Lucide React icons
Backend: Python, FastAPI, Pandas, Pydantic, SQLite, SQLAlchemy
Testing: Pytest (TC01 - TC18)
Deployment: Frontend on Vercel, Backend on Render
```

### B. Distilled Prompt
```text
Act as a Principal FinTech Engineer. Build "ReconAI", an automated end-to-end payment reconciliation system adhering to these non-negotiables:
1. FINANCIAL ARITHMETIC: Enforce Python decimal.Decimal across all monetary models, validators, and matching calculations. Prohibit IEEE 754 floats.
2. DISCREPANCY HEURISTICS: Deterministically generate sample datasets (seed=42, 40+ txns) containing:
   - Next-Month Settlement (TXN1001 Oct 31 -> Nov 1) classified as TIMING_DIFFERENCE (not a loss)
   - Rounding Difference (individual sub-paisa diffs + cumulative aggregate variance)
   - Duplicate Bank Settlement (STL-1003B quarantined; revenue never double-counted)
   - Orphan Refund (REF1004 referencing unmapped TXN9999)
   - Unmatched transactions & unclaimed bank settlements
3. MATCHING ENGINE: Implement a prioritized matching engine: ID Normalization -> Duplicate Quarantine -> Orphan Quarantine -> Exact Ref & Amount -> Exact Ref & Tolerance (0.01) -> Cross-Month Timing Detection -> Missing Settlement Classification.
4. FULL-STACK IMPLEMENTATION:
   - FastAPI: REST endpoints for /upload, /reconciliation/run, /summary, /results, /exceptions, /monthly, /reports/export (CSV & ReportLab PDF), and auto-seeding on startup.
   - React 18 + Vite + Tailwind: Dark-navy SaaS layout, Dashboard with Recharts, Upload desk, Reconciliation table with category tabs, Exception desk, PDF/CSV Reports, and Settings.
5. TESTING & VERIFICATION: 18 automated pytest test cases (TC01-TC18) covering all discrepancy types, boundary cases, empty inputs, and non-INR currency rejections.
```

---

## 3. CLAUDE CODE & EXECUTION THREAD (Including Wrong Turns & Fixes)

### Chronological Execution Log

| Phase | Action / Step | Issue / Wrong Turn Encountered | Resolution & Correction Applied |
|---|---|---|---|
| **1. Setup** | Initial directory generation | PowerShell rejected `&&` chaining syntax | Converted PowerShell commands to `;` chaining and `New-Item -ItemType Directory`. |
| **2. Swarm** | Spawned multi-agent swarm workers | Model hit rate limits (`RESOURCE_EXHAUSTED 429`) on Opus subagents | Migrated to main model session to implement all files directly in workspace without token blockage. |
| **3. Backend** | Python requirements installation | Missing `pytest`, `sqlalchemy`, `reportlab`, `python-multipart` | Ran `python -m pip install pytest sqlalchemy reportlab python-multipart` into environment. |
| **4. Engine** | Reconciliation engine build | Needed to ensure duplicate settlements don't inflate totals | Added settlement pre-scan step: duplicate refs are quarantined so legitimate matching only pairs the primary record once. |
| **5. Frontend** | Vite React build | Missing `Reconciliation.jsx`, `Exceptions.jsx`, `Reports.jsx`, `Settings.jsx` | Built all 4 pages with full API bindings, filter tabs, CSV/PDF download handlers, and responsive tables. `npm run build` passed in 1.54s. |
| **6. Git Remote** | Pushing to GitHub | User command included `<` and `>` angle brackets; PowerShell truncated URL to `https://github.com/<pawanrathod45>/<` | Fixed remote URL to `https://github.com/pawanrathod45/ReconAI-AI-Powered-Payment-Reconciliation-System.git` and set branch to `main`. |
| **7. Git Push** | Remote reject `[rejected] (fetch first)` | Remote GitHub repository had an initial commit with a blank README | Ran `git push -u origin main --force` to push the complete local repository to GitHub. |
| **8. Render Build** | Render deployment failed with `No such file: 'requirements.txt'` | Render executed `pip install -r requirements.txt` at root, but file was in `backend/` | Created root `requirements.txt`, root `main.py` entrypoint, and root `Procfile`. Pushed commit `e60fd14`. |
| **9. Sample Data** | Sample data not appearing on Dashboard | `generate_sample()` only saved raw records to DB without executing engine, and CORS blocked cross-origin credentials | Updated `main.py` to auto-execute `ReconciliationEngine` upon generation, enabled startup auto-seeding, and configured permissive wildcard CORS headers. |

---

## 4. TEST CASES SPECIFICATION & RESULTS (TC01 – TC18)

All 18 automated tests are located in `backend/tests/test_reconciliation.py`.
Run command: `python -m pytest backend/tests/ -v`

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\admin\Downloads\AI-Native Engineer Assesment
collected 18 items

backend/tests/test_reconciliation.py::TestReconciliation::test_tc01_exact_match PASSED              [  5%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc02_one_day_delay PASSED            [ 11%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc03_two_day_delay PASSED            [ 16%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc04_next_month_settlement PASSED    [ 22%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc05_individual_rounding PASSED      [ 27%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc06_aggregate_rounding PASSED       [ 33%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc07_duplicate_settlement PASSED     [ 38%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc08_orphan_refund PASSED            [ 44%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc09_missing_settlement PASSED       [ 50%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc10_unmatched_settlement PASSED     [ 55%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc11_invalid_csv PASSED              [ 61%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc12_missing_columns PASSED          [ 66%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc13_invalid_amount PASSED           [ 72%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc14_duplicate_transaction_ids PASSED [ 77%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc15_month_end_reconciliation PASSED [ 83%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc16_empty_datasets PASSED          [ 88%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc17_non_inr_currency_rejected PASSED [ 94%]
backend/tests/test_reconciliation.py::TestReconciliation::test_tc18_duplicate_not_counted_twice PASSED [100%]

============================= 18 passed in 0.71s ==============================
```

---

## 5. WORKING OUTPUT & PRODUCTION EVALUATION

### A. Repository & Deployment Links
- **GitHub Repository**: [https://github.com/pawanrathod45/ReconAI-AI-Powered-Payment-Reconciliation-System](https://github.com/pawanrathod45/ReconAI-AI-Powered-Payment-Reconciliation-System)
- **Backend API (Render)**: `https://reconai-api.onrender.com` (or your active Render service URL)
- **Frontend App (Vercel)**: `https://reconai-ai-powered-payment-reconciliation-system.vercel.app` (or your active Vercel deployment URL)
- **Local Source ZIP**: `ReconAI_Submission.zip` (91.3 KB, generated at project root)

### B. Demo Video Walkthrough Script (3–4 minutes)
1. **0:00 - 0:45 | Introduction & Stack**: Present ReconAI problem statement (batch bank settlement lag) and architecture (FastAPI + Decimal arithmetic + React/Vite/Tailwind).
2. **0:45 - 1:30 | Ingestion & Sample Data**: Open `/upload`. Demonstrate CSV upload areas. Click "Generate Sample Data" to load the deterministic 40 transactions and 42 settlements.
3. **1:30 - 2:30 | Reconciliation Engine & 4 Discrepancy Types**:
   - Open `/reconciliation`. Select October 2026 and run engine.
   - Show **Timing Difference**: `TXN1001` (Oct 31) settled Nov 01 (timing deferral, not a loss).
   - Show **Rounding Difference**: `TXN1002` (₹1,000.005 vs ₹1,000.00) and aggregate cumulative variance.
   - Show **Duplicate Entry**: `STL-1003B` quarantined without inflating legitimate revenue.
   - Show **Orphan Refund**: `REF1004` referencing non-existent `TXN9999`.
4. **2:30 - 3:00 | Financial Dashboard & Reports**:
   - Return to `/` to view Recharts visualizations and metric cards.
   - Open `/reports` and download the formal **Audit PDF** and **Ledger CSV**.
5. **3:00 - 3:30 | Test Suite Execution**: Run `python -m pytest backend/tests/ -v` in terminal demonstrating 18/18 passing tests.

### C. Exactly 3 Sentences on What It Would Get Wrong in Production
1. **Manual Ingestion Fragility**: Without direct ISO 20022 or host-to-host bank SFTP/API feeds, the system relies on manual CSV uploads that introduce ingestion latency, human handling errors, and cannot handle streaming real-time intraday settlements.
2. **Strict Reference-Centric Matching**: The reconciliation engine matches records strictly by transaction reference IDs, meaning it would fail to reconcile legitimate settlements that have truncated, misspelled, or obfuscated bank statement descriptions without fuzzy multi-field heuristics (matching on amount, timestamp proximity, and merchant metadata).
3. **Absence of Enterprise FinTech Controls**: In a real production banking environment, the system would fail to account for multi-currency foreign exchange revaluations, tiered card-network interchange fee deductions, chargeback representment workflows, and regulatory SOX/PCI-DSS audit compliance logging.
