"""
Environment setup wizard for the Sujin CLI.
"""

import os
import logging
import requests
from typing import Dict, Any
from .config import save_config
from .console import console

logger = logging.getLogger(__name__)

def setup_environment() -> int:
    """
    Set up the environment by creating a .env file.
    
    Returns:
        0 for success, 1 for failure
    """
    console.print("\n" + "="*50)
    console.print("[agent]Sujin Environment Setup Wizard[/agent]")
    console.print("="*50)
    console.print("\nThis wizard will help you set up your Sujin environment.")
    console.print("It will create a .env file with your API credentials.")
    console.print("\nPress Ctrl+C at any time to cancel.")
    console.print("\n" + "-"*50)
    
    try:
        # Check if .env file already exists
        if os.path.exists(".env"):
            console.print("\n[warning].env file already exists.[/warning]")
            overwrite = input("Do you want to overwrite it? (y/n): ").lower()
            if overwrite != "y":
                console.print("[warning]Setup cancelled.[/warning]")
                return 1
        
        # Create .env file
        env_vars = {}
        
        # Get API URL
        console.print("\n[agent]1. API Configuration[/agent]")
        console.print("-"*50)
        
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
            console.print("[error]API Key is required.[/error]")
            api_key = input("API Key: ")
        
        env_vars["CUSTOM_API_KEY"] = api_key.strip()
        
        # Test connection
        console.print("\n[info]Testing connection to API...[/info]")
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
                console.print("[success]Connection successful![/success]")
                
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
                            console.print(f"\n[info]Available models: {len(available_models)}[/info]")
                            for i, model in enumerate(available_models[:10], 1):
                                console.print(f"{i}. {model}")
                            if len(available_models) > 10:
                                console.print(f"...and {len(available_models) - 10} more")
                except Exception as e:
                    logger.error(f"Error getting models: {e}")
                    available_models = []
            else:
                console.print(f"[error]Connection failed with status {response.status_code}: {response.text}[/error]")
                available_models = []
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            console.print(f"[error]Connection failed: {e}[/error]")
            available_models = []
        
        # Get model
        default_model = "RekaAI/reka-flash-3"
        
        if available_models:
            console.print("\n[agent]Choose a model:[/agent]")
            for i, model in enumerate(available_models[:10], 1):
                console.print(f"{i}. {model}")
            console.print(f"Or enter a custom model name")
            
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
        console.print("\n[agent]2. Agent Configuration[/agent]")
        console.print("-"*50)
        
        default_name = "Sujin"
        name = input(f"Agent Name [default: {default_name}]: ")
        env_vars["AGENT_NAME"] = name.strip() if name.strip() else default_name
        
        default_description = "AI Assistant powered by Sujin Agent Framework"
        description = input(f"Agent Description [default: {default_description}]: ")
        env_vars["AGENT_DESCRIPTION"] = description.strip() if description.strip() else default_description
        
        # Write to .env file
        console.print("\n[info]Writing configuration to .env file...[/info]")
        save_config(env_vars)
        
        console.print("\n[success]Environment setup complete![/success]")
        console.print(f".env file created at {os.path.abspath('.env')}")
        console.print("\nYou can now run 'python sujin_cli.py' to start the Sujin CLI.")
        console.print("="*50)
        
        return 0
    except KeyboardInterrupt:
        console.print("\n\n[warning]Setup cancelled by user.[/warning]")
        return 1
    except Exception as e:
        logger.error(f"Error setting up environment: {e}")
        console.print(f"\n[error]Error setting up environment: {e}[/error]")
        return 1
