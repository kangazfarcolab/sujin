#!/usr/bin/env python
"""
Sujin CLI with environment setup wizard.
"""

import os
import sys
import argparse
import logging
import requests
import json
from dotenv import load_dotenv, set_key
from typing import Dict, List, Any, Optional

# Rich library for better CLI formatting
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.theme import Theme
from rich.table import Table
from rich import box

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def call_api(
    prompt: str,
    api_url: str,
    api_key: str,
    model: str,
    system_message: str = "You are a helpful assistant.",
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Call the API with the given prompt.

    Args:
        prompt: The user prompt
        api_url: The API URL
        api_key: The API key
        model: The model to use
        system_message: The system message

    Returns:
        The API response
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }

    logger.debug(f"Calling API at {api_url}")
    logger.debug(f"Using model: {model}")
    logger.debug(f"Messages: {data['messages']}")

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30  # 30 second timeout
        )

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API request failed with status {response.status_code}: {response.text}")
            return {"error": f"API request failed with status {response.status_code}: {response.text}"}
    except Exception as e:
        logger.error(f"Error calling API: {e}")
        return {"error": f"Error calling API: {e}"}

def extract_response(api_response: Dict[str, Any]) -> str:
    """
    Extract the response text from the API response.

    Args:
        api_response: The API response

    Returns:
        The response text
    """
    if "error" in api_response:
        return f"Error: {api_response['error']}"

    try:
        if "choices" in api_response and len(api_response["choices"]) > 0:
            choice = api_response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]

        return "No response generated."
    except Exception as e:
        logger.error(f"Error extracting response: {e}")
        return f"Error extracting response: {e}"

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
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in a .env file or as environment variables.")
        print("Run 'python sujin.py env' to set up your environment.")
        return False

    return True

def setup_environment():
    """
    Set up the environment by creating a .env file.
    """
    print("\n" + "="*50)
    print("Sujin Environment Setup Wizard")
    print("="*50)
    print("\nThis wizard will help you set up your Sujin environment.")
    print("It will create a .env file with your API credentials.")
    print("\nPress Ctrl+C at any time to cancel.")
    print("\n" + "-"*50)

    # Check if .env file already exists
    if os.path.exists(".env"):
        print("\n.env file already exists.")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != "y":
            print("Setup cancelled.")
            return

    # Create .env file
    env_vars = {}

    # Get API URL
    print("\n1. API Configuration")
    print("-"*50)

    # Get host
    default_host = "https://llm.chutes.ai/v1/chat/completions"
    host = input(f"Host URL [default: {default_host}]: ")
    host = host.strip() if host.strip() else default_host

    # Ensure the URL has the correct format
    if not host.endswith("/chat/completions"):
        if host.endswith("/v1"):
            host = f"{host}/chat/completions"
        elif not host.endswith("/"):
            host = f"{host}/v1/chat/completions"
        else:
            host = f"{host}v1/chat/completions"

    env_vars["CUSTOM_API_URL"] = host

    # Get API key
    api_key = input("API Key: ")
    while not api_key.strip():
        print("API Key is required.")
        api_key = input("API Key: ")

    env_vars["CUSTOM_API_KEY"] = api_key.strip()

    # Test connection
    print("\nTesting connection to API...")
    try:
        # Simple request to check if the API is accessible
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.get(
            host.replace("/chat/completions", ""),
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            print("Connection successful!")

            # Try to get available models
            try:
                models_url = host.replace("/chat/completions", "/models")
                models_response = requests.get(
                    models_url,
                    headers=headers,
                    timeout=10
                )

                available_models = []
                if models_response.status_code == 200:
                    models_data = models_response.json()
                    if "data" in models_data:
                        available_models = [model["id"] for model in models_data["data"]]
                        print(f"\nAvailable models: {len(available_models)}")
                        for i, model in enumerate(available_models[:10], 1):
                            print(f"{i}. {model}")
                        if len(available_models) > 10:
                            print(f"...and {len(available_models) - 10} more")
            except Exception as e:
                logger.error(f"Error getting models: {e}")
                available_models = []
        else:
            print(f"Connection failed with status {response.status_code}: {response.text}")
            available_models = []
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        print(f"Connection failed: {e}")
        available_models = []

    # Get model
    default_model = "RekaAI/reka-flash-3"

    if available_models:
        print("\nChoose a model:")
        for i, model in enumerate(available_models[:10], 1):
            print(f"{i}. {model}")
        print(f"Or enter a custom model name")

        model_choice = input(f"Model [default: {default_model}]: ")

        if model_choice.strip() and model_choice.isdigit():
            choice_idx = int(model_choice) - 1
            if 0 <= choice_idx < len(available_models):
                model = available_models[choice_idx]
            else:
                model = default_model
        elif model_choice.strip():
            model = model_choice.strip()
        else:
            model = default_model
    else:
        model = input(f"Model [default: {default_model}]: ")
        model = model.strip() if model.strip() else default_model

    env_vars["CUSTOM_API_MODEL"] = model

    # Get agent configuration
    print("\n2. Agent Configuration")
    print("-"*50)

    default_name = "Sujin"
    name = input(f"Agent Name [default: {default_name}]: ")
    env_vars["AGENT_NAME"] = name.strip() if name.strip() else default_name

    default_description = "AI Assistant powered by Sujin Agent Framework"
    description = input(f"Agent Description [default: {default_description}]: ")
    env_vars["AGENT_DESCRIPTION"] = description.strip() if description.strip() else default_description

    # Write to .env file
    print("\nWriting configuration to .env file...")

    with open(".env", "w") as f:
        f.write("# API Configuration\n")
        f.write(f"CUSTOM_API_URL={env_vars['CUSTOM_API_URL']}\n")
        f.write(f"CUSTOM_API_KEY={env_vars['CUSTOM_API_KEY']}\n")
        f.write(f"CUSTOM_API_MODEL={env_vars['CUSTOM_API_MODEL']}\n")
        f.write("\n# Agent Configuration\n")
        f.write(f"AGENT_NAME={env_vars['AGENT_NAME']}\n")
        f.write(f"AGENT_DESCRIPTION={env_vars['AGENT_DESCRIPTION']}\n")

    print("\nEnvironment setup complete!")
    print(f".env file created at {os.path.abspath('.env')}")
    print("\nYou can now run 'python sujin.py' to start the Sujin CLI.")
    print("="*50)

def run_cli():
    """Run the Sujin CLI."""
    # Create a custom theme for Rich
    custom_theme = Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "green",
        "agent": "bold blue",
        "user": "bold white",
        "system": "italic yellow",
        "metadata": "dim cyan",
        "highlight": "magenta",
    })

    # Create a console with the custom theme
    console = Console(theme=custom_theme)

    # Load environment variables
    load_dotenv()

    # Check required environment variables
    required_vars = ["CUSTOM_API_URL", "CUSTOM_API_KEY", "CUSTOM_API_MODEL"]
    if not check_required_env_vars(required_vars):
        console.print("\n[error]Missing required environment variables.[/error]")
        console.print("Run 'python sujin.py env' to set up your environment.")
        return 1

    # Get environment variables
    api_url = os.environ.get("CUSTOM_API_URL")
    api_key = os.environ.get("CUSTOM_API_KEY")
    model = os.environ.get("CUSTOM_API_MODEL")
    agent_name = os.environ.get("AGENT_NAME", "Sujin")

    # Clear the screen
    console.clear()

    # Display a welcome banner
    banner = """
    ╭───────────────────────────────────────────────╮
    │                                               │
    │   ███████╗██╗   ██╗     ██╗██╗███╗   ██╗     │
    │   ██╔════╝██║   ██║     ██║██║████╗  ██║     │
    │   ███████╗██║   ██║     ██║██║██╔██╗ ██║     │
    │   ╚════██║██║   ██║██   ██║██║██║╚██╗██║     │
    │   ███████║╚██████╔╝╚█████╔╝██║██║ ╚████║     │
    │   ╚══════╝ ╚═════╝  ╚════╝ ╚═╝╚═╝  ╚═══╝     │
    │                                               │
    │           Agent Framework CLI                 │
    │                                               │
    ╰───────────────────────────────────────────────╯
    """
    console.print(Panel(banner, border_style="agent"))

    # Create a table with agent information
    table = Table(box=box.ROUNDED, show_header=False, border_style="info")
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Agent Name", f"[agent]{agent_name}[/agent]")
    table.add_row("API Endpoint", f"[info]{api_url}[/info]")
    table.add_row("Model", f"[highlight]{model}[/highlight]")

    console.print(table)
    console.print("\n[system]Type 'exit' to quit. Type 'help' for available commands.[/system]\n")

    # Enhanced REPL
    while True:
        try:
            # Use Rich's Prompt for better input
            user_input = Prompt.ask("\n[bold white]>[/bold white]", console=console)

            # Handle special commands
            if user_input.lower() == "exit":
                console.print("\n[system]Exiting...[/system]")
                break
            elif user_input.lower() == "help":
                help_table = Table(title="Available Commands", box=box.ROUNDED, border_style="info")
                help_table.add_column("Command", style="bold")
                help_table.add_column("Description")

                help_table.add_row("exit", "Exit the CLI")
                help_table.add_row("help", "Show this help message")
                help_table.add_row("clear", "Clear the screen")
                help_table.add_row("env", "Show current environment")

                console.print(help_table)
                continue
            elif user_input.lower() == "env":
                env_table = Table(title="Environment", box=box.ROUNDED, border_style="info")
                env_table.add_column("Setting", style="bold")
                env_table.add_column("Value")

                env_table.add_row("API URL", f"[info]{api_url}[/info]")
                env_table.add_row("Model", f"[highlight]{model}[/highlight]")
                env_table.add_row("Agent Name", f"[agent]{agent_name}[/agent]")

                console.print(env_table)
                continue
            elif user_input.lower() == "clear":
                console.clear()
                # Re-display the banner and info
                console.print(Panel(banner, border_style="agent"))
                console.print(table)
                console.print("\n[system]Type 'exit' to quit. Type 'help' for available commands.[/system]\n")
                continue
            elif not user_input.strip():
                continue

            # Show user message
            console.print(f"\n[user]{user_input}[/user]")

            # Show thinking message with spinner
            with console.status("[info]Thinking...[/info]", spinner="dots"):
                # The actual processing happens here

            # Call the API
            response = call_api(
                prompt=user_input,
                api_url=api_url,
                api_key=api_key,
                model=model,
                max_tokens=1500  # Increased token limit for more complete responses
            )

            # Extract and print the response
            response_text = extract_response(response)

            # Clean up the response text
            import re

            # Simply remove any <reasoning> tags and their content
            cleaned_text = re.sub(r'<reasoning>.*?</reasoning>', '', response_text, flags=re.DOTALL)

            # Remove any <sep> tags and everything after them
            cleaned_text = re.sub(r'<sep>.*$', '', cleaned_text, flags=re.DOTALL)

            # If the response is empty after cleaning, provide a simple message
            if cleaned_text.strip() == "":
                cleaned_text = "I'm sorry, I couldn't generate a proper response."

            # Improve formatting for mathematical expressions
            # Replace LaTeX formatting with more readable symbols
            cleaned_text = re.sub(r'\\\(', '', cleaned_text)  # Remove \(
            cleaned_text = re.sub(r'\\\)', '', cleaned_text)  # Remove \)
            cleaned_text = re.sub(r'\\times', '×', cleaned_text)  # Replace \times with ×
            cleaned_text = re.sub(r'\\div', '÷', cleaned_text)  # Replace \div with ÷
            cleaned_text = re.sub(r'\\cdot', '·', cleaned_text)  # Replace \cdot with ·
            cleaned_text = re.sub(r'\\sqrt', '√', cleaned_text)  # Replace \sqrt with √
            cleaned_text = re.sub(r'\\pi', 'π', cleaned_text)  # Replace \pi with π
            cleaned_text = re.sub(r'\\boxed\{([^}]*)\}', r'\1', cleaned_text)  # Remove \boxed{}

            # Fix spacing around operators for better readability
            cleaned_text = re.sub(r'(\d)\s*([+\-×÷·])\s*(\d)', r'\1 \2 \3', cleaned_text)

            # Keep paragraph structure
            cleaned_text = cleaned_text.strip()

            # Format the response
            # Try to parse as markdown for better formatting
            try:
                md = Markdown(cleaned_text)
                console.print(Panel(md, title="[agent]Response[/agent]", border_style="agent", expand=False))
            except Exception:
                # If markdown parsing fails, fall back to simple panel
                console.print(Panel(cleaned_text, title="[agent]Response[/agent]", border_style="agent", expand=False))

            # Print usage information if available
            if "usage" in response:
                usage = response["usage"]
                usage_table = Table(box=box.SIMPLE, show_header=False, title="Usage", title_style="metadata")
                usage_table.add_column("Metric", style="metadata")
                usage_table.add_column("Value", style="metadata")

                usage_table.add_row(
                    "Tokens",
                    f"Total: {usage.get('total_tokens', 'N/A')} | "
                    f"Prompt: {usage.get('prompt_tokens', 'N/A')} | "
                    f"Completion: {usage.get('completion_tokens', 'N/A')}"
                )

                console.print(usage_table)

        except KeyboardInterrupt:
            console.print("\n[system]Exiting...[/system]")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            console.print(f"\n[error]Error: {e}[/error]")

    return 0

def main():
    """Main entry point for the CLI."""
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
        setup_environment()
        return 0
    elif args.command == "run" or args.command is None:
        return run_cli()
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
