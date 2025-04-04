"""
Flask application for the Sujin Agent Framework.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
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

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Get environment variables
API_URL = os.environ.get("CUSTOM_API_URL")
API_KEY = os.environ.get("CUSTOM_API_KEY")
MODEL = os.environ.get("CUSTOM_API_MODEL")
AGENT_NAME = os.environ.get("AGENT_NAME", "Sujin")

# Create API client
api_client = None
if API_URL and API_KEY and MODEL:
    api_client = CustomAPIClient(
        base_url=API_URL,
        api_key=API_KEY,
        default_model=MODEL
    )
    logger.info(f"Created API client for {API_URL} with model {MODEL}")
else:
    logger.warning("API client not created. Missing environment variables.")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', agent_name=AGENT_NAME)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    if not api_client:
        return jsonify({
            "error": "API client not configured. Please set up environment variables."
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
            "content": f"You are {AGENT_NAME}, a helpful AI assistant."
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
            "message": "API client not configured. Please set up environment variables."
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
                "message": "API is accessible",
                "model": MODEL
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
        "agent_name": AGENT_NAME,
        "api_url": API_URL,
        "model": MODEL,
        "api_configured": api_client is not None
    })

def create_app():
    """Create and configure the Flask app."""
    return app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
