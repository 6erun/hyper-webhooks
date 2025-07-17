"""
Hyper-V Webhook Service

A Flask web service to handle webhooks for starting and stopping Hyper-V virtual machines.
"""

import ctypes
import os
import logging
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import subprocess
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VMRequest(BaseModel):
    """Pydantic model for VM operation requests."""
    vm_name: str
    action: str
    force: bool = False


class HyperVManager:
    """Manager class for Hyper-V operations using PowerShell."""
    @staticmethod
    def is_admin():
        """Check if the current process is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    @staticmethod
    def check_privileges():
        """Check if we have the necessary privileges for Hyper-V operations."""
        if not HyperVManager.is_admin():
            return {
                "success": False,
                "error": "Administrator privileges required for Hyper-V operations"
            }
        return {"success": True}
        
    @staticmethod
    def execute_powershell(command: str) -> Dict[str, Any]:
        """Execute a PowerShell command and return the result."""
        try:
            # Prepare the PowerShell command
            ps_command = [
                "pwsh.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]
            
            logger.info(f"Executing PowerShell command: {command}")
            
            # Execute the command
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip()
                }
                
        except subprocess.TimeoutExpired:
            logger.error("PowerShell command timed out")
            return {
                "success": False,
                "output": "",
                "error": "Command timed out"
            }
        except Exception as e:
            logger.error(f"Error executing PowerShell command: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    @staticmethod
    def get_vm_status(vm_name: str) -> Dict[str, Any]:
        """Get the status of a virtual machine."""
        command = f"Get-VM -Name '{vm_name}' | Select-Object Name, State | ConvertTo-Json -EnumsAsStrings"
        result = HyperVManager.execute_powershell(command)
        logger.info(f"VM status result: {result}")
        if result["success"] and result["output"]:
            try:
                vm_info = json.loads(result["output"])
                status = vm_info.get("State", "Unknown").lower()
                # Map "Off" status to "stopped" for consistency
                if status == "off":
                    status = "stopped"

                return {
                    "success": True,
                    "vm_name": vm_info["Name"],
                    "status": status,
                    #"raw_status": f"status: {status}"  # Add this for regex matching
                }
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing VM status: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error parsing VM status: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": result["error"] or "VM not found"
            }
    
    @staticmethod
    def start_vm(vm_name: str) -> Dict[str, Any]:
        """Start a virtual machine."""
        command = f"Start-VM -Name '{vm_name}'"
        result = HyperVManager.execute_powershell(command)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"VM '{vm_name}' started successfully",
                "vm_name": vm_name
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "vm_name": vm_name
            }
    
    @staticmethod
    def stop_vm(vm_name: str, force: bool = False) -> Dict[str, Any]:
        """Stop a virtual machine."""
        if force:
            command = f"Stop-VM -Name '{vm_name}' -Force"
        else:
            command = f"Stop-VM -Name '{vm_name}'"
            
        result = HyperVManager.execute_powershell(command)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"VM '{vm_name}' stopped successfully",
                "vm_name": vm_name
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "vm_name": vm_name
            }
    
    @staticmethod
    def restart_vm(vm_name: str, force: bool = False) -> Dict[str, Any]:
        """Restart a virtual machine."""
        if force:
            command = f"Restart-VM -Name '{vm_name}' -Force"
        else:
            command = f"Restart-VM -Name '{vm_name}'"
            
        result = HyperVManager.execute_powershell(command)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"VM '{vm_name}' restarted successfully",
                "vm_name": vm_name
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "vm_name": vm_name
            }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "hyper-v-webhook-service",
        "version": "1.0.0"
    })


@app.route('/vm/start', methods=['POST'])
def start_vm():
    """Start a virtual machine."""
    try:
        logger.info(f"Received request to stop VM: headers: {request.headers} data: {request.data}")

        vm_name = request.args.get('vm_name', '')
        if not vm_name:
            return jsonify({"success": False, "error": "vm_name parameter required"}), 400

        result = HyperVManager.start_vm(vm_name)
        
        if result["success"]:
            # Get updated status
            status_result = HyperVManager.get_vm_status(vm_name)
            if status_result["success"]:
                result["status"] = status_result["status"]
            
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"success": False, "error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error starting VM: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/vm/stop', methods=['POST'])
def stop_vm():
    """Stop a virtual machine."""
    try:
        logger.info(f"Received request to stop VM: headers: {request.headers} data: {request.data}")

        vm_name = request.args.get('vm_name')
        force_stop = request.args.get('force', 'false').lower() == 'true'
        if not vm_name:
            return jsonify({"success": False, "error": "vm_name parameter required"}), 400
        
        result = HyperVManager.stop_vm(vm_name, force_stop)
        
        if result["success"]:
            # Get updated status
            status_result = HyperVManager.get_vm_status(vm_name)
            if status_result["success"]:
                result["status"] = status_result["status"]
            
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"success": False, "error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error stopping VM: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/vm/restart', methods=['POST'])
def restart_vm():
    """Restart a virtual machine."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        vm_request = VMRequest(**data)
        result = HyperVManager.restart_vm(vm_request.vm_name, vm_request.force)
        
        if result["success"]:
            # Get updated status
            status_result = HyperVManager.get_vm_status(vm_request.vm_name)
            if status_result["success"]:
                result["status"] = status_result["status"]
            
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"success": False, "error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error restarting VM: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/vm/status', methods=['GET'])
def get_vm_status():
    """Get the status of a virtual machine."""
    try:
        vm_name = request.args.get('vm_name')
        if not vm_name:
            return jsonify({"success": False, "error": "vm_name parameter required"}), 400
        
        result = HyperVManager.get_vm_status(vm_name)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Error getting VM status: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/webhook/vm', methods=['POST'])
def vm_webhook():
    """Handle VM webhook events."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        logger.info(f"Received webhook: {data}")
        
        vm_request = VMRequest(**data)
        
        # Route to appropriate action
        if vm_request.action.lower() == "start":
            result = HyperVManager.start_vm(vm_request.vm_name)
        elif vm_request.action.lower() == "stop":
            result = HyperVManager.stop_vm(vm_request.vm_name, vm_request.force)
        elif vm_request.action.lower() == "restart":
            result = HyperVManager.restart_vm(vm_request.vm_name, vm_request.force)
        else:
            return jsonify({
                "success": False,
                "error": f"Invalid action: {vm_request.action}. Must be start, stop, or restart"
            }), 400
        
        if result["success"]:
            # Get updated status
            status_result = HyperVManager.get_vm_status(vm_request.vm_name)
            if status_result["success"]:
                result["status"] = status_result["status"]
            
            logger.info(f"Webhook processed successfully: {result}")
            return jsonify(result), 200
        else:
            logger.error(f"Webhook processing failed: {result}")
            return jsonify(result), 500
            
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"success": False, "error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Hyper-V Webhook Service on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
