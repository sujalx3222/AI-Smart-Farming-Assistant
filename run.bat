@echo off
setlocal
set ROOT_DIR=%~dp0

echo ==========================================
echo    Smart Agriculture System - Startup
echo ==========================================

:: 1. Backend Check
echo [1/3] Checking Backend...
cd /d "%ROOT_DIR%backend"
if not exist ".venv" (
    echo [!] Warning: .venv not found. Creating one...
    python -m venv .venv
    echo Installing base requirements...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
)

:: 2. Frontend Check
echo.
echo [2/3] Checking Frontend...
cd /d "%ROOT_DIR%frontend"
if not exist "node_modules" (
    echo [!] Warning: node_modules not found. Installing...
    call npm install
)

:: 3. Launch Services
echo.
echo [3/3] Launching Servers...

:: Launch Backend on Port 8000
start "Django Backend" cmd /k "cd /d "%ROOT_DIR%backend" && .\.venv\Scripts\activate && python manage.py runserver 8000"

:: Launch Frontend
start "React Frontend" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

echo.
echo ==========================================
echo    SYSTEM INITIALIZED - Ports: 8000, 5173
echo ==========================================
echo The Backend (8000) and Frontend (5173) are starting in new windows.
pause

