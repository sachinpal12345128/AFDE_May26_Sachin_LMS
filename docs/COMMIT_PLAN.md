# Suggested 3-Day Commit Plan

The evaluation rewards **incremental daily commits**, not a single bulk
upload. Here's a recommended sequence that lines up with the project's
3-day timeline.

> The whole project is already built. The point of this plan is to commit it
> in realistic, dated slices rather than one big push.

## Day 1 — Foundation & Backend

1. `chore: initialize repository with project structure and gitignore`
2. `feat(db): add SQLite schema and seed data for books, borrowers, transactions`
3. `feat(backend): scaffold FastAPI app with database session factory`
4. `feat(models): add SQLAlchemy models for Book, Borrower, Transaction`
5. `feat(schemas): add Pydantic schemas for request and response validation`
6. `feat(crud): implement CRUD helpers for books and borrowers`
7. `feat(api): add /books routes with full CRUD and 409 conflict handling`
8. `feat(api): add /borrowers routes with validation and delete guard`

## Day 2 — Borrow/Return + Frontend

9.  `feat(api): add /borrow, /return, /transactions endpoints`
10. `feat(api): add /search endpoint with case-insensitive matching`
11. `feat(api): add /dashboard/stats aggregate endpoint`
12. `chore(frontend): scaffold Vite + React project`
13. `feat(frontend): add axios api client and global stylesheet`
14. `feat(frontend): implement Dashboard page with live stats`
15. `feat(frontend): implement Books page with create/edit modal`
16. `feat(frontend): implement Borrowers page with form validation`

## Day 3 — Polish & Submit

17. `feat(frontend): implement Transactions page with borrow/return workflow`
18. `feat(frontend): implement Search page with category filter`
19. `fix(api): block deletion of borrowed books and borrowers with open loans`
20. `docs: write README, API.md, SETUP.md`
21. `chore: add Postman collection`
22. `chore: add UI screenshots`
23. `docs: final README polish and submission notes`

## Commit Hygiene Tips

- Use the conventional-commits prefixes (`feat:`, `fix:`, `docs:`,
  `chore:`, `refactor:`) — that earns easy "GitHub practices" points.
- Keep each commit focused on one logical change.
- Push at least twice a day — once before lunch, once at end of day.
- The evaluator looks at commit *cadence*, not just the final state.
