"""
Configuration module for the Hyper-V Webhook Service.
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the application."""
    
    # Flask configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # PowerShell configuration
    POWERSHELL_TIMEOUT = int(os.getenv('POWERSHELL_TIMEOUT', 30))
    POWERSHELL_EXECUTION_POLICY = os.getenv('POWERSHELL_EXECUTION_POLICY', 'Bypass')
    
    # Service configuration
    SERVICE_NAME = "Hyper-V Webhook Service"
    SERVICE_VERSION = "1.0.0"
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """Get configuration as a dictionary."""
        return {
            'flask': {
                'host': cls.FLASK_HOST,
                'port': cls.FLASK_PORT,
                'debug': cls.FLASK_DEBUG
            },
            'logging': {
                'level': cls.LOG_LEVEL,
                'format': cls.LOG_FORMAT
            },
            'powershell': {
                'timeout': cls.POWERSHELL_TIMEOUT,
                'execution_policy': cls.POWERSHELL_EXECUTION_POLICY
            },
            'service': {
                'name': cls.SERVICE_NAME,
                'version': cls.SERVICE_VERSION
            }
        }
