@echo off
echo.
echo [1/5] Checking Python Version...
python --version
python -c "import platform; print('Architecture:', platform.architecture()[0])"

echo.
echo [2/5] Deleting old virtual environment...
if exist .venv rmdir /s /q .venv

echo.
echo [3/5] Creating fresh virtual environment...
python -m venv .venv

echo.
echo [4/5] Installing core dependencies...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [5/5] Starting Django server...
.\.venv\Scripts\python.exe manage.py runserver
