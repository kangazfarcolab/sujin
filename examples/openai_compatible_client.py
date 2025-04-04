import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.clients.custom_api import CustomAPIClient

# Create a client for an OpenAI-compatible API
client = CustomAPIClient(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    default_model="openai/gpt-3.5-turbo"
)

# Example function that uses the client
def generate_response(prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    
    return response["choices"][0]["message"]["content"]

# Usage example
if __name__ == "__main__":
    user_prompt = "Explain quantum computing in simple terms."
    response_text = generate_response(user_prompt)
    print(f"Prompt: {user_prompt}")
    print(f"Response: {response_text}")
