"""
Phase 2 — Analytics router.

These endpoints serve data produced by the ETL pipeline (etl/run_etl.py).
They read directly from the reporting tables the ETL populates so the
backend stays decoupled from the cleaning logic.

Endpoints:
  GET /analytics/most-borrowed?limit=10
  GET /analytics/category-borrowing
  GET /analytics/monthly-trend
  GET /analytics/overdue
  GET /analytics/summary             (KPI tiles for the analytics dashboard)
  GET /analytics/etl-runs            (recent ETL runs from etl_run_log)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _table_exists(db: Session, name: str) -> bool:
    row = db.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:n"),
        {"n": name},
    ).first()
    return row is not None


def _rows_as_dicts(rows) -> List[dict]:
    return [dict(r._mapping) for r in rows]


def _require_analytics(db: Session) -> None:
    """Helpful 404 instead of a 500 when the ETL hasn't been run yet."""
    needed = [
        "analytics_most_borrowed",
        "analytics_category_borrowing",
        "analytics_monthly_trend",
        "analytics_overdue",
    ]
    missing = [t for t in needed if not _table_exists(db, t)]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=(
                "Analytics tables not found: "
                + ", ".join(missing)
                + ". Run the ETL first:  python -m etl.run_etl"
            ),
        )


@router.get("/most-borrowed")
def most_borrowed(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Top-N most borrowed books, ranked by borrow_count."""
    _require_analytics(db)
    rows = db.execute(
        text(
            """
            SELECT book_id, title, author, category, borrow_count
            FROM analytics_most_borrowed
            ORDER BY borrow_count DESC, title ASC
            LIMIT :limit
            """
        ),
        {"limit": limit},
    ).all()
    return _rows_as_dicts(rows)


@router.get("/category-borrowing")
def category_borrowing(db: Session = Depends(get_db)):
    """Borrow count grouped by book category."""
    _require_analytics(db)
    rows = db.execute(
        text(
            """
            SELECT category, borrow_count
            FROM analytics_category_borrowing
            ORDER BY borrow_count DESC
            """
        )
    ).all()
    return _rows_as_dicts(rows)


@router.get("/monthly-trend")
def monthly_trend(db: Session = Depends(get_db)):
    """Borrowing trend per month (YYYY-MM)."""
    _require_analytics(db)
    rows = db.execute(
        text(
            """
            SELECT month, borrow_count
            FROM analytics_monthly_trend
            ORDER BY month ASC
            """
        )
    ).all()
    return _rows_as_dicts(rows)


@router.get("/overdue")
def overdue(
    only_open: Optional[bool] = Query(
        None, description="If true, only still-open overdue loans"
    ),
    db: Session = Depends(get_db),
):
    """Overdue transactions (loan_days > 14)."""
    _require_analytics(db)
    sql = """
        SELECT transaction_id, book_id, title, borrower_id, borrower_name,
               borrow_date, return_date, loan_days, is_returned
        FROM analytics_overdue
    """
    if only_open:
        sql += " WHERE is_returned = 0"
    sql += " ORDER BY loan_days DESC"
    rows = db.execute(text(sql)).all()
    return _rows_as_dicts(rows)


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    """High-level KPIs for the analytics landing page."""
    _require_analytics(db)
    total_borrows = db.execute(
        text("SELECT COALESCE(SUM(borrow_count), 0) FROM analytics_most_borrowed")
    ).scalar()
    unique_books = db.execute(
        text("SELECT COUNT(*) FROM analytics_most_borrowed")
    ).scalar()
    overdue_count = db.execute(
        text("SELECT COUNT(*) FROM analytics_overdue")
    ).scalar()
    open_overdue = db.execute(
        text("SELECT COUNT(*) FROM analytics_overdue WHERE is_returned = 0")
    ).scalar()
    top = db.execute(
        text(
            "SELECT title, borrow_count FROM analytics_most_borrowed "
            "ORDER BY borrow_count DESC LIMIT 1"
        )
    ).first()
    top_category = db.execute(
        text(
            "SELECT category, borrow_count FROM analytics_category_borrowing "
            "ORDER BY borrow_count DESC LIMIT 1"
        )
    ).first()
    return {
        "total_borrows": int(total_borrows or 0),
        "unique_books_borrowed": int(unique_books or 0),
        "overdue_total": int(overdue_count or 0),
        "overdue_open": int(open_overdue or 0),
        "top_book": (
            {"title": top.title, "borrow_count": top.borrow_count} if top else None
        ),
        "top_category": (
            {"category": top_category.category, "borrow_count": top_category.borrow_count}
            if top_category
            else None
        ),
    }


@router.get("/etl-runs")
def etl_runs(db: Session = Depends(get_db)):
    """Recent ETL run audit trail."""
    if not _table_exists(db, "etl_run_log"):
        return []
    rows = db.execute(
        text(
            """
            SELECT run_id, run_at,
                   raw_books, raw_borrowers, raw_transactions,
                   clean_books, clean_borrowers, clean_transactions,
                   notes
            FROM etl_run_log
            ORDER BY run_id DESC
            LIMIT 20
            """
        )
    ).all()
    return _rows_as_dicts(rows)
