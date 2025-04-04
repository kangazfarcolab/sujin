"""
Client for Anthropic-compatible APIs.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class AnthropicMessage(BaseModel):
    role: str
    content: str


class AnthropicRequest(BaseModel):
    model: str
    messages: List[AnthropicMessage]
    max_tokens: int
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    stream: Optional[bool] = False


class AnthropicResponse(BaseModel):
    id: str
    type: str
    role: str
    content: List[Dict[str, Any]]
    model: str
    stop_reason: Optional[str] = None
    usage: Dict[str, int]


class CustomAnthropicClient:
    """Client for Anthropic-compatible APIs."""
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        default_model: str = "claude-2",
    ):
        """
        Initialize a new CustomAnthropicClient.
        
        Args:
            base_url: The base URL for the API
            api_key: The API key for authentication
            default_model: The default model to use
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests."""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
    def create_message(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a message using the Anthropic API.
        
        Args:
            messages: The messages to generate a response for
            model: The model to use (defaults to self.default_model)
            max_tokens: The maximum number of tokens to generate
            temperature: The temperature for sampling (0-1)
            top_p: The nucleus sampling parameter (0-1)
            top_k: The top-k sampling parameter
            stop_sequences: Sequences where the API will stop generating
            stream: Whether to stream the response
            
        Returns:
            The message response
        """
        url = f"{self.base_url}/messages"
        
        # Convert messages to the expected format if needed
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                formatted_messages.append(msg)
            elif isinstance(msg, AnthropicMessage):
                formatted_messages.append(msg.dict())
            else:
                raise ValueError(f"Invalid message format: {msg}")
        
        data = {
            "model": model or self.default_model,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if top_p is not None:
            data["top_p"] = top_p
        if top_k is not None:
            data["top_k"] = top_k
        if stop_sequences is not None:
            data["stop_sequences"] = stop_sequences
        if stream:
            data["stream"] = stream
            
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=data,
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
        return response.json()


def create_custom_anthropic_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> CustomAnthropicClient:
    """
    Create a client for a custom Anthropic-compatible API.
    
    Args:
        api_key: The API key (defaults to CUSTOM_ANTHROPIC_API_KEY env var)
        base_url: The base URL (defaults to CUSTOM_ANTHROPIC_URL env var)
        
    Returns:
        A CustomAnthropicClient
    """
    api_key = api_key or os.environ.get("CUSTOM_ANTHROPIC_API_KEY")
    base_url = base_url or os.environ.get("CUSTOM_ANTHROPIC_URL", "https://api.anthropic.com")
    
    if not api_key:
        raise ValueError("API key is required. Set CUSTOM_ANTHROPIC_API_KEY environment variable or pass api_key.")
        
    return CustomAnthropicClient(
        base_url=base_url,
        api_key=api_key,
        default_model="claude-2",
    )


def sample_anthropic_message(client: CustomAnthropicClient, prompt: str) -> str:
    """
    Generate a message using the provided client.
    
    Args:
        client: The API client to use
        prompt: The user prompt
        
    Returns:
        The generated text
    """
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    response = client.create_message(messages, max_tokens=500)
    
    # Extract the assistant's message
    if response and "content" in response:
        content_list = response["content"]
        if content_list and len(content_list) > 0:
            return content_list[0].get("text", "")
    
    return "No response generated."
