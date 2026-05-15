"""
Database configuration for the Library Management System.

Uses SQLite for Phase 1 (zero-config, file-based). The DB file lives
alongside the backend code at backend/library.db. If you want to switch
to PostgreSQL later, just change DATABASE_URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Phase 1: SQLite. To switch to PostgreSQL:
#   DATABASE_URL = "postgresql+psycopg2://user:pass@localhost:5432/library"
DATABASE_URL = "sqlite:///./library.db"

# check_same_thread=False is required for SQLite when used with FastAPI's
# threadpool. Safe here because each request gets its own Session.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
