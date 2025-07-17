# PowerShell script to start the Hyper-V Webhook Service

param(
    [Parameter(Mandatory=$false)]
    [string]$Host = "0.0.0.0",
    
    [Parameter(Mandatory=$false)]
    [int]$Port = 5000,
    
    [Parameter(Mandatory=$false)]
    [switch]$Debug,
    
    [Parameter(Mandatory=$false)]
    [switch]$Production
)

.venv\Scripts\Activate.ps1

# Set the working directory to the script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "Hyper-V Webhook Service Startup Script"
Write-Host "======================================="

# Check if Python is available
try {
    $pythonPath = ".\.venv\Scripts\python.exe"
    if (-not (Test-Path $pythonPath)) {
        Write-Host "Virtual environment not found. Please run setup first." -ForegroundColor Red
        exit 1
    }
    
    $pythonVersion = & $pythonPath --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python is not available. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check if Hyper-V module is available
if (-not (Get-Module -Name Hyper-V -ListAvailable)) {
    Write-Host "Warning: Hyper-V PowerShell module is not available." -ForegroundColor Yellow
    Write-Host "The service will start but VM operations will fail." -ForegroundColor Yellow
}

# Set environment variables
$env:FLASK_HOST = $Host
$env:FLASK_PORT = $Port.ToString()
$env:FLASK_DEBUG = if ($Debug) { "True" } else { "False" }

Write-Host "Configuration:"
Write-Host "  Host: $Host"
Write-Host "  Port: $Port"
Write-Host "  Debug: $($env:FLASK_DEBUG)"
Write-Host "  Production: $Production"
Write-Host ""

if ($Production) {
    Write-Host "Starting service in production mode with Gunicorn..."
    & $pythonPath -m gunicorn --bind "$Host`:$Port" --workers 4 --timeout 60 app:app
} else {
    Write-Host "Starting service in development mode..."
    Write-Host "Service will be available at: http://$Host`:$Port"
    Write-Host "Health check: http://$Host`:$Port/health"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the service"
    Write-Host ""
    
    & $pythonPath app.py
}
