@echo off
cd /d "%~dp0"
echo 🚀 Starting Satellite Fire Detection System...
echo 📍 Server will be available at: http://localhost:8000
echo 🌐 Web UI available at: http://localhost:8000/ui
echo 🔧 API documentation at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.
python start_server.py
pause
