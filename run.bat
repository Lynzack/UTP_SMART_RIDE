@echo off
setlocal

echo ======================================
echo       UTP SMART RIDE SYSTEM
echo ======================================
echo.

if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Checking Python dependencies...
python -m pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing project requirements...
    python -m pip install -r requirements.txt
)

echo.
echo Starting Smart Ride web server...
python backend\server.py

pause
