@echo off
title Quantum HealthGuard — GitHub Push
color 0B
echo ================================================
echo   QUANTUM HEALTHGUARD — Push to GitHub
echo ================================================
echo.

:: Refresh PATH so gh is found after fresh install
set PATH=%PATH%;C:\Program Files\GitHub CLI\

echo [1/3] Logging into GitHub...
echo       A browser window will open — sign in with: rishikesh2006-cloud
echo.
gh auth login --web --git-protocol https

echo.
echo [2/3] Creating GitHub repository...
gh repo create quantum-healthguard ^
  --public ^
  --description "IoT health monitoring with Raspberry Pi, MQTT, ML and Qiskit QSVC" ^
  --source=. ^
  --remote=origin ^
  --push

echo.
echo [3/3] Verifying...
git log --oneline -3
echo.
echo ================================================
echo  DONE! Your repo is live at:
echo  https://github.com/rishikesh2006-cloud/quantum-healthguard
echo ================================================
echo.
pause
