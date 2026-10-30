@echo off
title Push Autonomous AI Reels to GitHub
cd /d "%~dp0"
echo ======================================================================
echo Pushing Autonomous AI Reels System to GitHub
echo ======================================================================
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/viral-reels.git): "
if "%REPO_URL%"=="" (
    echo Error: Repository URL cannot be empty!
    pause
    exit /b 1
)

git init
git add .
git commit -m "feat: complete autonomous AI viral reels platform with GitHub Actions"
git branch -M main
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ======================================================================
echo Push complete!
echo Navigate to the 'Actions' tab in your GitHub repository to see the
echo autonomous 6-hour cloud scheduler and CI pipeline running.
echo ======================================================================
pause
