@echo off
title Gaucho MITM Proxy Sniffer - Conquer II Mobile
cd /d "%~dp0\rust"
echo ========================================================
echo   Gaucho Conquer II Mobile - MITM Proxy Sniffer
echo   Transparent ^& 100%% Stable (Zero Crash Risk)
echo ========================================================
echo.
set PROXY_PORT=8020
set TARGET_SERVER=170.33.9.35:8020
set NAMES_FILE=..\mobile-packets-ids-names.txt

echo [*] Applying LDPlayer iptables port redirection...
C:\LDPlayer\LDPlayer9\adb.exe shell "su -c 'iptables -t nat -F OUTPUT; iptables -t nat -A OUTPUT -p tcp --dport 8020 -j DNAT --to-destination 192.168.1.8:8020'"

echo [*] Starting Proxy Sniffer on port 8020...
echo.
target\debug\gaucho-proxy.exe

echo.
echo [*] Cleaning up iptables on exit...
C:\LDPlayer\LDPlayer9\adb.exe shell "su -c 'iptables -t nat -F OUTPUT'"
pause
