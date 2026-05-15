# Quick Setup — TL;DR

Two terminals, one for backend, one for frontend.

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer (for Vite)
- Git

## Terminal 1 — Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux

pip install -r ../requirements.txt
python seed_db.py                # one-time seed
uvicorn main:app --reload --port 8000
```

Verify: open <http://localhost:8000/docs>

## Terminal 2 — Frontend

```bash
cd frontend
npm install
npm run dev
```

Verify: open <http://localhost:5173>

## Common Issues

- **CORS errors in browser**: Make sure backend is on port `8000` and frontend
  on `5173`. The default config allows all origins for development.
- **`sqlite3.OperationalError: disk I/O error`** when running on a network
  drive or some virtualized filesystems — move the project to a local disk.
- **Port already in use**: change `--port 8000` (backend) or the `server.port`
  in `vite.config.js` (frontend) and update `VITE_API_BASE` accordingly.
- **Reset everything**: delete `backend/library.db` and re-run `seed_db.py`.

## Useful Endpoints During Demo

- Swagger UI: <http://localhost:8000/docs>
- Health: <http://localhost:8000/>
- Dashboard stats: <http://localhost:8000/dashboard/stats>
