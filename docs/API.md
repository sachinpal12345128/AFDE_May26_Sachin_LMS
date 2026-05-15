# API Reference — Library Management System

Base URL: `http://localhost:8000`

All endpoints return JSON. Errors use the standard FastAPI shape:

```json
{ "detail": "Human-readable message" }
```

---

## Health

### `GET /`
Health probe. Returns service banner.

**Response 200**
```json
{
  "status": "ok",
  "service": "Library Management System",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## Dashboard

### `GET /dashboard/stats`
Aggregate counts shown on the dashboard landing page.

**Response 200**
```json
{
  "total_books": 15,
  "available_books": 14,
  "borrowed_books": 1,
  "total_borrowers": 5,
  "active_transactions": 1
}
```

---

## Books

### `GET /books`
List all books.

**Response 200**
```json
[
  {
    "book_id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "category": "Programming",
    "isbn": "9780132350884",
    "availability_status": "Available"
  }
]
```

### `GET /books/{book_id}`
Get a single book.

**Errors:** `404` if not found.

### `POST /books`
Add a book.

**Request**
```json
{
  "title": "Domain-Driven Design",
  "author": "Eric Evans",
  "category": "Programming",
  "isbn": "9780321125217"
}
```

**Response 201** — the created book including `book_id` and
`availability_status: "Available"`.

**Errors:**
- `409` if `isbn` already exists.
- `422` if any required field is missing or fails validation.

### `PUT /books/{book_id}`
Partial update. All fields are optional; only those provided are changed.

**Request**
```json
{ "category": "Software Engineering" }
```

**Errors:** `404` if missing; `409` if `isbn` clashes with another book.

### `DELETE /books/{book_id}`
Delete a book. Returns `204 No Content`.

**Errors:**
- `404` if missing.
- `400` if the book is currently borrowed (must be returned first).

---

## Borrowers

### `GET /borrowers`
List all borrowers.

**Response 200**
```json
[
  {
    "borrower_id": 1,
    "borrower_name": "Aarav Sharma",
    "email": "aarav.sharma@example.com",
    "phone": "9876543210"
  }
]
```

### `GET /borrowers/{borrower_id}`
Get a borrower. `404` if missing.

### `POST /borrowers`
Add a borrower.

**Request**
```json
{
  "borrower_name": "Diya Patel",
  "email": "diya.patel@example.com",
  "phone": "9876543299"
}
```

**Errors:** `409` if email is already in use; `422` on validation failure.

### `PUT /borrowers/{borrower_id}`
Partial update — same rules as `PUT /books/{id}`.

### `DELETE /borrowers/{borrower_id}`
Delete a borrower. `400` if the borrower still has an open (unreturned)
transaction.

---

## Transactions (Borrow / Return)

### `POST /borrow`
Record a borrow. Sets the book's `availability_status` to `Borrowed` and
stamps `borrow_date`.

**Request**
```json
{ "book_id": 1, "borrower_id": 1 }
```

**Response 201**
```json
{
  "transaction_id": 1,
  "book_id": 1,
  "borrower_id": 1,
  "borrow_date": "2026-05-15T08:34:19.815367",
  "return_date": null,
  "book_title": "Clean Code",
  "borrower_name": "Aarav Sharma"
}
```

**Errors:**
- `404` if book or borrower does not exist.
- `400` if the book is not currently `Available`.

### `POST /return`
Record a return. Flips the book back to `Available` and stamps `return_date`.

**Request**
```json
{ "transaction_id": 1 }
```

**Response 200** — same shape as borrow, with `return_date` populated.

**Errors:**
- `404` if transaction not found.
- `400` if the book was already returned.

### `GET /transactions`
List all transactions, most recent first. Each row includes denormalized
`book_title` and `borrower_name` for convenience.

---

## Search

### `GET /search?q={keyword}`
Case-insensitive partial match across `title`, `author`, and `category`.

**Example:** `GET /search?q=programming`

**Response 200** — array of books matching the same shape as `GET /books`.

**Errors:**
- `422` if `q` is missing or empty.

---

## HTTP Status Code Conventions

| Code | When                                             |
|------|--------------------------------------------------|
| 200  | Successful GET/PUT/POST returning a body         |
| 201  | Resource created (POST /books, /borrowers, /borrow) |
| 204  | Resource deleted (DELETE)                        |
| 400  | Business-rule violation (e.g. borrow unavailable)|
| 404  | Resource not found                               |
| 409  | Unique-constraint conflict (duplicate ISBN/email)|
| 422  | Pydantic validation failure                      |
| 500  | Unhandled server error                           |
