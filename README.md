# Food Inventory App

A desktop-first inventory management app with a PyQt5 GUI, a FastAPI REST backend, a React (Vite) frontend, and an optional Electron shell.

## Overview
- **Desktop GUI**: PyQt5 app (`app.py`) to manage products, with search, inline alerts, and CSV export.
- **Backend API**: FastAPI service (`backend/api.py`) exposing products, sales, and ingredients endpoints backed by SQLite.
- **Database**: SQLite file (`backend/inventory.db`). Schema managed in `backend/database.py`.
- **Web Frontend**: React + Vite + Tailwind (`/frontend`).
- **Electron Shell**: Optional wrapper to run the web frontend as a desktop app (`/electron`).

## Project Structure
- `app.py` — PyQt5 desktop application.
- `backend/` — FastAPI app (`api.py`) and SQLite persistence (`database.py`).
- `frontend/` — Vite + React UI.
- `electron/` — Electron wrapper for the frontend.
- `icon.jpg` — App icon for the PyQt5 window.
- `main.py` — One-off helper script to seed products (optional).

## Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend/electron)
- Windows, macOS, or Linux

## Setup (Python)
```bash
# from project root
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

## Run the Desktop GUI (PyQt5)
```bash
# from project root (so that `backend.*` imports work)
python app.py
```
Notes:
- The SQLite database is created automatically on first use via `backend/database.py`.
- Inventory export saves a timestamped CSV (e.g., `inventory_export_YYYYMMDD_HHMMSS.csv`).

## Run the API Server (FastAPI)
Option A (recommended): run from the `backend` folder so relative imports like `from database import ...` work.
```bash
# terminal 1
cd backend
uvicorn api:app --reload --host 127.0.0.1 --port 8000
```
Option B: run from project root by setting the app dir.
```bash
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```
- Open docs at http://127.0.0.1:8000/docs

## Run the Web Frontend (React + Vite)
```bash
# from frontend folder
cd frontend
npm install
npm run dev
```
- Defaults to http://127.0.0.1:5173
- If the UI needs to call the API, ensure the API server is running on http://127.0.0.1:8000

## Run the Electron Shell (optional)
```bash
# from electron folder
cd electron
npm install
npm run dev
```
- Set `ELECTRON_DEV=1` to load your frontend dev server in development (already in the `dev` script).

## Database
- File: `backend/inventory.db`
- Schema migration/creation occurs in `backend/database.py` (`init_db`).
- You can seed initial data using `main.py`:
```bash
python main.py
```

## Troubleshooting
- PyQt5 issues on Linux: ensure `qt5` libraries are present from your distro.
- Import errors when running the API: run uvicorn from the `backend` directory (`uvicorn api:app`) or use `backend.api:app` from project root.
- CSV export permission errors: the export filename includes a timestamp to avoid conflicts.

## Licensing
- Provide your preferred license here.
