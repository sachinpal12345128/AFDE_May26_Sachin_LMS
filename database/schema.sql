-- Library Management System — Database Schema
-- Target: SQLite (also works with PostgreSQL with minor type tweaks)
-- Generated for reference; the application uses SQLAlchemy to create
-- these tables automatically on first run via Base.metadata.create_all().

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS borrowers;
DROP TABLE IF EXISTS books;

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
