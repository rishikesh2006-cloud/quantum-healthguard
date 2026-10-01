@echo off
title Quantum HealthGuard Launcher
color 0A
echo ============================================
echo    QUANTUM HEALTHGUARD - WINDOWS TEST MODE
echo ============================================
echo.

SET ROOT=%~dp0
SET VENV=%ROOT%.venv\Scripts

echo [1/4] Starting MQTT Broker (Python)...
start "QHG - MQTT Broker" cmd /k "title QHG-Broker && %VENV%\python.exe %ROOT%communication\mqtt_broker.py"
echo     Waiting for broker to start...
timeout /t 4 /nobreak >nul

echo [2/4] Starting MQTT Receiver...
start "QHG - MQTT Receiver" cmd /k "title QHG-Receiver && %VENV%\python.exe %ROOT%communication\mqtt_receiver.py"
timeout /t 2 /nobreak >nul

echo [3/4] Starting Sensor Simulator...
start "QHG - Sensor Simulator" cmd /k "title QHG-Simulator && %VENV%\python.exe %ROOT%simulator\sensor_simulator.py"
timeout /t 2 /nobreak >nul

echo [4/4] Starting Dashboard...
start "QHG - Dashboard" cmd /k "title QHG-Dashboard && %VENV%\python.exe %ROOT%dashboard\app.py"
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo  ALL COMPONENTS STARTED!
echo  Open browser: http://localhost:5000
echo ============================================
echo.
start http://localhost:5000
echo Press any key to close this launcher...
pause >nul
