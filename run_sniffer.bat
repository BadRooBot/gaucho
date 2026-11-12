@echo off
title Gaucho Packet Sniffer - Conquer II Mobile
cd /d "%~dp0"
echo ========================================================
echo   Gaucho Conquer II Mobile - Packet Sniffer ^& Logger
echo ========================================================
echo.
python tools\sniff.py
pause

