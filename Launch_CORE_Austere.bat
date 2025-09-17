@echo off
REM CORE_Austere Desktop Launcher
REM This batch file launches the CORE_Austere Electron app

echo Starting CORE_Austere...
echo.

REM Change to the app directory
cd /d "C:\Users\marka\Coding Projects\Core\CORE_Austere"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Build React frontend if needed
echo Building React frontend...
cd user_interface
call npm run build
cd ..

REM Launch Electron app
echo Launching CORE_Austere desktop app...
call npm start

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to close...
    pause >nul
)
