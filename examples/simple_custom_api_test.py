#!/usr/bin/env python
"""
Simple test script for using a custom API host.
"""

import os
import sys
import requests
import json

# API configuration
api_url = "https://llm.chutes.ai/v1/chat/completions"
api_key = "cpk_f7f99ca38d4444d7b3003e6537d93d2b.961c728be2eb57348e16013b23a8453a.JE3meZydUdd9ZGv3sFTI8IGa1YtJ78Kv"
model = "RekaAI/reka-flash-3"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Request data
data = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, who are you?"}
    ],
    "temperature": 0.7,
    "max_tokens": 150
}

# Make the request
print(f"Sending request to {api_url}...")
print(f"Using model: {model}")
print("Waiting for response...\n")

try:
    response = requests.post(
        api_url,
        headers=headers,
        json=data,
        timeout=30  # 30 second timeout
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        
        # Extract and print the response
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                print("Response:")
                print("-" * 50)
                print(choice["message"]["content"])
                print("-" * 50)
                
                # Print usage information if available
                if "usage" in result:
                    usage = result["usage"]
                    print(f"\nTokens used: {usage.get('total_tokens', 'N/A')} "
                          f"(Prompt: {usage.get('prompt_tokens', 'N/A')}, "
                          f"Completion: {usage.get('completion_tokens', 'N/A')})")
            else:
                print("Error: Unexpected response format (no message content)")
                print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("Error: Unexpected response format")
            print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("Error: Request timed out after 30 seconds")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
