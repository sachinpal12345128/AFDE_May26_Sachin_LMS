"""
LOAD stage - write cleaned and analytics frames into SQLite.

We write into the SAME database file the FastAPI backend uses
(backend/library.db) so the operational and analytics tables live
side by side and can be joined or queried via the existing app.

Operational tables (books, borrowers, transactions) are TRUNCATE-AND-LOAD
so the database matches the freshly cleaned dataset on each ETL run.

Analytics tables are CREATE-OR-REPLACE so dashboards always read the
latest snapshot:

  - analytics_most_borrowed
  - analytics_category_borrowing
  - analytics_monthly_trend
  - analytics_overdue
  - etl_run_log         (audit trail of every run)

Implementation note
-------------------
We use the stdlib `sqlite3` module directly here (rather than SQLAlchemy)
because pandas' `DataFrame.to_sql` works with `sqlite3.Connection` natively
on every pandas version without any SQLAlchemy version detection. The
FastAPI backend still uses SQLAlchemy for the live application -- the ETL
only writes the file, so the two layers stay decoupled.
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import pandas as pd

from . import config

log = logging.getLogger(__name__)


@contextmanager
def _conn():
    """Yield a sqlite3 connection that commits on success, rolls back on error."""
    # Ensure the parent dir exists (first run creates backend/library.db)
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(config.DB_PATH))
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def _ensure_app_tables(c: sqlite3.Connection) -> None:
    """Create the application's tables if they don't exist."""
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            availability_status TEXT NOT NULL DEFAULT 'Available'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS borrowers (
            borrower_id INTEGER PRIMARY KEY,
            borrower_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            borrower_id INTEGER NOT NULL,
            borrow_date DATETIME NOT NULL,
            return_date DATETIME,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS etl_run_log (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at DATETIME NOT NULL,
            raw_books INTEGER, raw_borrowers INTEGER, raw_transactions INTEGER,
            clean_books INTEGER, clean_borrowers INTEGER, clean_transactions INTEGER,
            notes TEXT
        )
        """,
    ]
    cur = c.cursor()
    for stmt in ddl:
        cur.execute(stmt)


def load_operational(
    books: pd.DataFrame, borrowers: pd.DataFrame, transactions: pd.DataFrame
) -> None:
    """Truncate and reload the operational tables from cleaned frames."""
    books_load = books[
        ["book_id", "title", "author", "category", "isbn", "availability_status"]
    ]
    borrowers_load = borrowers[["borrower_id", "borrower_name", "email", "phone"]]

    txn_load = transactions[
        ["transaction_id", "book_id", "borrower_id", "borrow_date", "return_date"]
    ].copy()
    txn_load["borrow_date"] = txn_load["borrow_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    txn_load["return_date"] = (
        txn_load["return_date"]
        .dt.strftime("%Y-%m-%d %H:%M:%S")
        .where(txn_load["return_date"].notna(), None)
    )

    with _conn() as c:
        _ensure_app_tables(c)
        cur = c.cursor()
        cur.execute("DELETE FROM transactions")
        cur.execute("DELETE FROM borrowers")
        cur.execute("DELETE FROM books")

        # pandas.to_sql with a sqlite3 Connection works on all pandas versions
        books_load.to_sql("books", c, if_exists="append", index=False)
        borrowers_load.to_sql("borrowers", c, if_exists="append", index=False)
        txn_load.to_sql("transactions", c, if_exists="append", index=False)

        # Recompute availability from open transactions
        cur.execute("UPDATE books SET availability_status='Available'")
        cur.execute(
            """
            UPDATE books
            SET availability_status = 'Borrowed'
            WHERE book_id IN (
                SELECT t.book_id FROM transactions t
                WHERE t.return_date IS NULL
            )
            """
        )

    log.info(
        "Loaded operational tables: books=%d, borrowers=%d, transactions=%d",
        len(books_load), len(borrowers_load), len(txn_load),
    )


def load_analytics(frames: dict) -> None:
    """Write the analytics frames as standalone reporting tables."""
    mapping = {
        "most_borrowed": "analytics_most_borrowed",
        "category_borrowing": "analytics_category_borrowing",
        "monthly_trend": "analytics_monthly_trend",
        "overdue": "analytics_overdue",
    }
    with _conn() as c:
        for key, table in mapping.items():
            df = frames[key].copy()
            for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
                df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
            df.to_sql(table, c, if_exists="replace", index=False)
            log.info("Loaded %s (%d rows)", table, len(df))


def log_run(raw_counts: dict, clean_counts: dict, notes: str = "") -> int:
    with _conn() as c:
        _ensure_app_tables(c)
        cur = c.cursor()
        cur.execute(
            """
            INSERT INTO etl_run_log (
                run_at,
                raw_books, raw_borrowers, raw_transactions,
                clean_books, clean_borrowers, clean_transactions,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                raw_counts["books"], raw_counts["borrowers"], raw_counts["transactions"],
                clean_counts["books"], clean_counts["borrowers"], clean_counts["transactions"],
                notes,
            ),
        )
        return cur.lastrowid or 0
