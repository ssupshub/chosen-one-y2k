@echo off
echo.
echo  chosen-one-y2k :: Starting Backend
echo  ====================================
echo.

cd /d "%~dp0backend"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo  ERROR: Python not found. Install Python 3 from python.org
    pause
    exit /b 1
)

echo  Installing dependencies...
pip install -r requirements.txt --quiet --break-system-packages 2>nul || pip install -r requirements.txt --quiet

echo.
echo  Backend starting at http://localhost:5000
echo  Open index.html in your browser separately.
echo  Press Ctrl+C to stop.
echo.

python app.py
pause
