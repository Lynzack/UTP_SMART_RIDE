@echo off

echo ======================================
echo       UTP SMART RIDE SYSTEM
echo ======================================

echo.
echo Activating virtual environment...

call venv\Scripts\activate.bat

echo.
echo Checking Flask installation...

python -m pip show flask >nul 2>&1

if errorlevel 1 (
    echo Flask not found. Installing Flask...
    python -m pip install flask
)

echo.
echo Starting SmartRide web server...

python backend\server.py

pause