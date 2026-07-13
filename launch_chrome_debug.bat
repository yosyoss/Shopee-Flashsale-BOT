@echo off
REM ==========================================================
REM Launch Chrome with remote debugging port enabled.
REM The bot will connect to this Chrome instance and inherit
REM your login state, cookies, and browser fingerprint.
REM ==========================================================

set CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe
set DEBUG_PORT=9222
set USER_DATA=%LOCALAPPDATA%\Google\Chrome\User Data

if not exist "%CHROME%" (
    echo.
    echo [ERROR] Chrome not found at: %CHROME%
    echo Please edit this file and update the path to your chrome.exe
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Shopee Flashsale BOT - Chrome Launcher
echo ============================================================
echo.
echo Step 1/3: Closing all existing Chrome windows...
echo (so the new Chrome can use your existing profile)
echo.

taskkill /F /IM chrome.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo Step 2/3: Launching Chrome with --remote-debugging-port=%DEBUG_PORT%...
echo.

REM Use `start` with title="", all on one line (no ^ line-continuation,
REM which can confuse cmd.exe's argument parser). `start` returns
REM immediately so the .bat can continue to Step 3/3.
start "" "%CHROME%" --remote-debugging-port=%DEBUG_PORT% --user-data-dir="%USER_DATA%" --no-first-run --no-default-browser-check "https://shopee.co.id"

echo.
echo Step 3/3: Verifying debug port is open...
echo.

REM Give Chrome time to fully load the profile and bind the debug port.
REM Loading Yosua's profile (with tabs, extensions) can take 5-10 seconds.
timeout /t 8 /nobreak >nul

echo Looking for port %DEBUG_PORT% in active connections...
echo.
netstat -an | findstr ":%DEBUG_PORT%"
echo.

netstat -an | findstr ":%DEBUG_PORT%" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Port %DEBUG_PORT% is listening. Bot can connect.
) else (
    echo [WARN] Port %DEBUG_PORT% does NOT appear to be open.
    echo.
    echo Possible causes:
    echo   1. Chrome is still loading the profile - wait 10s and re-run the bot
    echo   2. The flag was rejected by Chrome (rare for this flag)
    echo   3. Another Chrome instance locked the profile and the new one
    echo      silently dropped the --remote-debugging-port flag
    echo.
    echo Manual check - run this in PowerShell:
    echo   netstat -an ^| findstr %DEBUG_PORT%
    echo.
    echo If you see nothing, try this manual launch in PowerShell:
    echo   Start-Process chrome -ArgumentList "--remote-debugging-port=9222","--user-data-dir=`"$env:LOCALAPPDATA\Google\Chrome\User Data`""
    echo Then check: netstat -an ^| findstr 9222
)

echo.
echo ============================================================
echo   NEXT STEPS:
echo   1. If asked, pick your profile (Yosua / Person 2)
echo   2. Make sure you are LOGGED IN to Shopee in this Chrome
echo   3. Leave this Chrome window OPEN
echo   4. In another terminal, run:  py main.py
echo ============================================================
echo.
pause
