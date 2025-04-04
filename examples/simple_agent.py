"""
A simple example of using the Sujin framework to create an agent.
"""

import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.core.agent import Agent
from src.sujin.tools.base import Tool


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
    
    def greet(self, name):
        """Greet a user by name."""
        return f"Hello, {name}! I am {self.name}."
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def run(self, input_data):
        """Process the input and return a response."""
        if input_data.startswith("greet "):
            name = input_data[6:]
            return self.greet(name)
        elif input_data.startswith("add "):
            try:
                parts = input_data[4:].split()
                a = float(parts[0])
                b = float(parts[1])
                return f"The sum of {a} and {b} is {self.add(a, b)}"
            except (ValueError, IndexError):
                return "Please provide two numbers to add."
        else:
            return "I don't understand that command. Try 'greet [name]' or 'add [number] [number]'."


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
        
        response = agent.run(user_input)
        print(response)
