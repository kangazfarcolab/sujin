"""
API client wrapper for the Sujin CLI.
"""

import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

def call_api(
    prompt: str,
    api_url: str,
    api_key: str,
    model: str,
    system_message: str = "You are a helpful assistant.",
    max_tokens: int = 1500
) -> Dict[str, Any]:
    """
    Call the API with the given prompt.
    
    Args:
        prompt: The user prompt
        api_url: The API URL
        api_key: The API key
        model: The model to use
        system_message: The system message
        max_tokens: Maximum number of tokens to generate
        
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
        "max_tokens": max_tokens
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
