@echo off
title Autonomous AI Reels - Run Content Cycle
cd /d "%~dp0"
echo ======================================================================
echo Triggering Autonomous AI Content Pipeline
echo ======================================================================
echo.
set PYTHONPATH=%~dp0
call .venv\Scripts\activate.bat
python backend/cli.py --niche "sci-fi and mystery" --auto-publish --duration 45
pause
