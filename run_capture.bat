@echo off
title Conquer II Mobile - Packet Capture ^& REA Analyzer
cd /d "%~dp0"
echo ========================================================
echo   Conquer II Mobile - Live Packet Capture ^& Analyzer
echo ========================================================
echo.
python tools\capture_tool.py
pause

