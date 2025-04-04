# API Client Documentation

The Sujin Agent Framework includes a custom API client that can connect to OpenAI-compatible APIs.

## Overview

The custom API client allows you to:

1. Connect to any OpenAI-compatible API endpoint
2. Send requests with custom parameters
3. Process responses in a standardized format

## Usage

### Basic Usage

```python
from src.sujin.clients.custom_api import CustomAPIClient

# Create a client
client = CustomAPIClient(
    base_url="https://your-api-url/v1/chat/completions",
    api_key="your-api-key",
    default_model="your-model"
)

# Generate a response
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ],
    temperature=0.7,
    max_tokens=150
)

# Extract the response text
response_text = response["choices"][0]["message"]["content"]
print(response_text)
```

### Available Parameters

The `chat_completion` method accepts the following parameters:

- `messages`: A list of message objects with `role` and `content` fields
- `model`: The model to use (defaults to the one specified when creating the client)
- `temperature`: Controls randomness (0-2, default: 0.7)
- `max_tokens`: Maximum number of tokens to generate
- `top_p`: Nucleus sampling parameter (0-1)
- `frequency_penalty`: Frequency penalty (-2 to 2)
- `presence_penalty`: Presence penalty (-2 to 2)
- `stop`: Sequences where the API will stop generating
- `stream`: Whether to stream the response
- `user`: A unique identifier for the end-user
- `timeout`: Timeout for the request in seconds

### Error Handling

The client includes error handling for common issues:

```python
try:
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
    )
except Exception as e:
    print(f"Error: {e}")
```

## Customizing the Client

You can customize the client by extending the `CustomAPIClient` class:

```python
class MyCustomClient(CustomAPIClient):
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        super().__init__(
            base_url="https://my-custom-api.com/v1/chat/completions",
            api_key=api_key,
            default_model=model
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Override to add custom headers."""
        headers = super()._get_headers()
        headers["X-Custom-Header"] = "custom-value"
        return headers
```

## Helper Functions

The framework includes helper functions for common use cases:

### Creating an OpenRouter Client

```python
from src.sujin.clients.custom_api import create_openrouter_client

# Create a client for OpenRouter
client = create_openrouter_client(api_key="your-openrouter-api-key")
```

### Sample Chat Completion

```python
from src.sujin.clients.custom_api import sample_chat_completion, create_openrouter_client

# Create a client
client = create_openrouter_client(api_key="your-openrouter-api-key")

# Generate a completion
response_text = sample_chat_completion(client, "Tell me a joke")
print(response_text)
```

## Supported API Endpoints

The client has been tested with the following API endpoints:

- OpenAI API
- OpenRouter
- Custom endpoints (e.g., llm.chutes.ai)

For other endpoints, you may need to adjust the URL format or authentication method.
