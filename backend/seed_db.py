"""
One-shot seeder — populates library.db with sample books and borrowers.

Run from the backend/ directory after installing requirements:
    python seed_db.py

Safe to re-run: existing rows with the same ISBN / email are skipped.
"""

from database import Base, SessionLocal, engine
import models

BOOKS = [
    ("Clean Code", "Robert C. Martin", "Programming", "9780132350884"),
    ("The Pragmatic Programmer", "Andrew Hunt", "Programming", "9780201616224"),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Programming", "9781449373320"),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "9780262033848"),
    ("Cracking the Coding Interview", "Gayle Laakmann McDowell", "Career", "9780984782857"),
    ("Atomic Habits", "James Clear", "Self-Help", "9780735211292"),
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "History", "9780062316097"),
    ("The Lean Startup", "Eric Ries", "Business", "9780307887894"),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", "9780374533557"),
    ("The Mythical Man-Month", "Fred Brooks", "Programming", "9780201835953"),
    ("Refactoring", "Martin Fowler", "Programming", "9780134757599"),
    ("You Don't Know JS Yet", "Kyle Simpson", "Programming", "9781091210095"),
    ("Deep Work", "Cal Newport", "Self-Help", "9781455586691"),
    ("The Phoenix Project", "Gene Kim", "Business", "9780988262508"),
    ("Site Reliability Engineering", "Betsy Beyer", "Programming", "9781491929124"),
]

BORROWERS = [
    ("Aarav Sharma", "aarav.sharma@example.com", "9876543210"),
    ("Priya Iyer", "priya.iyer@example.com", "9876543211"),
    ("Rahul Verma", "rahul.verma@example.com", "9876543212"),
    ("Ananya Singh", "ananya.singh@example.com", "9876543213"),
    ("Karthik Nair", "karthik.nair@example.com", "9876543214"),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        added_books = 0
        for title, author, category, isbn in BOOKS:
            if not db.query(models.Book).filter_by(isbn=isbn).first():
                db.add(
                    models.Book(
                        title=title,
                        author=author,
                        category=category,
                        isbn=isbn,
                        availability_status="Available",
                    )
                )
                added_books += 1

        added_borrowers = 0
        for name, email, phone in BORROWERS:
            if not db.query(models.Borrower).filter_by(email=email).first():
                db.add(
                    models.Borrower(borrower_name=name, email=email, phone=phone)
                )
                added_borrowers += 1

        db.commit()
        print(f"Seed complete — added {added_books} books, {added_borrowers} borrowers.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
