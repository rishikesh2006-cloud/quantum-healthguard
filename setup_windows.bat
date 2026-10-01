@echo off
title Quantum HealthGuard — Setup
color 0B
echo ================================================
echo    QUANTUM HEALTHGUARD — First-Time Setup
echo    Windows Setup Script
echo ================================================
echo.

:: ── Check Python ──────────────────────────────────────────────────
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python found:
python --version

:: ── Create Virtual Environment ────────────────────────────────────
echo.
echo [1/4] Creating virtual environment...
IF EXIST ".venv" (
    echo [SKIP] .venv already exists.
) ELSE (
    python -m venv .venv
    echo [OK] Virtual environment created.
)

:: ── Install Dependencies ──────────────────────────────────────────
echo.
echo [2/4] Installing dependencies (this may take 2-5 minutes)...
.venv\Scripts\pip install --upgrade pip --quiet
.venv\Scripts\pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo [ERROR] Package installation failed. Check your internet connection.
    pause
    exit /b 1
)
echo [OK] All packages installed.

:: ── Create .env ───────────────────────────────────────────────────
echo.
echo [3/4] Setting up environment config...
IF NOT EXIST ".env" (
    copy .env.example .env >nul
    echo [OK] Created .env from .env.example — edit it if needed.
) ELSE (
    echo [SKIP] .env already exists.
)

:: ── Create data directories ───────────────────────────────────────
echo.
echo [4/4] Creating data directories...
IF NOT EXIST "database" mkdir database
IF NOT EXIST "logs"     mkdir logs
IF NOT EXIST "ml"       mkdir ml
echo [OK] Directories ready.

:: ── Done ──────────────────────────────────────────────────────────
echo.
echo ================================================
echo  Setup complete!
echo  Run START_ALL.bat to launch the project.
echo ================================================
echo.
pause
