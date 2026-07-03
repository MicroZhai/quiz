@echo off
title 热处理刷题 - 推送 GitHub
cd /d "%~dp0"

echo.
echo ========================================
echo    Re Re Chu Li - Push to GitHub
echo ========================================
echo.
echo Current dir: %cd%
echo.

:: Check git availability
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] git command not found!
    echo Please install Git and add it to PATH.
    echo.
    pause
    exit /b 1
)

echo [Git version]
git --version
echo.

:: Check if this is a git repo
git status >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Not a git repository!
    echo.
    pause
    exit /b 1
)

:: Check for uncommitted changes
git diff --quiet
set diff_exit=%errorlevel%
git diff --cached --quiet
set cached_exit=%errorlevel%

:: If both are 0, nothing to commit (0 means no diff)
if %diff_exit% equ 0 if %cached_exit% equ 0 (
    echo [INFO] No uncommitted changes.
    goto :push
)

:: Otherwise, commit
echo [INFO] Changes detected, committing...
git add -A
if %errorlevel% neq 0 (
    echo [ERROR] git add failed!
    pause
    exit /b 1
)

set commit_msg=Update: %date% %time%
git commit -m "%commit_msg%"
if %errorlevel% neq 0 (
    echo [ERROR] git commit failed!
    pause
    exit /b 1
)
echo [OK] Commit done.

:push
echo.
echo [INFO] Pushing master to main...
git push origin master:main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Pushed to GitHub.
    echo   https://microzhai.github.io/quiz/
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   FAILED! Check network and remote repo.
    echo ========================================
)

echo.
pause
