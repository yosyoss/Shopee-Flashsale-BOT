# ==========================================================
# Launch Chrome with remote debugging port enabled (PowerShell)
# The bot will connect to this Chrome instance and inherit
# your login state, cookies, and browser fingerprint.
# ==========================================================

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$userData = "$env:LOCALAPPDATA\Google\Chrome\User Data"

if (-not (Test-Path $chrome)) {
    Write-Host "[ERROR] Chrome not found at: $chrome" -ForegroundColor Red
    Write-Host "Please edit this file and update the path to your chrome.exe"
    pause
    exit 1
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  Shopee Flashsale BOT - Chrome Launcher (PowerShell)"
Write-Host "============================================================"
Write-Host ""
Write-Host "Step 1/3: Closing all existing Chrome windows..."

# Force-close all Chrome processes so the new instance can use the profile
Get-Process chrome -ErrorAction SilentlyContinue | ForEach-Object { $_.Kill() }
Start-Sleep -Seconds 2

Write-Host "Step 2/3: Launching Chrome with remote-debugging-port=9222..."
Write-Host ""

# Build argument array
$args = @(
    "--remote-debugging-port=9222",
    "--user-data-dir=`"$userData`"",
    "--no-first-run",
    "--no-default-browser-check",
    "https://shopee.co.id"
)

Start-Process -FilePath $chrome -ArgumentList $args

Write-Host ""
Write-Host "Step 3/3: Chrome is now open with debug port."
Write-Host ""
Write-Host "============================================================"
Write-Host "  NEXT STEPS:"
Write-Host "  1. If asked, pick your profile (Yosua / Person 2)"
Write-Host "  2. Make sure you are LOGGED IN to Shopee in this Chrome"
Write-Host "  3. Leave this Chrome window OPEN"
Write-Host "  4. In another terminal, run:  py main.py"
Write-Host "============================================================"
Write-Host ""
pause
