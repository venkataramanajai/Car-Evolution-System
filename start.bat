@echo off
echo ===================================================
echo     Starting Car Evolution System...
echo ===================================================

echo [1/2] Starting FastAPI Backend (Port 8000)...
start "FastAPI Backend" cmd /k ".\venv\Scripts\activate && uvicorn backend.main:app --reload"

echo [2/2] Starting React Frontend (Port 5173)...
start "React Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both services are starting in separate windows.
echo - Backend API: http://127.0.0.1:8000
echo - Frontend UI: http://localhost:5173
echo.
pause
