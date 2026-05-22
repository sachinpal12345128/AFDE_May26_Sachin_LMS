# Library Management System - Phase 2 (ETL + Analytics)

**Capstone:** Library_Management_System_Phase2 (extends `AFDE_May26_Sachin_LMS`)
**Stack:** React (Vite) + Chart.js / FastAPI / SQLite / Pandas ETL

Phase 2 extends the Phase 1 CRUD application with a Pandas ETL pipeline that
ingests messy CSV datasets, cleans them, loads analytics-ready tables, and
powers a new in-app analytics dashboard.

---

## 1. What's new in Phase 2

| Area                | Phase 1                                  | Phase2
|                                              |
|---------------------|------------------------------------------|------------------------------------------------------|
| Data ingestion      | Manual entry via REST API                | Pandas ETL from CSV datasets                         |
| Database            | books, borrowers, transactions           | + analytics_* reporting tables + etl_run_log         |
| Backend             | CRUD + search + dashboard                | + `/analytics/*` endpoints                           |
| Frontend            | Dashboard / Books / Borrowers / Txns     | + Analytics page (charts + overdue table)            |
| Workflow            | -                                        | `python -m etl.run_etl` rebuilds the DB              |

The four required analytics features are all delivered:

1. **Most borrowed books** -> `/analytics/most-borrowed`
2. **Category-wise borrowing** -> `/analytics/category-borrowing`
3. **Monthly borrowing trends** -> `/analytics/monthly-trend`
4. **Overdue transaction analysis** -> `/analytics/overdue`

---

## 2. Project structure

```
Library_Management_System_Phase2/
|-- backend/                      FastAPI app + SQLAlchemy models
|   |-- main.py
|   |-- database.py
|   |-- models.py / schemas.py / crud.py
|   |-- routers/
|   |   |-- books.py / borrowers.py / transactions.py / search.py / dashboard.py
|   |   `-- analytics.py          <-- NEW: serves data produced by ETL
|   `-- seed_db.py
|-- etl/                          NEW: Pandas ETL pipeline (Phase 2)
|   |-- __init__.py
|   |-- config.py                 paths + DB URL
|   |-- extract.py                read raw CSVs
|   |-- transform.py              clean + derive + analytics frames
|   |-- load.py                   write into SQLite (operational + analytics)
|   |-- run_etl.py                orchestrator (Extract -> Transform -> Load)
|   `-- reports/                  per-run CSV snapshots + summary.json
|-- datasets/                     NEW: input CSVs (297 raw rows)
|   |-- books.csv
|   |-- borrowers.csv
|   `-- transactions.csv
|-- frontend/                     React 18 + Vite + Chart.js
|   `-- src/
|       |-- App.jsx               + /analytics route
|       |-- api.js                + analytics* helpers
|       |-- components/Navbar.jsx + Analytics link
|       `-- pages/Analytics.jsx   NEW: charts + overdue table
|-- database/
|   |-- schema.sql                + analytics tables documented
|   `-- seed.sql
|-- docs/                         API.md, SETUP.md, postman collection
|-- screenshots/
|-- requirements.txt              + pandas, numpy
`-- README.md                     (this file)
```

---

## 3. The ETL workflow

The pipeline is built around three small, single-responsibility modules.

### 3.1 Extract (`etl/extract.py`)

Loads the three raw CSVs **as-is**, with no cleaning. Datasets are deliberately
dirty (duplicate ISBNs, missing return dates, blank emails, inconsistent
category casing, stray whitespace) so the Transform stage has something real
to do.

```
extract_books()       -> 45 raw rows
extract_borrowers()   -> 39 raw rows
extract_transactions()-> 213 raw rows
```

### 3.2 Transform (`etl/transform.py`)

Each entity has its own cleaning function:

| Entity        | Cleaning rules                                                                 |
|---------------|-------------------------------------------------------------------------------|
| books         | strip whitespace; normalize null tokens; drop rows missing isbn/title;        |
|               | fill missing author/category with "Unknown"; Title-Case category;             |
|               | drop duplicate isbns                                                          |
| borrowers     | strip whitespace; drop rows missing email/name; default phone "0000000000";   |
|               | lower-case email; drop duplicate emails                                       |
| transactions  | drop rows missing isbn / email / borrow_date; parse dates;                    |
|               | resolve foreign keys by joining on isbn / email; drop rows that cannot       |
|               | be linked; drop exact duplicates; derive `loan_days`, `is_returned`,         |
|               | `is_overdue` (loan > 14 days)                                                |

After cleaning, `build_analytics(books, borrowers, transactions)` produces the
four reporting frames:

- `most_borrowed`        - GROUP BY book, COUNT(*)
- `category_borrowing`   - GROUP BY category, COUNT(*)
- `monthly_trend`        - GROUP BY YYYY-MM(borrow_date), COUNT(*)
- `overdue`              - rows where `loan_days` > 14

### 3.3 Load (`etl/load.py`)

Writes into the **same** SQLite file the FastAPI backend uses
(`backend/library.db`) so operational and analytics tables live side-by-side:

- Operational tables (`books`, `borrowers`, `transactions`) are
  **truncate-and-load** so the database always reflects the cleaned dataset.
- Analytics tables (`analytics_*`) are **create-or-replace** via
  `pandas.DataFrame.to_sql(..., if_exists='replace')`.
- Every run is logged in `etl_run_log` (raw counts vs. clean counts).
- A timestamped CSV snapshot of every frame is written under
  `etl/reports/<timestamp>/` for screenshots and debugging.

### 3.4 Run it

From the project root:

```bash
python -m etl.run_etl
```

Sample output (from a real run):

```
[1/3] Extract
  books.csv: 45 rows  borrowers.csv: 39 rows  transactions.csv: 213 rows
[2/3] Transform
  books         dropped 3 duplicate isbns
  borrowers     dropped 2 duplicate emails
  transactions  dropped 5 missing-date + 3 unlinkable + 5 duplicates
  analytics built (36 / 9 / 13 / 80 rows)
[3/3] Load
  Loaded books=42, borrowers=37, transactions=200
  Snapshot written to etl/reports/<timestamp>/
  ETL run id: 1
```

---

## 4. Dataset details

All three input files live in `datasets/` and total **297 raw rows** (well
above the 150-record minimum). The pipeline cleans them to **279 records**
that make it into the operational store.

| File              | Raw rows | Clean rows | Notes                                  |
|-------------------|----------|-----------|----------------------------------------|
| books.csv         | 45       | 42        | 3 dup isbns + 2 dirty rows dropped     |
| borrowers.csv     | 39       | 37        | 2 dup emails dropped                   |
| transactions.csv  | 213      | 200       | 13 rows dropped (missing/bogus/dup)    |

The transaction dates span the last 12 months and include three classes:
returned-on-time, returned-late, and still-open. The "still open" rows are the
ones that show up as overdue in the analytics.

---

## 5. Setup and run

### 5.1 Backend + ETL

```bash
# from project root
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# Step 1: run the ETL to (re)build the SQLite database from datasets/
python -m etl.run_etl

# Step 2: start the API
cd backend
uvicorn main:app --reload --port 8000
```

- API:     http://localhost:8000
- Swagger: http://localhost:8000/docs

### 5.2 Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite serves the app on http://localhost:5173. The new **Analytics** tab is in
the top navigation.

### 5.3 Reset the database

```bash
rm backend/library.db   # macOS/Linux
del backend\library.db  # Windows
python -m etl.run_etl
```

---

## 6. API summary (Phase 2 additions)

| Method | Endpoint                              | Description                                |
|--------|---------------------------------------|--------------------------------------------|
| GET    | `/analytics/summary`                  | KPI tiles (totals + top book + top cat.)   |
| GET    | `/analytics/most-borrowed?limit=10`   | Top-N most borrowed books                  |
| GET    | `/analytics/category-borrowing`       | Borrow count per category                  |
| GET    | `/analytics/monthly-trend`            | Borrow count per YYYY-MM                   |
| GET    | `/analytics/overdue?only_open=true`   | Overdue transactions (loan_days > 14)      |
| GET    | `/analytics/etl-runs`                 | Recent ETL runs (audit log)                |

All Phase 1 endpoints (`/books`, `/borrowers`, `/borrow`, `/return`,
`/transactions`, `/search`, `/dashboard/stats`) continue to work unchanged.

---

## 7. Screenshots to capture for submission

Save these into the `screenshots/` folder:

- `etl_run.png`               - terminal output of `python -m etl.run_etl`
- `analytics_dashboard.png`   - the new /analytics page
- `most_borrowed.png`         - top-10 books bar chart
- `category_borrowing.png`    - category doughnut chart
- `monthly_trend.png`         - monthly line chart
- `overdue_table.png`         - overdue transactions table
- `swagger_analytics.png`     - the /analytics/* endpoints in Swagger UI
- `etl_runs_history.png`      - ETL run audit table at the bottom of /analytics

---

## 8. Submission checklist (from Phase 2 common instructions)

- [x] Python ETL scripts using Pandas
- [x] CSV datasets in `datasets/`
- [x] Clear Extract / Transform / Load stages
- [x] Cleaned data stored in reporting / analytics tables
- [x] Frontend dashboard displays the analytics
- [x] Dataset > 150 records (297 raw / 279 clean)
- [x] README documents the ETL workflow
- [ ] GitHub repository with daily commits     (do at submission time)
- [ ] Screenshots of ETL execution + dashboards (capture after running)

---

## 9. License & attribution

Capstone submission for FDE training - Phase 2. Builds directly on the
Phase 1 deliverable (`AFDE_May26_Sachin_LMS`). Free to reuse for educational
purposes.
