#!/usr/bin/env python
"""
Test script for the MCP architecture in the Sujin framework.
"""

import os
import sys
import argparse
import logging

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.core.agent import Agent
from src.sujin.core.models import Message, AgentInput, AgentOutput, ToolCall
from src.sujin.tools.base import Tool
from src.sujin.plugins.mcp.example import ExampleMCPPlugin
from src.sujin.clients.custom_api import CustomAPIClient


class CustomAPIAgent(Agent):
    """An agent that uses a custom API for generating responses."""
    
    def __init__(
        self, 
        name="CustomAPIAgent",
        api_url="https://llm.chutes.ai/v1",
        api_key="cpk_f7f99ca38d4444d7b3003e6537d93d2b.961c728be2eb57348e16013b23a8453a.JE3meZydUdd9ZGv3sFTI8IGa1YtJ78Kv",
        model="RekaAI/reka-flash-3"
    ):
        super().__init__(name, "An agent that uses a custom API")
        
        # Create the API client
        self.client = CustomAPIClient(
            base_url=api_url,
            api_key=api_key,
            default_model=model
        )
        
        # Add some tools
        self.add_tool(Tool(
            name="echo",
            description="Echo a message back",
            func=self.echo
        ))
        
        # Register the example MCP plugin
        self.register_plugin(ExampleMCPPlugin())
    
    def echo(self, message: str) -> str:
        """Echo a message back.
        
        Args:
            message: The message to echo
            
        Returns:
            The same message
        """
        return message
    
    def run(self, input_data: AgentInput) -> AgentOutput:
        """Process the input and return a response.
        
        Args:
            input_data: The input data to process
            
        Returns:
            The agent's output
        """
        # Get all messages
        messages = []
        for msg in input_data.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # If no system message, add one
        if not any(msg["role"] == "system" for msg in messages):
            messages.insert(0, {
                "role": "system",
                "content": "You are a helpful assistant."
            })
        
        try:
            # Call the API
            response = self.client.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response
            if response and "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    content = choice["message"]["content"]
                    return AgentOutput(
                        message=Message(
                            role="assistant",
                            content=content
                        )
                    )
            
            # Fallback response if API call fails or returns unexpected format
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content="I'm sorry, I couldn't generate a response."
                )
            )
        except Exception as e:
            logging.error(f"Error calling API: {e}")
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content=f"I encountered an error: {str(e)}"
                )
            )


def main():
    parser = argparse.ArgumentParser(description='Test the MCP architecture')
    parser.add_argument('--api-key', default=os.environ.get('CUSTOM_API_KEY'),
                        help='API key for the custom host')
    parser.add_argument('--api-url', default=os.environ.get('CUSTOM_API_URL'),
                        help='URL for the custom host')
    parser.add_argument('--model', default=os.environ.get('CUSTOM_API_MODEL'),
                        help='Model to use')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Validate arguments
    if not args.api_key:
        args.api_key = "cpk_f7f99ca38d4444d7b3003e6537d93d2b.961c728be2eb57348e16013b23a8453a.JE3meZydUdd9ZGv3sFTI8IGa1YtJ78Kv"
        print(f"Using default API key: {args.api_key[:10]}...")
    
    if not args.api_url:
        args.api_url = "https://llm.chutes.ai/v1"
        print(f"Using default API URL: {args.api_url}")
    
    if not args.model:
        args.model = "RekaAI/reka-flash-3"
        print(f"Using default model: {args.model}")
    
    # Create the agent
    agent = CustomAPIAgent(
        api_url=args.api_url,
        api_key=args.api_key,
        model=args.model
    )
    
    print(f"Starting {agent.name}...")
    print("This agent uses the MCP architecture to process messages.")
    print("The ExampleMCPPlugin adds '[Example] ' prefix and ' [End]' suffix to messages.")
    print("Type 'exit' to quit.")
    
    # Simple REPL
    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            break
        
        # Process the input
        output = agent.process(user_input)
        print(f"\nResponse: {output.message.content}")


if __name__ == "__main__":
    main()
