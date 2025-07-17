@echo off
.\venv\Scripts\activate.bat

REM Set PowerShell 7+ path
set PWSH_PATH="C:\Program Files\PowerShell\7\pwsh.exe"

REM Check if PowerShell 7+ is available at the specified path
%PWSH_PATH% -version >nul 2>&1
if %errorLevel% neq 0 (
    echo PowerShell 7+ not found at %PWSH_PATH%
    echo Please ensure PowerShell 7+ is installed
    echo Download from: https://github.com/PowerShell/PowerShell/releases
    pause
    exit /b 1
)

echo Found PowerShell 7+ at %PWSH_PATH%

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    python app.py
) else (
    echo Requesting administrator privileges...
    %PWSH_PATH% -Command "Start-Process python -ArgumentList 'app.py' -Verb RunAs"
)