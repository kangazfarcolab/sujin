#!/usr/bin/env python
"""
Web UI for the Sujin Agent Framework.
"""

import os
import sys
import argparse
import logging
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
    parser.add_argument("--port", type=int, default=5000, help="Port to run the web UI on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the web UI on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["CUSTOM_API_URL", "CUSTOM_API_KEY", "CUSTOM_API_MODEL"]
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in a .env file or as environment variables.")
        print("Run 'python sujin.py env' to set up your environment.")
        return 1
    
    # Import the Flask app
    from web.app import app
    
    # Run the app
    print(f"Starting Sujin Web UI on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
