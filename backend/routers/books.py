"""Routes for /books — full CRUD over the catalog."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=List[schemas.BookOut])
def list_books(db: Session = Depends(get_db)):
    return crud.get_books(db)


@router.get("/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("", response_model=schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    if crud.get_book_by_isbn(db, payload.isbn):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"A book with ISBN {payload.isbn} already exists",
        )
    return crud.create_book(db, payload)


@router.put("/{book_id}", response_model=schemas.BookOut)
def update_book(
    book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)
):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    if payload.isbn and payload.isbn != book.isbn:
        clash = crud.get_book_by_isbn(db, payload.isbn)
        if clash:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"ISBN {payload.isbn} already used by another book",
            )
    return crud.update_book(db, book, payload)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.availability_status == "Borrowed":
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a book that is currently borrowed",
        )
    crud.delete_book(db, book)
    return None
