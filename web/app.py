"""
Flask application for the Sujin Agent Framework Web UI.
"""

import os
import sys
import logging
import requests
import subprocess
import time
import signal
import atexit
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

# Import and register workflow API blueprint
from web.workflow_api import workflow_api
app.register_blueprint(workflow_api)

# Get environment variables
AGENT_SERVICE_URL = os.environ.get("AGENT_SERVICE_URL", "http://localhost:5000")
AGENT_NAME = os.environ.get("AGENT_NAME", "Sujin")
AGENT_SERVICE_PORT = int(os.environ.get("AGENT_SERVICE_PORT", "5000"))

# Agent service process
agent_service_process = None

def start_agent_service():
    """Start the agent service as a subprocess."""
    global agent_service_process

    # Check if the service is already running
    if agent_service_process and agent_service_process.poll() is None:
        logger.info("Agent service is already running")
        return True

    # Check if another instance is running by trying to connect
    try:
        response = requests.get(f"{AGENT_SERVICE_URL}/api/status", timeout=2)
        if response.status_code == 200:
            logger.info("Agent service is already running externally")
            return True
    except requests.RequestException:
        # Service is not running, which is what we expect
        pass

    # Get the path to the agent service script
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_script = os.path.join(script_dir, "sujin_service.py")

    # Start the agent service
    try:
        # Use the same Python interpreter that's running this script
        python_executable = sys.executable

        # Start the process
        agent_service_process = subprocess.Popen(
            [python_executable, service_script, "--port", str(AGENT_SERVICE_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Register cleanup function
        atexit.register(stop_agent_service)

        # Wait for the service to start
        logger.info("Waiting for agent service to start...")
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{AGENT_SERVICE_URL}/api/status", timeout=2)
                if response.status_code == 200:
                    logger.info("Agent service started successfully")
                    return True
            except requests.RequestException:
                # Service not ready yet
                pass

            # Check if process has terminated
            if agent_service_process.poll() is not None:
                stdout, stderr = agent_service_process.communicate()
                logger.error(f"Agent service failed to start: {stderr}")
                return False

            # Wait before retrying
            time.sleep(1)

        logger.error(f"Timed out waiting for agent service to start after {max_retries} seconds")
        return False
    except Exception as e:
        logger.error(f"Error starting agent service: {e}")
        return False

def stop_agent_service():
    """Stop the agent service subprocess."""
    global agent_service_process

    if agent_service_process:
        logger.info("Stopping agent service...")
        try:
            # Try to terminate gracefully
            agent_service_process.terminate()

            # Wait for process to terminate
            try:
                agent_service_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                agent_service_process.kill()
                agent_service_process.wait()

            logger.info("Agent service stopped")
        except Exception as e:
            logger.error(f"Error stopping agent service: {e}")
        finally:
            agent_service_process = None

logger.info(f"Web UI configured to connect to agent service at {AGENT_SERVICE_URL}")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', agent_name=AGENT_NAME)

@app.route('/workflows')
def workflows():
    """Render the workflows page."""
    return render_template('workflows.html')

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
            "message": f"Error connecting to agent service: {str(e)}",
            "can_start": True  # Indicate that the service can be started
        })

@app.route('/api/service/start', methods=['POST'])
def start_service():
    """Start the agent service."""
    # Try to start the agent service
    if start_agent_service():
        # Check the status
        try:
            response = requests.get(f"{AGENT_SERVICE_URL}/api/status", timeout=5)
            if response.status_code == 200:
                return jsonify({
                    "success": True,
                    "message": "Agent service started successfully",
                    "status": response.json()
                })
        except requests.RequestException as e:
            logger.error(f"Error checking agent service status after starting: {e}")

        # If we couldn't get the status, still return success
        return jsonify({
            "success": True,
            "message": "Agent service started, but couldn't verify status"
        })
    else:
        return jsonify({
            "success": False,
            "message": "Failed to start agent service"
        }), 500

@app.route('/api/service/stop', methods=['POST'])
def stop_service():
    """Stop the agent service."""
    stop_agent_service()
    return jsonify({
        "success": True,
        "message": "Agent service stopped"
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
