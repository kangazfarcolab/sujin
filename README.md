# 수진 (Sujin) Agent Framework

A modern, flexible framework for building AI agents with Pydantic and MCP (Model-Controller-Plugin) architecture.

## Overview

Sujin (수진) is a comprehensive framework designed to simplify the development, deployment, and management of AI agents. It provides a structured approach to building agents that can perform a wide range of tasks, from simple automation to complex reasoning.

## Features

- **Modular Architecture**: Easily extend and customize agent capabilities
- **Pydantic Integration**: Strong typing and validation with Pydantic models
- **MCP Architecture**: Model-Controller-Plugin pattern for flexible, extensible agents
- **Plugin System**: Dynamically discover and load plugins
- **Tool Integration**: Seamlessly connect with external tools and APIs
- **Memory Management**: Sophisticated systems for short and long-term memory
- **Planning & Reasoning**: Advanced planning capabilities for complex tasks

## Architecture

Sujin is built around several key components:

### Core

- **Agent**: The main agent class that processes inputs and generates outputs
- **Models**: Pydantic models for data validation and serialization

### Plugins

- **Plugin System**: A flexible plugin architecture for extending agent capabilities
- **MCP Architecture**: Model-Controller-Plugin pattern for organizing code
  - **Model**: Data structures using Pydantic
  - **Controller**: Business logic for processing models
  - **Plugin**: Integration with the agent framework

### Tools

- **Tool**: Interface for defining tools that agents can use
- **Tool Schema**: Automatic schema generation for tools

### Memory

- **Memory**: Systems for storing and retrieving information

### Planning

- **Planner**: Systems for creating and executing plans

## Getting Started

```python
from sujin.core.agent import Agent
from sujin.core.models import Message, AgentInput, AgentOutput
from sujin.tools.base import Tool

# Create a simple agent
class MyAgent(Agent):
    def __init__(self):
        super().__init__("MyAgent", "A simple example agent")

        # Add a tool
        self.add_tool(Tool(
            name="greet",
            description="Greet a user by name",
            func=self.greet
        ))

    def greet(self, name: str) -> str:
        """Greet a user by name."""
        return f"Hello, {name}!"

    def run(self, input_data: AgentInput) -> AgentOutput:
        # Process the input and return a response
        return AgentOutput(
            message=Message(
                role="assistant",
                content="Hello, world!"
            )
        )

# Create and use the agent
agent = MyAgent()
output = agent.process("Hello!")
print(output.message.content)
```

See the `examples` directory for more detailed examples.

## License

MIT
