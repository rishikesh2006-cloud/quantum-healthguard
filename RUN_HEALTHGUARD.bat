@echo off
title Quantum HealthGuard — Launcher
color 0A
echo ===================================================
echo   QUANTUM HEALTHGUARD — 1-CLICK LAUNCHER
echo ===================================================
echo.

SET ROOT=%~dp0
SET VENV=%ROOT%.venv\Scripts\python.exe

:: Stop any previous background processes
taskkill /FI "WINDOWTITLE eq QHG-*" /F >nul 2>&1

echo [1/4] Starting MQTT Broker...
start /low "QHG-Broker" /min cmd /c "%VENV% %ROOT%communication\mqtt_broker.py"
ping -n 3 127.0.0.1 >nul

echo [2/4] Starting MQTT Receiver...
start /low "QHG-Receiver" /min cmd /c "%VENV% %ROOT%communication\mqtt_receiver.py"
ping -n 2 127.0.0.1 >nul

echo [3/4] Starting Sensor Simulator...
start /low "QHG-Simulator" /min cmd /c "%VENV% %ROOT%simulator\sensor_simulator.py"
ping -n 2 127.0.0.1 >nul

echo [4/4] Starting Web Dashboard Server...
start /low "QHG-Dashboard" /min cmd /c "%VENV% %ROOT%dashboard\app.py"
ping -n 3 127.0.0.1 >nul

echo.
echo ===================================================
echo  ALL SERVICES LAUNCHED IN BACKGROUND!
echo  Client View : http://localhost:5000
echo  Admin View  : http://localhost:5000/admin
echo ===================================================
echo.
start http://localhost:5000
exit
