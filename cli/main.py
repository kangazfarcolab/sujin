"""
Main entry point for the Sujin CLI.
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Any, Optional
from rich.prompt import Prompt

from .config import load_config, check_required_env_vars
from .console import console, display_welcome
from .commands import process_command
from .setup import setup_environment

logger = logging.getLogger(__name__)

def run_cli() -> int:
    """
    Run the Sujin CLI.
    
    Returns:
        0 for success, 1 for failure
    """
    # Load configuration
    config = load_config()
    
    # Check required environment variables
    required_vars = ["CUSTOM_API_URL", "CUSTOM_API_KEY", "CUSTOM_API_MODEL"]
    if not check_required_env_vars(required_vars):
        console.print("\n[error]Missing required environment variables.[/error]")
        console.print("Run 'python sujin_cli.py env' to set up your environment.")
        return 1
    
    # Display welcome message
    display_welcome(config)
    
    # Main REPL loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold white]>[/bold white]", console=console)
            
            # Process the command
            should_exit = process_command(user_input, config)
            if should_exit:
                break
        except KeyboardInterrupt:
            console.print("\n[system]Exiting...[/system]")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            console.print(f"\n[error]Error: {e}[/error]")
    
    return 0

def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        0 for success, 1 for failure
    """
    parser = argparse.ArgumentParser(description="Sujin CLI")
    
    # Subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Environment setup command
    env_parser = subparsers.add_parser("env", help="Set up environment")
    
    # Run command (default)
    run_parser = subparsers.add_parser("run", help="Run the CLI")
    run_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set logging level
    if hasattr(args, "verbose") and args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Run the appropriate command
    if args.command == "env":
        return setup_environment()
    elif args.command == "run" or args.command is None:
        return run_cli()
    else:
        parser.print_help()
        return 1
