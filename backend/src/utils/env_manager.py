"""
Environment configuration management for Pregame
"""

import os
import sys
from pathlib import Path
from typing import Dict

# Add the parent directory to the path to access the .env.local file
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

def read_env_file() -> Dict[str, str]:
    """
    Read API keys from .env.local file
    
    Returns:
        Dict[str, str]: Dictionary of environment variables
    """
    # Check current directory first
    env_file = Path(".env.local")
    if not env_file.exists():
        # Check parent directory as fallback
        env_file = parent_dir / ".env.local"
    
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    
    return env_vars

def get_api_keys() -> Dict[str, str]:
    """
    Get required API keys from environment
    
    Returns:
        Dict[str, str]: Dictionary with API keys
    """
    env_vars = read_env_file()
    
    return {
        'openai_key': env_vars.get('OPENAI_KEY'),
        'google_api_key': env_vars.get('GOOGLE_API_KEY', "AIzaSyAT4tQKRNt1rwrqrTs2GzlXuWi-BAYJWPA"),
        'google_cx': env_vars.get('GOOGLE_CX', "010381b2504d141f5")
    }

def validate_api_keys() -> bool:
    """
    Validate that required API keys are present
    
    Returns:
        bool: True if all required keys are present
    """
    keys = get_api_keys()
    return bool(keys['openai_key']) 