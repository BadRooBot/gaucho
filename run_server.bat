@echo off
REM ++++++++++++
REM * gaucho - conquer mobile private server
REM * with love from bolzov (ᵔᴥᵔ)
REM * https://github.com/ibolzov
REM ++++++++++++
setlocal

REM -- pick an adb that actually sees a device (platform-tools, PATH, or LDPlayer's own) --
if not defined ADB if defined ANDROID_HOME set "ADB=%ANDROID_HOME%\platform-tools\adb.exe"
if not defined ADB set "ADB=C:\Users\Youssef\Downloads\PC\AndroidSdk\AndroidSdk\platform-tools\adb.exe"
set "ADBOK="
call :adb_ok "%ADB%"
if not errorlevel 1 set "ADBOK=%ADB%"
if not defined ADBOK (
  call :adb_ok "adb"
  if not errorlevel 1 set "ADBOK=adb"
)
if not defined ADBOK for %%A in ("C:\LDPlayer\LDPlayer9\adb.exe" "C:\leidian\LDPlayer9\adb.exe" "C:\LDPlayer\LDPlayer4\adb.exe" "C:\leidian\LDPlayer4\adb.exe") do if not defined ADBOK (
  call :adb_ok "%%~A"
  if not errorlevel 1 set "ADBOK=%%~A"
)
if not defined ADBOK (
  echo [X] no adb that sees a device.
  echo     start LDPlayer first ^(or plug the phone with usb debugging^), then run this again.
  pause
  exit /b 1
)

REM -- pick the device: prefer emulator/loopback serials, wait out adb startup fights --
set /a _n=0
:pick_dev
for /f "tokens=1,2" %%a in ('"%ADBOK%" devices 2^>nul') do if /i "%%b"=="device" if not defined DEV (echo %%a| findstr /r /c:"^emulator-" /c:"^127\.0\.0\.1:" /c:"^localhost" >nul && set "DEV=%%a")
for /f "tokens=1,2" %%a in ('"%ADBOK%" devices 2^>nul') do if /i "%%b"=="device" if not defined DEV set "DEV=%%a"
if defined DEV goto dev_ready
set /a _n+=1
if %_n% equ 3 (
  echo [..] no device yet - restarting the adb server once
  "%ADBOK%" kill-server >nul 2>&1
  ping -n 4 127.0.0.1 >nul
)
if %_n% lss 8 (
  ping -n 2 127.0.0.1 >nul
  goto pick_dev
)
echo [X] no adb device in "device" state. start LDPlayer ^(or plug the phone^) and run again.
pause
exit /b 1

:dev_ready
"%ADBOK%" devices 2>nul | findstr /c:"%DEV%" | findstr /c:"device" >nul
if not errorlevel 1 goto dev_ok
echo [..] %DEV% not in the device list, trying adb connect
"%ADBOK%" connect %DEV% >nul 2>&1
ping -n 3 127.0.0.1 >nul
"%ADBOK%" devices 2>nul | findstr /c:"%DEV%" | findstr /c:"device" >nul
if not errorlevel 1 goto dev_ok
echo [X] device %DEV% is not reachable through adb.
pause
exit /b 1
:dev_ok

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8020" ^| findstr LISTENING') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5816" ^| findstr LISTENING') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":9528" ^| findstr LISTENING') do taskkill /F /PID %%p >nul 2>&1

REM -- reverse tunnels: verify each one, retry, and abort loudly instead of failing silent --
set "REVFAIL="
call :rev 8020
call :rev 5816
call :rev 9528
if defined REVFAIL (
  echo [X] adb reverse failed - the emulator would get "Cannot reach the server".
  echo     a second adb on port 5037 - LDPlayer's own - may be fighting yours. close it and retry.
  pause
  exit /b 1
)

if "%~1"=="" (
  set CQ2_BIND_HOST=127.0.0.1
) else (
  set CQ2_BIND_HOST=127.0.0.1,%~1
)

REM -- localhost GM hook: /gm?cmd=/cps+100000 (useful when an emulator IME crashes) --
set CQ2_GM_HTTP=1

echo [OK] adb: %ADBOK%
echo [OK] device: %DEV%
echo [OK] reverse 8020/5816/9528: %DEV% -^> 127.0.0.1
echo [OK] bind: %CQ2_BIND_HOST%
echo [..] emulator uses the tunnels above; a real phone needs its pc ip: run_server.bat pc-ip-here

cd /d "%~dp0rust"
cargo run --release
pause
endlocal
exit /b 0

REM ---- subroutines ----

:adb_ok
set "_d="
for /f "tokens=1,2" %%a in ('"%~1" devices 2^>nul') do if /i "%%b"=="device" if not defined _d set "_d=%%a"
if not defined _d exit /b 1
exit /b 0

:rev
set /a _r=0
:rev_try
"%ADBOK%" -s "%DEV%" reverse tcp:%~1 tcp:%~1 >nul 2>&1
"%ADBOK%" reverse --list 2>nul | findstr /c:"tcp:%~1 tcp:%~1" >nul
if not errorlevel 1 exit /b 0
set /a _r+=1
if %_r% lss 3 (
  ping -n 3 127.0.0.1 >nul
  goto rev_try
)
echo [X] reverse tcp:%~1 failed on %DEV%
set "REVFAIL=1"
exit /b 1
