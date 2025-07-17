# PowerShell script to set up the Hyper-V Webhook Service

Write-Host "Hyper-V Webhook Service Setup Script"
Write-Host "====================================="

# Set the working directory to the script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python is not available. Please install Python 3.8 or higher first." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies..."
$pythonPath = ".\.venv\Scripts\python.exe"
$pipPath = ".\.venv\Scripts\pip.exe"

& $pipPath install --upgrade pip
& $pipPath install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..."
    Copy-Item ".env.example" ".env"
}

# Check Hyper-V availability
Write-Host "Checking Hyper-V availability..."
if (Get-Module -Name Hyper-V -ListAvailable) {
    Write-Host "Hyper-V PowerShell module is available." -ForegroundColor Green
} else {
    Write-Host "Warning: Hyper-V PowerShell module is not available." -ForegroundColor Yellow
    Write-Host "To install Hyper-V, run the following command as Administrator:" -ForegroundColor Yellow
    Write-Host "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the service:"
Write-Host "  .\start_service.ps1"
Write-Host ""
Write-Host "To start in production mode:"
Write-Host "  .\start_service.ps1 -Production"
Write-Host ""
Write-Host "To test with a VM:"
Write-Host "  python test_client.py <vm_name>"
Write-Host ""
Write-Host "To test PowerShell operations directly:"
Write-Host "  .\test_hyperv.ps1 -VMName <vm_name> -Action status"
