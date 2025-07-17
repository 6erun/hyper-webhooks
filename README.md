# Hyper-V Webhook Service

A Python web service to handle webhooks for starting and stopping Hyper-V virtual machines.

## Features

- RESTful API endpoints for VM operations
- Webhook handling for external systems
- Hyper-V PowerShell integration
- Request validation and error handling
- Logging and monitoring

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your settings
4. Run the service:
   ```bash
   python app.py
   ```

1. Install Powershell: `winget install --id Microsoft.PowerShell --source winget`

## API Endpoints

### VM Operations
- `POST /vm/start` - Start a virtual machine
- `POST /vm/stop` - Stop a virtual machine
- `POST /vm/restart` - Restart a virtual machine
- `GET /vm/status` - Get VM status

### Webhooks
- `POST /webhook/vm` - Handle VM webhook events

## Request Format

```json
{
    "vm_name": "MyVM",
    "action": "start|stop|restart",
    "force": false
}
```

## Response Format

```json
{
    "success": true,
    "message": "VM operation completed successfully",
    "vm_name": "MyVM",
    "status": "running"
}
```

## Environment Variables

- `FLASK_HOST` - Host to bind the service (default: 0.0.0.0)
- `FLASK_PORT` - Port to bind the service (default: 5000)
- `FLASK_DEBUG` - Enable debug mode (default: False)
- `LOG_LEVEL` - Logging level (default: INFO)
