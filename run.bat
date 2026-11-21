@echo off

echo Activating virtual environment...

call venv\Scripts\activate.bat

echo Virtual environment activated!

python backend\main.py

pause