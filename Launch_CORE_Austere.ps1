# CORE_Austere Desktop Launcher (PowerShell)
# This script launches the CORE_Austere Electron app

Write-Host "Starting CORE_Austere..." -ForegroundColor Green
Write-Host ""

# Change to the app directory
$AppPath = "C:\Users\marka\Coding Projects\Core\CORE_Austere"
Set-Location $AppPath

# Activate virtual environment
Write-Host "Activating Python virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Build React frontend
Write-Host "Building React frontend..." -ForegroundColor Yellow
Set-Location "user_interface"
npm run build
Set-Location ".."

# Launch Electron app
Write-Host "Launching CORE_Austere desktop app..." -ForegroundColor Green
npm start

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error occurred. Press any key to close..." -ForegroundColor Red
    Read-Host
}
