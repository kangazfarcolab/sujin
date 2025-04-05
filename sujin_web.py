#!/usr/bin/env python
"""
Web UI for the Sujin Agent Framework.
"""

import os
import sys
import argparse
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the web UI."""
    parser = argparse.ArgumentParser(description="Sujin Web UI")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the web UI on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the web UI on")
    parser.add_argument("--service-url", type=str, help="URL of the agent service")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Set initial agent service URL for configuration
    if args.service_url:
        os.environ["AGENT_SERVICE_URL"] = args.service_url
    elif not os.environ.get("AGENT_SERVICE_URL"):
        # Default to localhost:5000 if not specified
        os.environ["AGENT_SERVICE_URL"] = "http://localhost:5000"

    # Get the path to the agent service script
    agent_service_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sujin_service.py")
    agent_service_port = int(os.environ.get("AGENT_SERVICE_PORT", "5000"))

    # Start the agent service
    print(f"Starting agent service on port {agent_service_port}...")
    import subprocess
    import atexit
    import time

    agent_service_process = subprocess.Popen(
        [sys.executable, agent_service_script, "--port", str(agent_service_port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Register cleanup function to stop agent service when web UI exits
    def stop_agent_service():
        if agent_service_process and agent_service_process.poll() is None:
            print("Stopping agent service...")
            agent_service_process.terminate()
            try:
                agent_service_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                agent_service_process.kill()
                agent_service_process.wait()
            print("Agent service stopped")

    atexit.register(stop_agent_service)

    # Set the final agent service URL
    agent_service_url = f"http://localhost:{agent_service_port}"
    os.environ["AGENT_SERVICE_URL"] = agent_service_url
    print(f"Waiting for agent service to start at {agent_service_url}...")

    # Wait for the agent service to start
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{agent_service_url}/api/status", timeout=2)
            if response.status_code == 200:
                print(f"Agent service started successfully")
                logger.info(f"Agent service is running at {agent_service_url}")
                break
        except requests.RequestException:
            # Service not ready yet
            pass

        # Check if process has terminated
        if agent_service_process.poll() is not None:
            stdout, stderr = agent_service_process.communicate()
            print(f"Agent service failed to start: {stderr}")
            break

        # Wait before retrying
        time.sleep(1)
        print(f"Waiting for agent service... ({i+1}/{max_retries})")

    # Agent service is now started automatically at the beginning

    # Initialize workflow engine
    from workflow.engine import WorkflowEngine
    workflow_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)
    workflow_engine = WorkflowEngine(storage_dir=workflow_dir)

    # Make workflow engine available to the app
    os.environ["WORKFLOW_DIR"] = workflow_dir

    # Import the Flask app
    from web.app import app

    # Add workflow engine to app context
    app.config["WORKFLOW_ENGINE"] = workflow_engine

    # Add agent service process to app context
    app.config["AGENT_SERVICE_PROCESS"] = agent_service_process

    # Run the app
    print(f"Starting Sujin Web UI on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

    return 0

if __name__ == "__main__":
    sys.exit(main())
