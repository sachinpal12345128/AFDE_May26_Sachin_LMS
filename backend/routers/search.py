"""Search endpoint — case-insensitive match across title / author / category."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(tags=["Search"])


@router.get("/search", response_model=List[schemas.BookOut])
def search(
    q: str = Query(..., min_length=1, description="Search keyword"),
    db: Session = Depends(get_db),
):
    if not q.strip():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Search query cannot be empty"
        )
    return crud.search_books(db, q.strip())
