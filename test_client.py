"""
Test client for the Hyper-V Webhook Service

This script demonstrates how to interact with the webhook service.
"""

import requests
import json
import sys
from typing import Dict, Any


class HyperVWebhookClient:
    """Client for interacting with the Hyper-V Webhook Service."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the webhook service."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return {
                "status_code": response.status_code,
                "success": response.status_code < 400,
                "data": response.json() if response.content else {}
            }
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the service is healthy."""
        return self._make_request("GET", "/health")
    
    def start_vm(self, vm_name: str) -> Dict[str, Any]:
        """Start a virtual machine."""
        data = {"vm_name": vm_name, "action": "start"}
        return self._make_request("POST", "/vm/start", data)
    
    def stop_vm(self, vm_name: str, force: bool = False) -> Dict[str, Any]:
        """Stop a virtual machine."""
        data = {"vm_name": vm_name, "action": "stop", "force": force}
        return self._make_request("POST", "/vm/stop", data)
    
    def restart_vm(self, vm_name: str, force: bool = False) -> Dict[str, Any]:
        """Restart a virtual machine."""
        data = {"vm_name": vm_name, "action": "restart", "force": force}
        return self._make_request("POST", "/vm/restart", data)
    
    def get_vm_status(self, vm_name: str) -> Dict[str, Any]:
        """Get the status of a virtual machine."""
        return self._make_request("GET", f"/vm/status?vm_name={vm_name}")
    
    def send_webhook(self, vm_name: str, action: str, force: bool = False) -> Dict[str, Any]:
        """Send a webhook request."""
        data = {"vm_name": vm_name, "action": action, "force": force}
        return self._make_request("POST", "/webhook/vm", data)


def print_response(response: Dict[str, Any], operation: str):
    """Print a formatted response."""
    print(f"\n=== {operation} ===")
    print(f"Status Code: {response.get('status_code', 'N/A')}")
    print(f"Success: {response.get('success', False)}")
    
    if 'data' in response:
        print("Response Data:")
        print(json.dumps(response['data'], indent=2))
    
    if 'error' in response:
        print(f"Error: {response['error']}")
    
    print("-" * 50)


def main():
    """Main function to demonstrate the client."""
    if len(sys.argv) < 2:
        print("Usage: python test_client.py <vm_name> [service_url]")
        print("Example: python test_client.py MyVM")
        print("Example: python test_client.py MyVM http://localhost:5000")
        sys.exit(1)
    
    vm_name = sys.argv[1]
    service_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000"
    
    client = HyperVWebhookClient(service_url)
    
    print(f"Testing Hyper-V Webhook Service with VM: {vm_name}")
    print(f"Service URL: {service_url}")
    
    # Health check
    response = client.health_check()
    print_response(response, "Health Check")
    
    if not response.get('success'):
        print("Service is not available. Make sure the service is running.")
        sys.exit(1)
    
    # Get initial VM status
    response = client.get_vm_status(vm_name)
    print_response(response, f"Initial Status for {vm_name}")
    
    # Test webhook endpoint
    print("\nTesting webhook endpoints...")
    
    # Test start via webhook
    response = client.send_webhook(vm_name, "start")
    print_response(response, f"Webhook Start {vm_name}")
    
    # Get status after start
    response = client.get_vm_status(vm_name)
    print_response(response, f"Status after start for {vm_name}")
    
    # Test stop via direct API
    response = client.stop_vm(vm_name)
    print_response(response, f"Direct API Stop {vm_name}")
    
    # Get final status
    response = client.get_vm_status(vm_name)
    print_response(response, f"Final Status for {vm_name}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    main()
