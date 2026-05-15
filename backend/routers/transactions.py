"""Borrow / return workflows and transaction history."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(tags=["Transactions"])


def _to_out(t) -> schemas.TransactionOut:
    """Flatten the joined book/borrower names for nicer API output."""
    return schemas.TransactionOut(
        transaction_id=t.transaction_id,
        book_id=t.book_id,
        borrower_id=t.borrower_id,
        borrow_date=t.borrow_date,
        return_date=t.return_date,
        book_title=t.book.title if t.book else None,
        borrower_name=t.borrower.borrower_name if t.borrower else None,
    )


@router.post(
    "/borrow",
    response_model=schemas.TransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def borrow(payload: schemas.BorrowRequest, db: Session = Depends(get_db)):
    book = crud.get_book(db, payload.book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    borrower = crud.get_borrower(db, payload.borrower_id)
    if not borrower:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Borrower not found")
    if book.availability_status != "Available":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Book is not currently available",
        )
    txn = crud.borrow_book(db, book, borrower)
    return _to_out(txn)


@router.post("/return", response_model=schemas.TransactionOut)
def return_(payload: schemas.ReturnRequest, db: Session = Depends(get_db)):
    txn = crud.get_transaction(db, payload.transaction_id)
    if not txn:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if txn.return_date is not None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Book already returned"
        )
    txn = crud.return_book(db, txn)
    return _to_out(txn)


@router.get("/transactions", response_model=List[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return [_to_out(t) for t in crud.get_transactions(db)]
