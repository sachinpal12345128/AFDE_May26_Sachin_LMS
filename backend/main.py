"""
Library Management System — FastAPI entry point.

Run with:
    uvicorn main:app --reload --port 8000

Swagger docs are available at http://localhost:8000/docs once the
server is running.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routers import books, borrowers, dashboard, search, transactions

# Create tables on startup (idempotent — only creates if missing)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System API",
    description=(
        "REST API for the LMS capstone — manage books, borrowers, "
        "and borrow/return transactions."
    ),
    version="1.0.0",
)

# CORS — open during development so the Vite dev server (port 5173)
# can talk to the API. Tighten this in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    """Health check / API banner."""
    return {
        "status": "ok",
        "service": "Library Management System",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Mount all feature routers
app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(search.router)
app.include_router(dashboard.router)
