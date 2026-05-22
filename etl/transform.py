"""
TRANSFORM stage — clean and reshape the extracted DataFrames.

Cleaning rules
--------------
Books
  - Strip whitespace, normalize blank/"na"/"null" to NaN
  - Drop rows missing isbn (we cannot key without it)
  - Fill missing author/category with "Unknown"
  - Normalize category casing to Title Case
  - Drop duplicate isbns (keep first)

Borrowers
  - Strip whitespace, normalize blanks/"na"/"null" to NaN
  - Drop rows missing email
  - Fill missing phone with "0000000000"
  - Drop duplicate emails (keep first)

Transactions
  - Strip whitespace, normalize blanks to NaT for dates
  - Drop rows missing isbn, borrower_email, OR borrow_date
  - Drop transactions whose isbn / email aren't in the cleaned books/borrowers
  - Parse borrow_date and return_date as datetime
  - Compute is_returned, loan_days, is_overdue (loan > 14 days OR open > 14d)
  - Drop exact duplicate rows

After cleaning, the operational rows are returned in the shape the application
expects (matching the SQLAlchemy models). Analytics frames are produced
separately by ``build_analytics``.
"""

from __future__ import annotations

import logging
from datetime import datetime

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

OVERDUE_LIMIT_DAYS = 14
NULL_TOKENS = {"", "na", "n/a", "null", "none", "nan"}


def _norm_str(series: pd.Series) -> pd.Series:
    """Strip whitespace and turn null-tokens into NaN."""
    s = series.astype("string").str.strip()
    return s.mask(s.str.lower().isin(NULL_TOKENS))


# ---------- BOOKS ----------
def clean_books(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    for col in ("title", "author", "category", "isbn"):
        df[col] = _norm_str(df[col])

    before = len(df)
    df = df.dropna(subset=["isbn", "title"])
    log.info("books: dropped %d rows missing isbn/title", before - len(df))

    df["author"] = df["author"].fillna("Unknown")
    df["category"] = df["category"].fillna("Unknown").str.title()

    before = len(df)
    df = df.drop_duplicates(subset=["isbn"], keep="first")
    log.info("books: dropped %d duplicate isbn rows", before - len(df))

    df["availability_status"] = "Available"
    df = df.reset_index(drop=True)
    df.insert(0, "book_id", df.index + 1)
    return df[["book_id", "title", "author", "category", "isbn", "availability_status"]]


# ---------- BORROWERS ----------
def clean_borrowers(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    for col in ("borrower_name", "email", "phone"):
        df[col] = _norm_str(df[col])

    before = len(df)
    df = df.dropna(subset=["email", "borrower_name"])
    log.info("borrowers: dropped %d rows missing email/name", before - len(df))

    df["phone"] = df["phone"].fillna("0000000000")
    df["email"] = df["email"].str.lower()

    before = len(df)
    df = df.drop_duplicates(subset=["email"], keep="first")
    log.info("borrowers: dropped %d duplicate email rows", before - len(df))

    df = df.reset_index(drop=True)
    df.insert(0, "borrower_id", df.index + 1)
    return df[["borrower_id", "borrower_name", "email", "phone"]]


# ---------- TRANSACTIONS ----------
def clean_transactions(
    raw: pd.DataFrame, books: pd.DataFrame, borrowers: pd.DataFrame
) -> pd.DataFrame:
    df = raw.copy()
    for col in ("isbn", "borrower_email", "borrow_date", "return_date"):
        df[col] = _norm_str(df[col])

    df["borrower_email"] = df["borrower_email"].str.lower()

    before = len(df)
    df = df.dropna(subset=["isbn", "borrower_email", "borrow_date"])
    log.info("transactions: dropped %d rows missing isbn/email/borrow_date", before - len(df))

    # Parse dates
    df["borrow_date"] = pd.to_datetime(df["borrow_date"], errors="coerce")
    df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["borrow_date"])
    log.info("transactions: dropped %d rows with unparseable borrow_date", before - len(df))

    # Resolve FK by joining on isbn / email
    df = df.merge(books[["book_id", "isbn"]], on="isbn", how="left")
    df = df.merge(
        borrowers[["borrower_id", "email"]].rename(columns={"email": "borrower_email"}),
        on="borrower_email",
        how="left",
    )

    before = len(df)
    df = df.dropna(subset=["book_id", "borrower_id"])
    log.info("transactions: dropped %d rows with unknown isbn or email", before - len(df))

    df["book_id"] = df["book_id"].astype(int)
    df["borrower_id"] = df["borrower_id"].astype(int)

    before = len(df)
    df = df.drop_duplicates(
        subset=["book_id", "borrower_id", "borrow_date", "return_date"], keep="first"
    )
    log.info("transactions: dropped %d duplicate rows", before - len(df))

    # Derived fields
    today = pd.Timestamp(datetime.utcnow().date())
    df["is_returned"] = df["return_date"].notna()
    df["loan_days"] = np.where(
        df["is_returned"],
        (df["return_date"] - df["borrow_date"]).dt.days,
        (today - df["borrow_date"]).dt.days,
    )
    df["is_overdue"] = df["loan_days"] > OVERDUE_LIMIT_DAYS

    df = df.reset_index(drop=True)
    df.insert(0, "transaction_id", df.index + 1)
    return df[
        [
            "transaction_id",
            "book_id",
            "borrower_id",
            "borrow_date",
            "return_date",
            "is_returned",
            "loan_days",
            "is_overdue",
        ]
    ]


# ---------- ANALYTICS ----------
def build_analytics(
    books: pd.DataFrame, borrowers: pd.DataFrame, transactions: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """Produce the four analytics tables required by the spec."""
    txn_books = transactions.merge(books, on="book_id", how="left")

    # 1. Most borrowed books
    most_borrowed = (
        txn_books.groupby(["book_id", "title", "author", "category"], as_index=False)
        .size()
        .rename(columns={"size": "borrow_count"})
        .sort_values("borrow_count", ascending=False)
        .reset_index(drop=True)
    )

    # 2. Category-wise borrowing
    category_borrowing = (
        txn_books.groupby("category", as_index=False)
        .size()
        .rename(columns={"size": "borrow_count"})
        .sort_values("borrow_count", ascending=False)
        .reset_index(drop=True)
    )

    # 3. Monthly borrowing trend (last 12 months bucketed by YYYY-MM)
    trend = transactions.copy()
    trend["month"] = trend["borrow_date"].dt.to_period("M").astype(str)
    monthly_trend = (
        trend.groupby("month", as_index=False)
        .size()
        .rename(columns={"size": "borrow_count"})
        .sort_values("month")
        .reset_index(drop=True)
    )

    # 4. Overdue transactions
    overdue = transactions[transactions["is_overdue"]].copy()
    overdue = overdue.merge(books[["book_id", "title"]], on="book_id", how="left")
    overdue = overdue.merge(
        borrowers[["borrower_id", "borrower_name"]], on="borrower_id", how="left"
    )
    overdue = overdue[
        [
            "transaction_id",
            "book_id",
            "title",
            "borrower_id",
            "borrower_name",
            "borrow_date",
            "return_date",
            "loan_days",
            "is_returned",
        ]
    ].sort_values("loan_days", ascending=False).reset_index(drop=True)

    log.info(
        "analytics built — most_borrowed=%d, categories=%d, months=%d, overdue=%d",
        len(most_borrowed), len(category_borrowing), len(monthly_trend), len(overdue),
    )

    return {
        "most_borrowed": most_borrowed,
        "category_borrowing": category_borrowing,
        "monthly_trend": monthly_trend,
        "overdue": overdue,
    }
