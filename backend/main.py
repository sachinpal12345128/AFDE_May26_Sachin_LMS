"""
Library Management System - FastAPI entry point.

Run with:
    uvicorn main:app --reload --port 8000

Swagger docs are available at http://localhost:8000/docs once the
server is running.

Phase 2 adds the /analytics/* router, which serves data produced by the
Pandas ETL pipeline (see etl/run_etl.py).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routers import analytics, books, borrowers, dashboard, search, transactions

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System API",
    description=(
        "REST API for the LMS capstone. Phase 1 covers books, borrowers, "
        "and borrow/return transactions. Phase 2 adds /analytics/* endpoints "
        "backed by the Pandas ETL pipeline (see etl/run_etl.py)."
    ),
    version="2.0.0",
)

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
        "version": "2.0.0",
        "phase": "2",
        "docs": "/docs",
    }


app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(search.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)  # Phase 2 - ETL-backed analytics
