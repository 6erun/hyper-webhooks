# PowerShell script to test Hyper-V VM operations
# This script demonstrates direct PowerShell commands that the service uses

param(
    [Parameter(Mandatory=$true)]
    [string]$VMName,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "status",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

function Write-Result {
    param(
        [string]$Operation,
        [bool]$Success,
        [string]$Message,
        [object]$Data = $null
    )
    
    $result = @{
        operation = $Operation
        success = $Success
        message = $Message
        vm_name = $VMName
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
    
    if ($Data) {
        $result.data = $Data
    }
    
    Write-Host ($result | ConvertTo-Json -Depth 3)
}

function Get-VMStatus {
    param([string]$Name)
    
    try {
        $vm = Get-VM -Name $Name -ErrorAction Stop
        Write-Result -Operation "get_status" -Success $true -Message "VM status retrieved successfully" -Data @{
            name = $vm.Name
            state = $vm.State
            status = $vm.Status
            uptime = $vm.Uptime
            memory_assigned = $vm.MemoryAssigned
            processor_count = $vm.ProcessorCount
        }
    }
    catch {
        Write-Result -Operation "get_status" -Success $false -Message "Failed to get VM status: $($_.Exception.Message)"
    }
}

function Start-VMOperation {
    param([string]$Name)
    
    try {
        Start-VM -Name $Name -ErrorAction Stop
        Write-Result -Operation "start" -Success $true -Message "VM started successfully"
        Start-Sleep -Seconds 2
        Get-VMStatus -Name $Name
    }
    catch {
        Write-Result -Operation "start" -Success $false -Message "Failed to start VM: $($_.Exception.Message)"
    }
}

function Stop-VMOperation {
    param([string]$Name, [bool]$ForceStop)
    
    try {
        if ($ForceStop) {
            Stop-VM -Name $Name -Force -ErrorAction Stop
            Write-Result -Operation "stop" -Success $true -Message "VM stopped successfully (forced)"
        } else {
            Stop-VM -Name $Name -ErrorAction Stop
            Write-Result -Operation "stop" -Success $true -Message "VM stopped successfully"
        }
        Start-Sleep -Seconds 2
        Get-VMStatus -Name $Name
    }
    catch {
        Write-Result -Operation "stop" -Success $false -Message "Failed to stop VM: $($_.Exception.Message)"
    }
}

function Restart-VMOperation {
    param([string]$Name, [bool]$ForceRestart)
    
    try {
        if ($ForceRestart) {
            Restart-VM -Name $Name -Force -ErrorAction Stop
            Write-Result -Operation "restart" -Success $true -Message "VM restarted successfully (forced)"
        } else {
            Restart-VM -Name $Name -ErrorAction Stop
            Write-Result -Operation "restart" -Success $true -Message "VM restarted successfully"
        }
        Start-Sleep -Seconds 2
        Get-VMStatus -Name $Name
    }
    catch {
        Write-Result -Operation "restart" -Success $false -Message "Failed to restart VM: $($_.Exception.Message)"
    }
}

# Check if Hyper-V module is available
if (-not (Get-Module -Name Hyper-V -ListAvailable)) {
    Write-Result -Operation "check_hyperv" -Success $false -Message "Hyper-V PowerShell module is not available. Please install Hyper-V feature."
    exit 1
}

# Import Hyper-V module
Import-Module Hyper-V -ErrorAction SilentlyContinue

Write-Host "Hyper-V VM Management Script"
Write-Host "VM Name: $VMName"
Write-Host "Action: $Action"
Write-Host "Force: $Force"
Write-Host "----------------------------------------"

# Execute the requested action
switch ($Action.ToLower()) {
    "start" {
        Start-VMOperation -Name $VMName
    }
    "stop" {
        Stop-VMOperation -Name $VMName -ForceStop $Force
    }
    "restart" {
        Restart-VMOperation -Name $VMName -ForceRestart $Force
    }
    "status" {
        Get-VMStatus -Name $VMName
    }
    default {
        Write-Result -Operation "unknown" -Success $false -Message "Unknown action: $Action"
    }
}
