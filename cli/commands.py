"""
Command handlers for the Sujin CLI.
"""

import os
import logging
from typing import Dict, Any, Callable, Optional
from .console import console, display_help, display_env, display_welcome, process_response, display_response
from .api import call_api, extract_response

logger = logging.getLogger(__name__)

def handle_exit() -> bool:
    """
    Handle the exit command.
    
    Returns:
        True to exit, False to continue
    """
    console.print("\n[system]Exiting...[/system]")
    return True

def handle_help(config: Dict[str, Any]) -> bool:
    """
    Handle the help command.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True to exit, False to continue
    """
    display_help()
    return False

def handle_env(config: Dict[str, Any]) -> bool:
    """
    Handle the env command.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True to exit, False to continue
    """
    display_env(config)
    return False

def handle_clear(config: Dict[str, Any]) -> bool:
    """
    Handle the clear command.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True to exit, False to continue
    """
    console.clear()
    display_welcome(config)
    return False

def handle_query(user_input: str, config: Dict[str, Any]) -> bool:
    """
    Handle a user query.
    
    Args:
        user_input: The user's input
        config: Configuration dictionary
        
    Returns:
        True to exit, False to continue
    """
    # Show user message
    console.print(f"\n[user]{user_input}[/user]")
    
    # Show thinking message with spinner
    with console.status("[info]Thinking...[/info]", spinner="dots"):
        # Call the API
        response = call_api(
            prompt=user_input,
            api_url=config["api_url"],
            api_key=config["api_key"],
            model=config["model"],
            max_tokens=1500  # Increased token limit for more complete responses
        )
    
    # Extract and process the response
    response_text = extract_response(response)
    processed_text = process_response(response_text)
    
    # Display the response
    display_response(processed_text, response)
    
    return False

# Command handlers dictionary
COMMANDS = {
    "exit": handle_exit,
    "help": handle_help,
    "env": handle_env,
    "clear": handle_clear,
}

def process_command(user_input: str, config: Dict[str, Any]) -> bool:
    """
    Process a command.
    
    Args:
        user_input: The user's input
        config: Configuration dictionary
        
    Returns:
        True to exit, False to continue
    """
    command = user_input.lower()
    
    if command in COMMANDS:
        return COMMANDS[command](config)
    elif not command.strip():
        return False
    else:
        return handle_query(user_input, config)
