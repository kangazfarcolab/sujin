#!/usr/bin/env python
"""
Simple connectivity test for the custom API.
"""

import requests
import json
import sys

# API configuration
api_url = "https://llm.chutes.ai/v1/chat/completions"
api_key = "cpk_f7f99ca38d4444d7b3003e6537d93d2b.961c728be2eb57348e16013b23a8453a.JE3meZydUdd9ZGv3sFTI8IGa1YtJ78Kv"
model = "RekaAI/reka-flash-3"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Request data - extremely simple
data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "Hi"}
    ],
    "max_tokens": 5
}

print(f"Testing connectivity to {api_url}")
print(f"API Key: {api_key[:10]}...")
print(f"Model: {model}")
print(f"Request data: {json.dumps(data, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(
        api_url,
        headers=headers,
        json=data,
        timeout=10  # 10 second timeout
    )
    
    print(f"\nResponse status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Success! API is accessible.")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.Timeout:
    print("Error: Request timed out after 10 seconds")
except requests.exceptions.ConnectionError:
    print("Error: Connection error - could not connect to the API")
except Exception as e:
    print(f"Error: {e}")

print("\nTest completed.")
