@echo off
echo ==========================================
echo Starting WhatsApp Catalog AI (Local Mode)
echo ==========================================

:: 1. Force use local SQLite database path (override .env for this session)
set DATABASE_URL=sqlite:///./catalog_db.sqlite

:: 2. Install dependencies
echo [Step 1/3] Installing/Updating dependencies...
pip install -r requirements.txt

:: 3. Seed the database
echo [Step 2/3] Seeding database with dummy data...
python seed.py

:: 4. Start the server
echo [Step 3/3] Starting FastAPI server on http://127.0.0.1:8000
echo Ctrl+C to stop the server.
:: Menggunakan 'python -m uvicorn' agar lebih stabil di Windows
python -m uvicorn main:app --reload --port 8000

pause
