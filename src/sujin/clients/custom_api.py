"""
Custom API client for OpenAI-compatible APIs.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    user: Optional[str] = None


class CompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class CustomAPIClient:
    """Client for OpenAI-compatible APIs like OpenRouter."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        default_model: str = "gpt-3.5-turbo",
    ):
        """
        Initialize a new CustomAPIClient.
        
        Args:
            base_url: The base URL for the API (e.g., "https://openrouter.ai/api/v1")
            api_key: The API key for authentication
            default_model: The default model to use for completions
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            messages: The messages to generate a completion for
            model: The model to use (defaults to self.default_model)
            temperature: The temperature for sampling (0-2)
            max_tokens: The maximum number of tokens to generate
            top_p: The nucleus sampling parameter (0-1)
            frequency_penalty: The frequency penalty (-2 to 2)
            presence_penalty: The presence penalty (-2 to 2)
            stop: Sequences where the API will stop generating
            stream: Whether to stream the response
            user: A unique identifier for the end-user
            
        Returns:
            The completion response
        """
        url = f"{self.base_url}/chat/completions"
        
        # Convert messages to the expected format if needed
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                formatted_messages.append(msg)
            elif isinstance(msg, Message):
                formatted_messages.append(msg.dict())
            else:
                raise ValueError(f"Invalid message format: {msg}")
        
        data = {
            "model": model or self.default_model,
            "messages": formatted_messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if top_p is not None:
            data["top_p"] = top_p
        if frequency_penalty is not None:
            data["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            data["presence_penalty"] = presence_penalty
        if stop is not None:
            data["stop"] = stop
        if stream:
            data["stream"] = stream
        if user is not None:
            data["user"] = user
            
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=data,
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
        return response.json()


def create_openrouter_client(api_key: Optional[str] = None) -> CustomAPIClient:
    """
    Create a client for the OpenRouter API.
    
    Args:
        api_key: The API key for OpenRouter (defaults to OPENROUTER_API_KEY env var)
        
    Returns:
        A CustomAPIClient configured for OpenRouter
    """
    api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass api_key.")
        
    return CustomAPIClient(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_model="openai/gpt-3.5-turbo",  # OpenRouter uses model prefixes
    )


def sample_chat_completion(client: CustomAPIClient, prompt: str) -> str:
    """
    Generate a chat completion using the provided client.
    
    Args:
        client: The API client to use
        prompt: The user prompt
        
    Returns:
        The generated text
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat_completion(messages)
    
    # Extract the assistant's message
    if response and "choices" in response and len(response["choices"]) > 0:
        choice = response["choices"][0]
        if "message" in choice and "content" in choice["message"]:
            return choice["message"]["content"]
    
    return "No response generated."
