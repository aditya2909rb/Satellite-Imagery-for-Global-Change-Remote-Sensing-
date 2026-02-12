@echo off
cd /d "g:\data science p2\satellite-detection-project\src\api"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
