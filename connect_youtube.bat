@echo off
title 1-Click Connect YouTube Channel
cd /d "%~dp0"
echo ======================================================================
echo 1-Click YouTube Channel Connector
echo ======================================================================
echo.
call .venv\Scripts\activate.bat
python connect_youtube.py
pause
