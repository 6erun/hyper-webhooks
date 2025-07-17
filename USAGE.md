# Hyper-V Webhook Service - Usage Examples

## Starting the Service

### Development Mode
```powershell
.\start_service.ps1
```

### Production Mode
```powershell
.\start_service.ps1 -Production
```

### With Custom Settings
```powershell
.\start_service.ps1 -Host "192.168.1.100" -Port 8080 -Debug
```

## API Usage Examples

### Using curl

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Start a VM
```bash
curl -X POST http://localhost:5000/vm/start \
  -H "Content-Type: application/json" \
  -d '{"vm_name": "MyVM", "action": "start"}'
```

#### Stop a VM
```bash
curl -X POST http://localhost:5000/vm/stop \
  -H "Content-Type: application/json" \
  -d '{"vm_name": "MyVM", "action": "stop", "force": false}'
```

#### Get VM Status
```bash
curl "http://localhost:5000/vm/status?vm_name=MyVM"
```

#### Send Webhook
```bash
curl -X POST http://localhost:5000/webhook/vm \
  -H "Content-Type: application/json" \
  -d '{"vm_name": "MyVM", "action": "restart", "force": true}'
```

### Using PowerShell

#### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET
```

#### Start a VM
```powershell
$body = @{
    vm_name = "MyVM"
    action = "start"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/vm/start" -Method POST -Body $body -ContentType "application/json"
```

#### Stop a VM with Force
```powershell
$body = @{
    vm_name = "MyVM"
    action = "stop"
    force = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/vm/stop" -Method POST -Body $body -ContentType "application/json"
```

#### Get VM Status
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/vm/status?vm_name=MyVM" -Method GET
```

#### Send Webhook
```powershell
$body = @{
    vm_name = "MyVM"
    action = "restart"
    force = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/webhook/vm" -Method POST -Body $body -ContentType "application/json"
```

### Using Python Test Client
```bash
python test_client.py MyVM
python test_client.py MyVM http://192.168.1.100:5000
```

## PowerShell Direct Testing

### Test VM Status
```powershell
.\test_hyperv.ps1 -VMName "MyVM" -Action status
```

### Start VM
```powershell
.\test_hyperv.ps1 -VMName "MyVM" -Action start
```

### Stop VM with Force
```powershell
.\test_hyperv.ps1 -VMName "MyVM" -Action stop -Force
```

### Restart VM
```powershell
.\test_hyperv.ps1 -VMName "MyVM" -Action restart
```

## Expected Response Formats

### Success Response
```json
{
  "success": true,
  "message": "VM 'MyVM' started successfully",
  "vm_name": "MyVM",
  "status": "running"
}
```

### Error Response
```json
{
  "success": false,
  "error": "VM 'MyVM' not found",
  "vm_name": "MyVM"
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "service": "hyper-v-webhook-service",
  "version": "1.0.0"
}
```

## Integration Examples

### GitHub Actions Webhook
```yaml
- name: Start VM via Webhook
  run: |
    curl -X POST ${{ secrets.HYPERV_WEBHOOK_URL }}/webhook/vm \
      -H "Content-Type: application/json" \
      -d '{"vm_name": "${{ secrets.VM_NAME }}", "action": "start"}'
```

### Azure DevOps Pipeline
```yaml
- task: PowerShell@2
  displayName: 'Start VM'
  inputs:
    targetType: 'inline'
    script: |
      $body = @{
          vm_name = "$(vmName)"
          action = "start"
      } | ConvertTo-Json
      
      Invoke-RestMethod -Uri "$(webhookUrl)/webhook/vm" -Method POST -Body $body -ContentType "application/json"
```
