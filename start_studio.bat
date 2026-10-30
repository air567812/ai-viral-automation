@echo off
title Autonomous AI Viral Reels & YouTube Shorts Studio
cd /d "%~dp0"
echo ======================================================================
echo Starting Autonomous AI Viral Reels & YouTube Shorts Studio Dashboard
echo ======================================================================
echo.
echo Dashboard URL: http://localhost:8000
echo.
set PYTHONPATH=%~dp0
call .venv\Scripts\activate.bat
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
