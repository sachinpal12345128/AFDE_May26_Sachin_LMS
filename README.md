# Library Management System — Phase 1

**Capstone:** `AFDE_Apr26_Sachin_LMS`
**Stack:** React (Vite) · FastAPI · SQLite

A full-stack web application that digitizes core library operations — managing
books, borrowers, and borrow/return transactions — with a clean REST API and a
responsive single-page frontend.

---

## 1. Project Overview

Libraries in schools, training institutes and small organizations often rely on
notebooks and spreadsheets to track inventory and lending, which leads to lost
records, missing books, and no visibility into borrowing history. This project
replaces that workflow with a centralized web application built around a single
source of truth (a relational database) and a REST API.

Phase 1 focuses on the foundational CRUD platform; later phases can layer in
authentication, analytics, recommendations, and semantic search.

## 2. Features Implemented

- **Books** — create, read, update, delete; filter; availability tracking
- **Borrowers** — full CRUD with email/phone validation
- **Borrow / Return** — atomic workflow that flips `availability_status` and
  records timestamps in a `transactions` table
- **Search** — case-insensitive across title, author, and category
- **Dashboard** — live counts of total / available / borrowed books, borrowers,
  open loans, plus the five most recent transactions
- **Validation & error handling** — Pydantic on the server, inline error
  feedback in every form on the client
- **Responsive UI** — works on phones, tablets and desktops with no JS frameworks
  beyond React Router

## 3. Technology Stack

| Layer        | Technology                              |
|--------------|------------------------------------------|
| Frontend     | React 18, React Router, Axios, Vite     |
| Styling      | Plain CSS (no Tailwind/MUI)             |
| Backend      | Python 3.10+, FastAPI, SQLAlchemy 2     |
| Database     | SQLite (file-based, zero-config)        |
| API testing  | Postman / curl                          |
| Version ctrl | Git + GitHub                            |

## 4. Project Structure

```
AFDE_Apr26_Sachin_LMS/
├── backend/
│   ├── main.py              # FastAPI app & router wiring
│   ├── database.py          # SQLAlchemy engine + session factory
│   ├── models.py            # ORM models: Book, Borrower, Transaction
│   ├── schemas.py           # Pydantic request/response models
│   ├── crud.py              # DB operations (pure functions on a Session)
│   ├── seed_db.py           # Idempotent seed script
│   └── routers/
│       ├── books.py
│       ├── borrowers.py
│       ├── transactions.py  # /borrow, /return, /transactions
│       ├── search.py
│       └── dashboard.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx          # Router + layout shell
│       ├── api.js           # Axios client wrapping all endpoints
│       ├── styles/global.css
│       ├── components/      # Navbar, Modal
│       └── pages/           # Dashboard, Books, Borrowers, Transactions, Search
├── database/
│   ├── schema.sql           # Plain-SQL schema for reference / PostgreSQL port
│   └── seed.sql             # Plain-SQL seed data
├── docs/
│   └── API.md               # Full endpoint reference with examples
├── screenshots/             # UI and Postman screenshots (added during demo)
├── requirements.txt
├── .gitignore
└── README.md
```

## 5. Setup Instructions

### 5.1 Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r ../requirements.txt
python seed_db.py            # creates library.db with 15 books + 5 borrowers
uvicorn main:app --reload --port 8000
```

The API will be live at **http://localhost:8000** and Swagger UI at
**http://localhost:8000/docs**.

### 5.2 Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will start the dev server at **http://localhost:5173**. CORS is already
configured on the backend, so the two talk to each other out of the box.

### 5.3 Database

The default DB is `backend/library.db`, created automatically the first time
the server (or `seed_db.py`) runs. To reset:

```bash
rm backend/library.db
python seed_db.py
```

To switch to PostgreSQL, change `DATABASE_URL` in `backend/database.py`. The
plain SQL in `database/schema.sql` and `database/seed.sql` is provided for
DBAs who prefer to provision the schema manually.

## 6. API Summary

Base URL: `http://localhost:8000`

| Method  | Endpoint              | Description                       |
|---------|-----------------------|-----------------------------------|
| GET     | `/`                   | Health check                      |
| GET     | `/dashboard/stats`    | Aggregate counts for the dashboard|
| GET     | `/books`              | List all books                    |
| GET     | `/books/{id}`         | Get a book by ID                  |
| POST    | `/books`              | Add a new book                    |
| PUT     | `/books/{id}`         | Update a book                     |
| DELETE  | `/books/{id}`         | Delete a book                     |
| GET     | `/borrowers`          | List borrowers                    |
| GET     | `/borrowers/{id}`     | Get a borrower by ID              |
| POST    | `/borrowers`          | Add a borrower                    |
| PUT     | `/borrowers/{id}`     | Update a borrower                 |
| DELETE  | `/borrowers/{id}`     | Delete a borrower                 |
| POST    | `/borrow`             | Borrow a book                     |
| POST    | `/return`             | Return a previously borrowed book |
| GET     | `/transactions`       | List all transactions             |
| GET     | `/search?q=...`       | Search books                      |

Full request / response samples live in [`docs/API.md`](docs/API.md).

## 7. Example Requests

```bash
# List books
curl http://localhost:8000/books

# Add a book
curl -X POST http://localhost:8000/books \
     -H "Content-Type: application/json" \
     -d '{"title":"Domain-Driven Design","author":"Eric Evans","category":"Programming","isbn":"9780321125217"}'

# Borrow
curl -X POST http://localhost:8000/borrow \
     -H "Content-Type: application/json" \
     -d '{"book_id":1,"borrower_id":1}'

# Return
curl -X POST http://localhost:8000/return \
     -H "Content-Type: application/json" \
     -d '{"transaction_id":1}'

# Search
curl "http://localhost:8000/search?q=programming"
```

## 8. Screenshots

UI and Postman screenshots are stored in the `screenshots/` folder:

- `dashboard.png` — Dashboard with live stats
- `books.png` — Books listing + create modal
- `borrowers.png` — Borrowers management
- `transactions.png` — Borrow / return workflow
- `search.png` — Search results
- `swagger.png` — FastAPI auto-generated docs
- `postman.png` — API test in Postman

## 9. Out of Scope (Phase 1)

Per the project requirement document, the following are intentionally deferred:

- Authentication / authorization
- Notifications and reminders
- Late-return fine calculation
- AI/ML, recommendations, semantic search
- Cloud deployment

## 10. License & Attribution

Capstone submission for FDE training — Phase 1. Free to reuse for educational
purposes.
