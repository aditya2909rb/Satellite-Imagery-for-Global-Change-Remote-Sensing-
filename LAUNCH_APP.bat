@echo off
echo 🚀 Satellite Fire Detection System Launcher
echo ===========================================
echo.
echo This will start the application server...
echo.
echo 📍 Server will be available at: http://localhost:8000
echo 🌐 Web UI available at: http://localhost:8000/ui
echo 🔧 API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
pause
echo.
echo Starting server...
echo.
cd /d "%~dp0"
python start_server.py
echo.
echo Server stopped.
pause