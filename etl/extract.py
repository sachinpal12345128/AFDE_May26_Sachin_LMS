"""
EXTRACT stage — read raw CSV datasets into Pandas DataFrames.

The raw files in datasets/ are deliberately messy: duplicate ISBNs,
missing return dates, blank emails, inconsistent casing, stray whitespace.
The Extract stage does NOT clean anything — it just loads the data as-is
so the Transform stage has a single, clear job.
"""

from __future__ import annotations

import logging

import pandas as pd

from . import config

log = logging.getLogger(__name__)


def extract_books() -> pd.DataFrame:
    """Load books.csv as-is."""
    df = pd.read_csv(config.BOOKS_CSV, dtype=str)
    log.info("Extracted %d raw rows from books.csv", len(df))
    return df


def extract_borrowers() -> pd.DataFrame:
    """Load borrowers.csv as-is."""
    df = pd.read_csv(config.BORROWERS_CSV, dtype=str)
    log.info("Extracted %d raw rows from borrowers.csv", len(df))
    return df


def extract_transactions() -> pd.DataFrame:
    """Load transactions.csv as-is. Dates are kept as strings here."""
    df = pd.read_csv(config.TRANSACTIONS_CSV, dtype=str)
    log.info("Extracted %d raw rows from transactions.csv", len(df))
    return df


def extract_all() -> dict[str, pd.DataFrame]:
    """Convenience — extract all three datasets in one call."""
    return {
        "books": extract_books(),
        "borrowers": extract_borrowers(),
        "transactions": extract_transactions(),
    }
