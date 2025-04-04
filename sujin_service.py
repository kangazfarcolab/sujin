#!/usr/bin/env python
"""
Service API for the Sujin Agent Framework.
"""

import os
import sys
import argparse
import logging
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import from Sujin
from src.sujin.clients.custom_api import CustomAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Global variables
api_client = None
agent_name = "Sujin"

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    if not api_client:
        return jsonify({
            "error": "Agent service not configured. Please set up environment variables."
        }), 500
    
    # Get request data
    data = request.json
    message = data.get('message', '')
    conversation_history = data.get('history', [])
    
    # Prepare messages for the API
    messages = []
    
    # Add system message if not present
    if not any(msg.get('role') == 'system' for msg in conversation_history):
        messages.append({
            "role": "system",
            "content": f"You are {agent_name}, a helpful AI assistant."
        })
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add the new message
    messages.append({
        "role": "user",
        "content": message
    })
    
    try:
        # Call the API
        logger.info(f"Calling API with message: {message}")
        response = api_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract the response
        if response and "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                
                # Create response object
                response_obj = {
                    "message": content,
                    "role": "assistant"
                }
                
                # Add usage information if available
                if "usage" in response:
                    response_obj["usage"] = response["usage"]
                
                return jsonify(response_obj)
        
        return jsonify({
            "error": "Failed to get response from API",
            "raw_response": response
        }), 500
    except Exception as e:
        logger.error(f"Error calling API: {e}")
        return jsonify({
            "error": f"Error calling API: {str(e)}"
        }), 500

@app.route('/api/status')
def status():
    """Check the status of the API."""
    if not api_client:
        return jsonify({
            "status": "error",
            "message": "Agent service not configured. Please set up environment variables."
        })
    
    try:
        # Make a simple request to check if the API is accessible
        response = api_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=10
        )
        
        if response and "choices" in response:
            return jsonify({
                "status": "ok",
                "message": "Agent service is running",
                "model": api_client.default_model
            })
        else:
            return jsonify({
                "status": "error",
                "message": "API returned an invalid response",
                "raw_response": response
            })
    except Exception as e:
        logger.error(f"Error checking API status: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error checking API status: {str(e)}"
        })

@app.route('/api/config')
def config():
    """Get the configuration."""
    return jsonify({
        "agent_name": agent_name,
        "model": api_client.default_model if api_client else None,
        "service_configured": api_client is not None
    })

def initialize_service():
    """Initialize the agent service."""
    global api_client, agent_name
    
    # Load environment variables
    load_dotenv()
    
    # Get environment variables
    api_url = os.environ.get("CUSTOM_API_URL")
    api_key = os.environ.get("CUSTOM_API_KEY")
    model = os.environ.get("CUSTOM_API_MODEL")
    agent_name = os.environ.get("AGENT_NAME", "Sujin")
    
    # Create API client
    if api_url and api_key and model:
        api_client = CustomAPIClient(
            base_url=api_url,
            api_key=api_key,
            default_model=model
        )
        logger.info(f"Initialized agent service with model {model}")
        return True
    else:
        logger.warning("Agent service not initialized. Missing environment variables.")
        return False

def main():
    """Main entry point for the agent service."""
    parser = argparse.ArgumentParser(description="Sujin Agent Service")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the service on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the service on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    # Initialize the service
    if not initialize_service():
        logger.error("Failed to initialize agent service")
        print("Error: Failed to initialize agent service. Check environment variables.")
        print("Run 'python sujin.py env' to set up your environment.")
        return 1
    
    # Run the app
    print(f"Starting Sujin Agent Service on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
