"""
Configuration handling for the Sujin CLI.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv, set_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        A dictionary with configuration values
    """
    # Load environment variables
    load_dotenv()
    
    # Get environment variables
    config = {
        "api_url": os.environ.get("CUSTOM_API_URL"),
        "api_key": os.environ.get("CUSTOM_API_KEY"),
        "model": os.environ.get("CUSTOM_API_MODEL"),
        "agent_name": os.environ.get("AGENT_NAME", "Sujin"),
        "agent_description": os.environ.get("AGENT_DESCRIPTION", "AI Assistant powered by Sujin Agent Framework"),
    }
    
    return config

def check_required_env_vars(required_vars: List[str]) -> bool:
    """
    Check if all required environment variables are set.
    
    Args:
        required_vars: List of required environment variable names
        
    Returns:
        True if all required variables are set, False otherwise
    """
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def save_config(env_vars: Dict[str, str]) -> None:
    """
    Save configuration to .env file.
    
    Args:
        env_vars: Dictionary of environment variables to save
    """
    with open(".env", "w") as f:
        f.write("# API Configuration\n")
        f.write(f"CUSTOM_API_URL={env_vars['CUSTOM_API_URL']}\n")
        f.write(f"CUSTOM_API_KEY={env_vars['CUSTOM_API_KEY']}\n")
        f.write(f"CUSTOM_API_MODEL={env_vars['CUSTOM_API_MODEL']}\n")
        f.write("\n# Agent Configuration\n")
        f.write(f"AGENT_NAME={env_vars['AGENT_NAME']}\n")
        f.write(f"AGENT_DESCRIPTION={env_vars['AGENT_DESCRIPTION']}\n")
    
    logger.info(f".env file created at {os.path.abspath('.env')}")
