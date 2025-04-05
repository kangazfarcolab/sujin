#!/usr/bin/env python
"""
Test script for using a custom API host with the Sujin framework.
"""

import os
import sys
import argparse

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.clients.custom_api import CustomAPIClient


def main():
    parser = argparse.ArgumentParser(description='Test a custom API host')
    parser.add_argument('--api-key', default=os.environ.get('CUSTOM_API_KEY'),
                        help='API key for the custom host')
    parser.add_argument('--api-url', default=os.environ.get('CUSTOM_API_URL'),
                        help='URL for the custom host')
    parser.add_argument('--model', default=os.environ.get('CUSTOM_API_MODEL'),
                        help='Model to use')
    parser.add_argument('--prompt', default='Explain quantum computing in simple terms.',
                        help='Prompt to send to the API')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.api_key:
        args.api_key = "cpk_f7f99ca38d4444d7b3003e6537d93d2b.961c728be2eb57348e16013b23a8453a.JE3meZydUdd9ZGv3sFTI8IGa1YtJ78Kv"
        print(f"Using default API key: {args.api_key[:10]}...")
    
    if not args.api_url:
        args.api_url = "https://llm.chutes.ai/v1"
        print(f"Using default API URL: {args.api_url}")
    
    if not args.model:
        args.model = "RekaAI/reka-flash-3"
        print(f"Using default model: {args.model}")
    
    # Create the client
    client = CustomAPIClient(
        base_url=args.api_url,
        api_key=args.api_key,
        default_model=args.model
    )
    
    print(f"\nSending prompt: '{args.prompt}'")
    print("Waiting for response...\n")
    
    try:
        # Call the API
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": args.prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and print the response
        if response and "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                print("Response:")
                print("-" * 50)
                print(choice["message"]["content"])
                print("-" * 50)
                
                # Print usage information if available
                if "usage" in response:
                    usage = response["usage"]
                    print(f"\nTokens used: {usage.get('total_tokens', 'N/A')} "
                          f"(Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                          f"Completion: {usage.get('completion_tokens', 'N/A')})")
            else:
                print("Error: Unexpected response format (no message content)")
                print(f"Response: {response}")
        else:
            print("Error: Unexpected response format")
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error calling API: {e}")


if __name__ == "__main__":
    main()
