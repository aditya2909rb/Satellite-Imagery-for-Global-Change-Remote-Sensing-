@echo off
REM Satellite Detection API Server Launcher
REM This script checks all dependencies and starts the server

echo.
echo ============================================================================
echo         SATELLITE FIRE DETECTION API - SERVER LAUNCHER
echo ============================================================================
echo.

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Navigate to the satellite-detection-project directory
cd /d "%~dp0satellite-detection-project"

echo Checking Python version...
python --version
echo.

echo Checking required dependencies...
python -c "import fastapi; import uvicorn; import aiohttp; print('✓ All required packages found!')" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================================
echo Starting Satellite Fire Detection API Server...
echo ============================================================================
echo.
echo 📍 API Server:     http://localhost:8000
echo 📚 API Docs:       http://localhost:8000/docs
echo 🌐 Web UI:         http://localhost:8000/ui
echo.
echo Available endpoints:
echo   GET  /health           - Health check
echo   GET  /satellites       - List satellites
echo   GET  /status           - System status
echo   POST /detect/smoke     - Detect smoke/fires
echo   POST /detect/dust      - Detect dust
echo.
echo Press CTRL+C to stop the server
echo ============================================================================
echo.

REM Run the server using start_server.py
python start_server.py

REM If the server stopped, show a message
if errorlevel 1 (
    echo.
    echo An error occurred. Check the output above.
    pause
)
