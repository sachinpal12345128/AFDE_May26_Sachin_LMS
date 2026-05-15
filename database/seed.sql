-- Seed data for the Library Management System
-- Run after schema.sql

INSERT INTO books (title, author, category, isbn, availability_status) VALUES
  ('Clean Code', 'Robert C. Martin', 'Programming', '9780132350884', 'Available'),
  ('The Pragmatic Programmer', 'Andrew Hunt', 'Programming', '9780201616224', 'Available'),
  ('Designing Data-Intensive Applications', 'Martin Kleppmann', 'Programming', '9781449373320', 'Available'),
  ('Introduction to Algorithms', 'Thomas H. Cormen', 'Computer Science', '9780262033848', 'Available'),
  ('Cracking the Coding Interview', 'Gayle Laakmann McDowell', 'Career', '9780984782857', 'Available'),
  ('Atomic Habits', 'James Clear', 'Self-Help', '9780735211292', 'Available'),
  ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'History', '9780062316097', 'Available'),
  ('The Lean Startup', 'Eric Ries', 'Business', '9780307887894', 'Available'),
  ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', '9780374533557', 'Available'),
  ('The Mythical Man-Month', 'Fred Brooks', 'Programming', '9780201835953', 'Available'),
  ('Refactoring', 'Martin Fowler', 'Programming', '9780134757599', 'Available'),
  ('You Don''t Know JS Yet', 'Kyle Simpson', 'Programming', '9781091210095', 'Available'),
  ('Deep Work', 'Cal Newport', 'Self-Help', '9781455586691', 'Available'),
  ('The Phoenix Project', 'Gene Kim', 'Business', '9780988262508', 'Available'),
  ('Site Reliability Engineering', 'Betsy Beyer', 'Programming', '9781491929124', 'Available');

INSERT INTO borrowers (borrower_name, email, phone) VALUES
  ('Aarav Sharma',  'aarav.sharma@example.com',  '9876543210'),
  ('Priya Iyer',    'priya.iyer@example.com',    '9876543211'),
  ('Rahul Verma',   'rahul.verma@example.com',   '9876543212'),
  ('Ananya Singh',  'ananya.singh@example.com',  '9876543213'),
  ('Karthik Nair',  'karthik.nair@example.com',  '9876543214');
