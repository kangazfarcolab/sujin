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
    system_message: str = "You are a helpful assistant."
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
        "max_tokens": 500
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
    # Load environment variables
    load_dotenv()

    # Check required environment variables
    required_vars = ["CUSTOM_API_URL", "CUSTOM_API_KEY", "CUSTOM_API_MODEL"]
    if not check_required_env_vars(required_vars):
        print("\nRun 'python sujin.py env' to set up your environment.")
        return 1

    # Get environment variables
    api_url = os.environ.get("CUSTOM_API_URL")
    api_key = os.environ.get("CUSTOM_API_KEY")
    model = os.environ.get("CUSTOM_API_MODEL")
    agent_name = os.environ.get("AGENT_NAME", "Sujin")

    # Print welcome message
    print("\n" + "="*50)
    print(f"{agent_name} CLI")
    print("="*50)
    print(f"API URL: {api_url}")
    print(f"Model: {model}")
    print("\nType 'exit' to quit.")
    print("Type 'help' for available commands.")
    print("-"*50)

    # Simple REPL
    while True:
        try:
            user_input = input("\n> ")

            # Handle special commands
            if user_input.lower() == "exit":
                break
            elif user_input.lower() == "help":
                print("\nAvailable commands:")
                print("  exit - Exit the CLI")
                print("  help - Show this help message")
                print("  env - Show current environment")
                print("  clear - Clear the screen")
                # Removed calc command as we're letting the AI handle all expressions
                continue
            elif user_input.lower() == "env":
                print("\nCurrent environment:")
                print(f"  API URL: {api_url}")
                print(f"  Model: {model}")
                print(f"  Agent Name: {agent_name}")
                continue
            elif user_input.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            elif user_input.lower().startswith("calc "):
                # Handle mathematical expressions directly
                try:
                    expression = user_input[5:].strip()
                    # Replace ^ with ** for exponentiation
                    expression = expression.replace("^", "**")
                    # Safely evaluate the expression
                    import math
                    # Define a safe namespace for evaluation
                    safe_dict = {
                        'abs': abs, 'round': round,
                        'min': min, 'max': max,
                        'sum': sum, 'len': len,
                        'pow': pow, 'round': round,
                        'int': int, 'float': float,
                        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                        'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
                        'sqrt': math.sqrt, 'log': math.log, 'log10': math.log10,
                        'pi': math.pi, 'e': math.e
                    }
                    result = eval(expression, {"__builtins__": {}}, safe_dict)

                    # Format the result
                    print("\nCalculation:")
                    print("-" * 80)
                    print(f"Expression: {expression}")
                    print(f"Result: {result}")

                    # For complex expressions, show the steps
                    if any(op in expression for op in ["+", "-", "*", "/", "**", "(", ")"]):
                        print("\nOrder of operations:")
                        # This is a simplified explanation - for complex expressions,
                        # we'd need a proper parser to show the exact steps
                        print("1. Evaluate expressions inside parentheses")
                        print("2. Evaluate exponents (^)")
                        print("3. Perform multiplication and division from left to right")
                        print("4. Perform addition and subtraction from left to right")

                    print("-" * 80)
                except Exception as e:
                    print(f"\nError calculating expression: {e}")
                    print("Try using the 'calc' command with a valid mathematical expression.")
                    print("Example: calc 2 + 2 * 3")
                continue
            elif not user_input.strip():
                continue

            print("Thinking...")

            # Call the API
            response = call_api(
                prompt=user_input,
                api_url=api_url,
                api_key=api_key,
                model=model
            )

            # Extract and print the response
            response_text = extract_response(response)

            # Clean up the response text
            import re
            # Remove any <reasoning> tags and their content
            cleaned_text = re.sub(r'<reasoning>.*?</reasoning>', '', response_text, flags=re.DOTALL)
            # Remove any <sep> tags and everything after them
            cleaned_text = re.sub(r'<sep>.*$', '', cleaned_text, flags=re.DOTALL)

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
            print("\nResponse:")
            print("-" * 80)

            # Preserve the structure of the response
            # Split by double newlines to get paragraphs
            paragraphs = cleaned_text.split("\n\n")
            for paragraph in paragraphs:
                # Split by single newlines to get lines within paragraphs
                lines = paragraph.split("\n")
                for line in lines:
                    print(line.strip())
                # Add a blank line between paragraphs
                if len(paragraphs) > 1:
                    print()

            print("-" * 80)

            # Print usage information if available
            if "usage" in response:
                usage = response["usage"]
                print(f"\nTokens used: {usage.get('total_tokens', 'N/A')} "
                      f"(Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                      f"Completion: {usage.get('completion_tokens', 'N/A')})")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")

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
