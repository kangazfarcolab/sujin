"""
Example of using the custom API client.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.clients.custom_api import create_openrouter_client, sample_chat_completion

# Load environment variables from .env file
load_dotenv()

def main():
    # Create an OpenRouter client
    client = create_openrouter_client()
    
    # Generate a completion
    prompt = "Explain the concept of artificial intelligence in one paragraph."
    response = sample_chat_completion(client, prompt)
    
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    
    # Example with custom parameters
    custom_prompt = "Write a haiku about programming."
    custom_response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a creative writing assistant."},
            {"role": "user", "content": custom_prompt}
        ],
        temperature=0.9,
        max_tokens=50
    )
    
    assistant_message = custom_response["choices"][0]["message"]["content"]
    print(f"\nCustom Prompt: {custom_prompt}")
    print(f"Custom Response: {assistant_message}")

if __name__ == "__main__":
    main()
