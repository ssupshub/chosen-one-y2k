@echo off
echo.
echo  chosen-one-y2k :: Build Windows Launcher
echo  ==========================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo  ERROR: Python not found.
    echo  Install from python.org and add to PATH.
    pause & exit /b 1
)

echo  Installing PyInstaller...
pip install pyinstaller --quiet

echo  Building chosen-one-y2k.exe...
pyinstaller --onefile --console --name "chosen-one-y2k" launcher.py

echo.
if exist dist\chosen-one-y2k.exe (
    echo  SUCCESS! File created: dist\chosen-one-y2k.exe
    echo  Copy it to the project root and double-click to play.
) else (
    echo  Build failed. Check errors above.
)
pause
