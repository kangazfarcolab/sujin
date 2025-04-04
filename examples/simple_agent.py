"""
A simple example of using the Sujin framework to create an agent.
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.core.agent import Agent
from src.sujin.core.models import Message, AgentInput, AgentOutput, ToolCall
from src.sujin.tools.base import Tool
from src.sujin.plugins.mcp.example import ExampleMCPPlugin

# Set up logging
logging.basicConfig(level=logging.INFO)


class SimpleAgent(Agent):
    """A simple agent that can greet users and perform basic calculations."""

    def __init__(self, name="SimpleAgent"):
        super().__init__(name, "A simple agent that can greet and calculate")

        # Add some tools
        self.add_tool(Tool(
            name="greet",
            description="Greet a user by name",
            func=self.greet
        ))

        self.add_tool(Tool(
            name="add",
            description="Add two numbers",
            func=self.add
        ))

        # Register the example MCP plugin
        self.register_plugin(ExampleMCPPlugin())

    def greet(self, name: str) -> str:
        """Greet a user by name.

        Args:
            name: The name of the user to greet

        Returns:
            A greeting message
        """
        return f"Hello, {name}! I am {self.name}."

    def add(self, a: float, b: float) -> float:
        """Add two numbers.

        Args:
            a: The first number
            b: The second number

        Returns:
            The sum of the two numbers
        """
        return a + b

    def run(self, input_data: AgentInput) -> AgentOutput:
        """Process the input and return a response.

        Args:
            input_data: The input data to process

        Returns:
            The agent's output
        """
        # Get the last user message
        last_message = input_data.messages[-1] if input_data.messages else None
        if not last_message or last_message.role != "user":
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content="I didn't receive a user message."
                )
            )

        content = last_message.content

        # Process commands
        if content.startswith("greet "):
            name = content[6:]
            greeting = self.greet(name)
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content=greeting
                )
            )
        elif content.startswith("add "):
            try:
                parts = content[4:].split()
                a = float(parts[0])
                b = float(parts[1])
                result = self.add(a, b)
                return AgentOutput(
                    message=Message(
                        role="assistant",
                        content=f"The sum of {a} and {b} is {result}"
                    ),
                    tool_calls=[
                        ToolCall(
                            tool_name="add",
                            parameters={"a": a, "b": b}
                        )
                    ]
                )
            except (ValueError, IndexError):
                return AgentOutput(
                    message=Message(
                        role="assistant",
                        content="Please provide two numbers to add."
                    )
                )
        else:
            return AgentOutput(
                message=Message(
                    role="assistant",
                    content="I don't understand that command. Try 'greet [name]' or 'add [number] [number]'."
                )
            )


if __name__ == "__main__":
    # Create an agent
    agent = SimpleAgent()

    print(f"Starting {agent.name}...")
    print("Type 'exit' to quit.")

    # Simple REPL
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break

        # Process the input
        output = agent.process(user_input)
        print(output.message.content)
