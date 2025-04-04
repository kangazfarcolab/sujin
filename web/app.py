"""
Flask application for the Sujin Agent Framework Web UI.
"""

import os
import logging
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

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
AGENT_SERVICE_URL = os.environ.get("AGENT_SERVICE_URL", "http://localhost:5000")
AGENT_NAME = os.environ.get("AGENT_NAME", "Sujin")

logger.info(f"Web UI configured to connect to agent service at {AGENT_SERVICE_URL}")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', agent_name=AGENT_NAME)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Proxy chat requests to the agent service."""
    try:
        # Forward the request to the agent service
        service_url = f"{AGENT_SERVICE_URL}/api/chat"
        logger.info(f"Forwarding chat request to agent service at {service_url}")

        # Send the request
        response = requests.post(
            service_url,
            json=request.json,
            timeout=60
        )

        # Return the response from the agent service
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logger.error(f"Error connecting to agent service: {e}")
        return jsonify({
            "error": f"Error connecting to agent service: {str(e)}"
        }), 500

@app.route('/api/status')
def status():
    """Proxy status request to the agent service."""
    try:
        # Forward the request to the agent service
        service_url = f"{AGENT_SERVICE_URL}/api/status"
        logger.info(f"Checking agent service status at {service_url}")

        # Send the request
        response = requests.get(service_url, timeout=10)

        # Return the response from the agent service
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logger.error(f"Error connecting to agent service: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error connecting to agent service: {str(e)}"
        })

@app.route('/api/config')
def config():
    """Get the configuration from the agent service and combine with local config."""
    try:
        # Forward the request to the agent service
        service_url = f"{AGENT_SERVICE_URL}/api/config"
        logger.info(f"Getting config from agent service at {service_url}")

        # Send the request
        response = requests.get(service_url, timeout=10)
        service_config = response.json()

        # Combine with local config
        config_data = {
            "agent_name": AGENT_NAME,
            "agent_service_url": AGENT_SERVICE_URL,
            "web_ui_version": "0.1.0"
        }

        # Add service config if available
        if response.status_code == 200:
            config_data.update(service_config)

        return jsonify(config_data)
    except requests.RequestException as e:
        logger.error(f"Error connecting to agent service: {e}")
        return jsonify({
            "agent_name": AGENT_NAME,
            "agent_service_url": AGENT_SERVICE_URL,
            "web_ui_version": "0.1.0",
            "service_error": str(e)
        })

def create_app():
    """Create and configure the Flask app."""
    return app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
