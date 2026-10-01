@echo off
title Quantum HealthGuard — Stopper
color 0C
echo ===================================================
echo   QUANTUM HEALTHGUARD — Stopping All Services...
echo ===================================================
echo.

taskkill /FI "WINDOWTITLE eq QHG-*" /F >nul 2>&1
wmic process where "commandline like '%%Quan%%'" terminate >nul 2>&1

echo [OK] All HealthGuard services stopped.
ping -n 3 127.0.0.1 >nul
exit
