"""
CRUD layer — pure database operations.

Routers stay thin and just call into this module. This separation makes
the code easier to test and means we can swap the persistence layer
(say to PostgreSQL or to a repository pattern) without touching routes.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

import models
import schemas


# ---------- Books ----------
def get_books(db: Session) -> List[models.Book]:
    return db.query(models.Book).order_by(models.Book.book_id).all()


def get_book(db: Session, book_id: int) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.book_id == book_id).first()


def get_book_by_isbn(db: Session, isbn: str) -> Optional[models.Book]:
    return db.query(models.Book).filter(models.Book.isbn == isbn).first()


def create_book(db: Session, payload: schemas.BookCreate) -> models.Book:
    book = models.Book(
        title=payload.title,
        author=payload.author,
        category=payload.category,
        isbn=payload.isbn,
        availability_status="Available",
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def update_book(
    db: Session, book: models.Book, payload: schemas.BookUpdate
) -> models.Book:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book: models.Book) -> None:
    db.delete(book)
    db.commit()


# ---------- Borrowers ----------
def get_borrowers(db: Session) -> List[models.Borrower]:
    return db.query(models.Borrower).order_by(models.Borrower.borrower_id).all()


def get_borrower(db: Session, borrower_id: int) -> Optional[models.Borrower]:
    return (
        db.query(models.Borrower)
        .filter(models.Borrower.borrower_id == borrower_id)
        .first()
    )


def get_borrower_by_email(db: Session, email: str) -> Optional[models.Borrower]:
    return db.query(models.Borrower).filter(models.Borrower.email == email).first()


def create_borrower(
    db: Session, payload: schemas.BorrowerCreate
) -> models.Borrower:
    borrower = models.Borrower(**payload.model_dump())
    db.add(borrower)
    db.commit()
    db.refresh(borrower)
    return borrower


def update_borrower(
    db: Session, borrower: models.Borrower, payload: schemas.BorrowerUpdate
) -> models.Borrower:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(borrower, field, value)
    db.commit()
    db.refresh(borrower)
    return borrower


def delete_borrower(db: Session, borrower: models.Borrower) -> None:
    db.delete(borrower)
    db.commit()


# ---------- Transactions ----------
def borrow_book(
    db: Session, book: models.Book, borrower: models.Borrower
) -> models.Transaction:
    txn = models.Transaction(
        book_id=book.book_id,
        borrower_id=borrower.borrower_id,
        borrow_date=datetime.utcnow(),
        return_date=None,
    )
    book.availability_status = "Borrowed"
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def return_book(db: Session, txn: models.Transaction) -> models.Transaction:
    txn.return_date = datetime.utcnow()
    if txn.book is not None:
        txn.book.availability_status = "Available"
    db.commit()
    db.refresh(txn)
    return txn


def get_transactions(db: Session) -> List[models.Transaction]:
    return (
        db.query(models.Transaction)
        .order_by(models.Transaction.transaction_id.desc())
        .all()
    )


def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.transaction_id == transaction_id)
        .first()
    )


# ---------- Search ----------
def search_books(db: Session, query: str) -> List[models.Book]:
    """Case-insensitive search across title, author, and category."""
    pattern = f"%{query}%"
    return (
        db.query(models.Book)
        .filter(
            or_(
                models.Book.title.ilike(pattern),
                models.Book.author.ilike(pattern),
                models.Book.category.ilike(pattern),
            )
        )
        .all()
    )


# ---------- Dashboard ----------
def get_dashboard_stats(db: Session) -> schemas.DashboardStats:
    total_books = db.query(models.Book).count()
    borrowed = (
        db.query(models.Book)
        .filter(models.Book.availability_status == "Borrowed")
        .count()
    )
    total_borrowers = db.query(models.Borrower).count()
    active_txns = (
        db.query(models.Transaction)
        .filter(models.Transaction.return_date.is_(None))
        .count()
    )
    return schemas.DashboardStats(
        total_books=total_books,
        available_books=total_books - borrowed,
        borrowed_books=borrowed,
        total_borrowers=total_borrowers,
        active_transactions=active_txns,
    )
