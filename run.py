#!/usr/bin/env python
"""
Minimal working CLI for the Sujin Agent Framework.
"""

import os
import sys
import argparse
import logging
import requests
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# Load environment variables from .env file
load_dotenv()

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
        print("See .env.example for an example.")
        return False
    
    return True

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Sujin Agent Framework CLI")
    
    # Basic configuration
    parser.add_argument("--api-url", default=os.environ.get("CUSTOM_API_URL"), 
                        help="URL for the custom API")
    parser.add_argument("--api-key", default=os.environ.get("CUSTOM_API_KEY"), 
                        help="API key for the custom API")
    parser.add_argument("--model", default=os.environ.get("CUSTOM_API_MODEL"), 
                        help="Model to use with the API")
    parser.add_argument("--verbose", action="store_true", 
                        help="Enable verbose logging")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Check required environment variables
    required_vars = ["CUSTOM_API_URL", "CUSTOM_API_KEY", "CUSTOM_API_MODEL"]
    if not (args.api_url and args.api_key and args.model):
        if not check_required_env_vars(required_vars):
            return 1
    
    # Use command line arguments if provided
    api_url = args.api_url or os.environ.get("CUSTOM_API_URL")
    api_key = args.api_key or os.environ.get("CUSTOM_API_KEY")
    model = args.model or os.environ.get("CUSTOM_API_MODEL")
    
    # Print welcome message
    print(f"Sujin Agent Framework CLI")
    print(f"API URL: {api_url}")
    print(f"Model: {model}")
    print("Type 'exit' to quit.")
    print()
    
    # Simple REPL
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() == "exit":
                break
            
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
            print("\nResponse:")
            print("-" * 80)
            print(response_text)
            print("-" * 80)
            
            # Print usage information if available
            if "usage" in response:
                usage = response["usage"]
                print(f"\nTokens used: {usage.get('total_tokens', 'N/A')} "
                      f"(Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                      f"Completion: {usage.get('completion_tokens', 'N/A')})")
            
            print()
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
