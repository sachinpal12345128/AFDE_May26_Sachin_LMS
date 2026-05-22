-- Library Management System - Database Schema (Phase 2)
-- Target: SQLite (also works with PostgreSQL with minor type tweaks)
-- The application creates these tables automatically on first run via
-- Base.metadata.create_all(); this file is provided for reference and
-- for DBAs who prefer to provision the schema manually.

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS borrowers;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS analytics_most_borrowed;
DROP TABLE IF EXISTS analytics_category_borrowing;
DROP TABLE IF EXISTS analytics_monthly_trend;
DROP TABLE IF EXISTS analytics_overdue;
DROP TABLE IF EXISTS etl_run_log;

-- ---------- Books ----------
CREATE TABLE books (
    book_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title                VARCHAR(200) NOT NULL,
    author               VARCHAR(150) NOT NULL,
    category             VARCHAR(100) NOT NULL,
    isbn                 VARCHAR(20)  NOT NULL UNIQUE,
    availability_status  VARCHAR(20)  NOT NULL DEFAULT 'Available'
                         CHECK (availability_status IN ('Available', 'Borrowed'))
);

CREATE INDEX idx_books_title    ON books(title);
CREATE INDEX idx_books_author   ON books(author);
CREATE INDEX idx_books_category ON books(category);

-- ---------- Borrowers ----------
CREATE TABLE borrowers (
    borrower_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    borrower_name  VARCHAR(150) NOT NULL,
    email          VARCHAR(150) NOT NULL UNIQUE,
    phone          VARCHAR(20)  NOT NULL
);

CREATE INDEX idx_borrowers_email ON borrowers(email);

-- ---------- Transactions ----------
CREATE TABLE transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id         INTEGER NOT NULL,
    borrower_id     INTEGER NOT NULL,
    borrow_date     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    return_date     DATETIME,
    FOREIGN KEY (book_id)     REFERENCES books(book_id),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
);

CREATE INDEX idx_txn_book     ON transactions(book_id);
CREATE INDEX idx_txn_borrower ON transactions(borrower_id);

-- =====================================================================
-- Phase 2 - Analytics / Reporting tables
-- Populated by the ETL pipeline (etl/run_etl.py) using
-- pandas.DataFrame.to_sql(..., if_exists='replace'), so the DDL below
-- is documentation only -- the ETL recreates them on each run.
-- =====================================================================

-- Most borrowed books, sorted by borrow_count
CREATE TABLE analytics_most_borrowed (
    book_id       INTEGER,
    title         TEXT,
    author        TEXT,
    category      TEXT,
    borrow_count  INTEGER
);

-- Category-wise borrowing
CREATE TABLE analytics_category_borrowing (
    category      TEXT,
    borrow_count  INTEGER
);

-- Monthly borrowing trend (month is YYYY-MM)
CREATE TABLE analytics_monthly_trend (
    month         TEXT,
    borrow_count  INTEGER
);

-- Overdue transactions (loan_days > 14)
CREATE TABLE analytics_overdue (
    transaction_id  INTEGER,
    book_id         INTEGER,
    title           TEXT,
    borrower_id     INTEGER,
    borrower_name   TEXT,
    borrow_date     DATETIME,
    return_date     DATETIME,
    loan_days       INTEGER,
    is_returned     INTEGER
);

-- ETL run audit log
CREATE TABLE etl_run_log (
    run_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at              DATETIME NOT NULL,
    raw_books           INTEGER,
    raw_borrowers       INTEGER,
    raw_transactions    INTEGER,
    clean_books         INTEGER,
    clean_borrowers     INTEGER,
    clean_transactions  INTEGER,
    notes               TEXT
);
