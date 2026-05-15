"""Routes for /borrowers — full CRUD over library members."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/borrowers", tags=["Borrowers"])


@router.get("", response_model=List[schemas.BorrowerOut])
def list_borrowers(db: Session = Depends(get_db)):
    return crud.get_borrowers(db)


@router.get("/{borrower_id}", response_model=schemas.BorrowerOut)
def get_borrower(borrower_id: int, db: Session = Depends(get_db)):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Borrower not found")
    return borrower


@router.post(
    "", response_model=schemas.BorrowerOut, status_code=status.HTTP_201_CREATED
)
def create_borrower(payload: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    if crud.get_borrower_by_email(db, payload.email):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"A borrower with email {payload.email} already exists",
        )
    return crud.create_borrower(db, payload)


@router.put("/{borrower_id}", response_model=schemas.BorrowerOut)
def update_borrower(
    borrower_id: int,
    payload: schemas.BorrowerUpdate,
    db: Session = Depends(get_db),
):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Borrower not found")
    if payload.email and payload.email != borrower.email:
        clash = crud.get_borrower_by_email(db, payload.email)
        if clash:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Email {payload.email} already used by another borrower",
            )
    return crud.update_borrower(db, borrower, payload)


@router.delete("/{borrower_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_borrower(borrower_id: int, db: Session = Depends(get_db)):
    borrower = crud.get_borrower(db, borrower_id)
    if not borrower:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Borrower not found")
    # Guard against deleting a borrower who has unreturned books
    open_txn = next(
        (t for t in borrower.transactions if t.return_date is None), None
    )
    if open_txn:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Borrower has unreturned books; cannot delete",
        )
    crud.delete_borrower(db, borrower)
    return None
