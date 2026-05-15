"""
Pydantic schemas — define the shape of request and response bodies.

Pattern used for each entity:
  - <Entity>Base    : fields shared by create / update / response
  - <Entity>Create  : payload for POST
  - <Entity>Update  : payload for PUT  (all fields optional)
  - <Entity>Out     : response model (includes DB-generated IDs and dates)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Book ----------
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    category: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=5, max_length=20)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=150)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, min_length=5, max_length=20)
    availability_status: Optional[str] = None


class BookOut(BookBase):
    book_id: int
    availability_status: str
    model_config = ConfigDict(from_attributes=True)


# ---------- Borrower ----------
class BorrowerBase(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(..., min_length=5, max_length=20)


class BorrowerCreate(BorrowerBase):
    pass


class BorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)


class BorrowerOut(BorrowerBase):
    borrower_id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Transaction ----------
class BorrowRequest(BaseModel):
    book_id: int
    borrower_id: int


class ReturnRequest(BaseModel):
    transaction_id: int


class TransactionOut(BaseModel):
    transaction_id: int
    book_id: int
    borrower_id: int
    borrow_date: datetime
    return_date: Optional[datetime]
    # Joined details for nicer UI display
    book_title: Optional[str] = None
    borrower_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---------- Dashboard stats ----------
class DashboardStats(BaseModel):
    total_books: int
    available_books: int
    borrowed_books: int
    total_borrowers: int
    active_transactions: int
