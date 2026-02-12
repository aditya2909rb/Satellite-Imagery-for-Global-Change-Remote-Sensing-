@echo off
REM Quick verification script to check if the app can start

echo.
echo ============================================================================
echo          SATELLITE FIRE DETECTION API - VERIFICATION SCRIPT
echo ============================================================================
echo.

REM Check Python
echo Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python NOT FOUND
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python found

REM Check FastAPI
echo.
echo Checking FastAPI...
python -c "import fastapi; print('✓ FastAPI', fastapi.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠ FastAPI not installed. Will install when running RUN_APP.bat
)

REM Check uvicorn
echo Checking uvicorn...
python -c "import uvicorn; print('✓ uvicorn', uvicorn.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠ uvicorn not installed. Will install when running RUN_APP.bat
)

REM Check aiohttp
echo Checking aiohttp...
python -c "import aiohttp; print('✓ aiohttp', aiohttp.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠ aiohttp not installed. Will install when running RUN_APP.bat
)

REM Check numpy
echo Checking numpy...
python -c "import numpy; print('✓ numpy', numpy.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠ numpy not installed. Will install when running RUN_APP.bat
)

REM Check imports
echo.
echo Checking app imports...
cd /d "%~dp0satellite-detection-project"
python -c "import sys; sys.path.insert(0, 'src'); from api.main import app; print('✓ App imports successful!')" 2>nul
if errorlevel 1 (
    echo ❌ App imports FAILED
    echo.
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo.
echo ✓ ✓ ✓ ALL CHECKS PASSED ✓ ✓ ✓
echo.
echo You can now run the app with:
echo   RUN_APP.bat
echo.
echo Or start it manually with:
echo   python start_server.py
echo.
cd /d "%~dp0"
pause
