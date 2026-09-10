@echo off
cd /d "%~dp0"

python -c "import PySide6, wmi, PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [1/2] Installing dependencies ...
    python -m pip install -r requirements.txt pyinstaller
    if errorlevel 1 goto :fail
)

echo [2/2] Building exe ...
python -m PyInstaller --noconfirm --clean DynamicIsland.spec
if errorlevel 1 goto :fail

echo.
echo Done: %~dp0dist\DynamicIsland.exe
pause
exit /b 0

:fail
echo.
echo Build FAILED, see messages above.
pause
exit /b 1
