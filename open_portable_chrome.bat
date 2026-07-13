@echo off
REM ==========================================================
REM Open the PORTABLE Chrome (extracted in chrome-portable/)
REM with the bot's profile (./chrome-profile/).
REM
REM Use this to:
REM   1. Log in to Shopee ONCE - cookies will be saved
REM   2. Browse normally with the bot's profile
REM ==========================================================

set CHROME=%~dp0chrome-portable\chrome-win64\chrome.exe
set PROFILE=%~dp0chrome-profile

echo.
echo Opening portable Chrome with bot profile...
echo.
echo Chrome : %CHROME%
echo Profile: %PROFILE%
echo.
echo After this Chrome opens, please:
echo   1. Go to https://shopee.co.id
echo   2. Log in to your Shopee account
echo   3. (Optional) Navigate to your flash sale URL
echo   4. Leave this Chrome OPEN, then run py main.py
echo.
echo Press Ctrl+C in this window to stop Chrome.
echo.

start "" "%CHROME%" --user-data-dir="%PROFILE%" --no-first-run --no-default-browser-check "https://shopee.co.id"
