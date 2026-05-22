"""
Central paths & settings for the ETL pipeline.

The pipeline reads CSVs from ../datasets/ and writes into the same SQLite
database the FastAPI backend uses (backend/library.db). This is by design —
the application's tables (books, borrowers, transactions) act as the
"operational store", and the ETL adds reporting / analytics tables alongside.
"""

from pathlib import Path

# Resolve paths relative to the project root (one level up from etl/)
ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT / "datasets"
BACKEND_DIR = ROOT / "backend"

BOOKS_CSV = DATASETS_DIR / "books.csv"
BORROWERS_CSV = DATASETS_DIR / "borrowers.csv"
TRANSACTIONS_CSV = DATASETS_DIR / "transactions.csv"

# The backend's SQLite DB. The ETL writes into the same file so analytics
# tables and operational tables can be joined freely.
DB_PATH = BACKEND_DIR / "library.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Output folder for run reports (CSV snapshots & summary JSON)
REPORTS_DIR = ROOT / "etl" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
