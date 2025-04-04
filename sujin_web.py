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

    # Set agent service URL
    if args.service_url:
        os.environ["AGENT_SERVICE_URL"] = args.service_url
    elif not os.environ.get("AGENT_SERVICE_URL"):
        # Default to localhost:5000 if not specified
        os.environ["AGENT_SERVICE_URL"] = "http://localhost:5000"

    service_url = os.environ.get("AGENT_SERVICE_URL")
    logger.info(f"Using agent service at {service_url}")

    # Check if agent service is running
    try:
        response = requests.get(f"{service_url}/api/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            if status_data.get("status") == "ok":
                logger.info(f"Agent service is running at {service_url}")
                print(f"Agent service is running at {service_url}")
            else:
                logger.warning(f"Agent service returned status: {status_data.get('message')}")
                print(f"Warning: Agent service returned status: {status_data.get('message')}")
        else:
            logger.warning(f"Agent service returned status code: {response.status_code}")
            print(f"Warning: Agent service returned status code: {response.status_code}")
    except requests.RequestException as e:
        logger.warning(f"Could not connect to agent service at {service_url}: {e}")
        print(f"Warning: Could not connect to agent service at {service_url}")
        print("The web UI will still start, but you'll need to start the agent service separately.")
        print(f"Run 'python sujin_service.py' to start the agent service.")

    # Import the Flask app
    from web.app import app

    # Run the app
    print(f"Starting Sujin Web UI on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

    return 0

if __name__ == "__main__":
    sys.exit(main())
