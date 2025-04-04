# 수진 (Sujin) Agent Framework

A modern, flexible framework for building AI agents with Pydantic and MCP (Model-Controller-Plugin) architecture.

## Overview

Sujin (수진) is a comprehensive framework designed to simplify the development, deployment, and management of AI agents. It provides a structured approach to building agents that can perform a wide range of tasks, from simple automation to complex reasoning.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sujin.git
cd sujin

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Set Up Environment

Run the environment setup wizard to configure your API credentials:

```bash
python sujin.py env
```

This will guide you through setting up your environment variables, including:
- API URL
- API Key
- Model selection
- Agent configuration

### Run the CLI

```bash
python sujin.py
```

This will start the Sujin CLI, allowing you to interact with your agent.

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

## Usage

### Using the CLI

The Sujin CLI provides a simple interface for interacting with your agent:

```bash
# Start the CLI
python sujin.py

# Show available commands
> help

# Display current environment
> env

# Clear the screen
> clear

# Exit the CLI
> exit
```

### Using the Web UI

Sujin provides a web-based chat interface that connects to the agent service:

#### Step 1: Start the Agent Service

```bash
# Start the agent service
python sujin_service.py

# Specify a different port
python sujin_service.py --port 5001

# Run in debug mode
python sujin_service.py --debug
```

#### Step 2: Start the Web UI

```bash
# Start the web UI (default connects to service at http://localhost:5000)
python sujin_web.py

# Connect to a specific agent service URL
python sujin_web.py --service-url http://localhost:5001

# Specify a different port for the web UI
python sujin_web.py --port 8080

# Run in debug mode
python sujin_web.py --debug
```

Once started, you can access the web UI at http://localhost:8000 (or the port you specified).

#### Architecture

The web UI and agent service are separate components:

- **Agent Service**: Handles the AI logic and API communication
- **Web UI**: Provides a user-friendly interface to interact with the agent

This separation allows you to:
- Run the agent service on a different machine than the web UI
- Have multiple web UIs connect to the same agent service
- Update the web UI without restarting the agent service

### Using the API Client

You can use the custom API client to connect to OpenAI-compatible APIs:

```python
from src.sujin.clients.custom_api import CustomAPIClient

# Create a client for an OpenAI-compatible API
client = CustomAPIClient(
    base_url="https://your-api-url/v1/chat/completions",
    api_key="your-api-key",
    default_model="your-model"
)

# Generate a response
response = client.chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ],
    temperature=0.7,
    max_tokens=150
)

# Extract the response text
response_text = response["choices"][0]["message"]["content"]
print(response_text)
```

### Creating a Custom Agent

You can create your own agent by extending the base Agent class:

```python
from src.sujin.core.agent import Agent
from src.sujin.core.models import Message, AgentInput, AgentOutput
from src.sujin.tools.base import Tool

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

### Using the MCP Architecture

The Model-Controller-Plugin (MCP) architecture provides a structured way to process data:

```python
from src.sujin.plugins.mcp.base import MCPModel, MCPController, MCPControllerConfig, MCPPlugin
from src.sujin.plugins.base import PluginConfig
from pydantic import BaseModel, Field

# Define a model
class MyModel(MCPModel):
    content: str = Field(..., description="Content to process")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

# Define a controller configuration
class MyControllerConfig(MCPControllerConfig):
    prefix: str = Field(default="[MCP] ", description="Prefix to add to content")
    suffix: str = Field(default=" [End]", description="Suffix to add to content")

# Define a controller
class MyController(MCPController[MyModel, MyControllerConfig]):
    @classmethod
    def get_default_config(cls) -> MyControllerConfig:
        return MyControllerConfig()

    @property
    def name(self) -> str:
        return "my_controller"

    @property
    def description(self) -> str:
        return "A simple controller that adds a prefix and suffix to content"

    def process(self, model: MyModel, context: dict) -> MyModel:
        model.content = f"{self.config.prefix}{model.content}{self.config.suffix}"
        model.metadata["processed_by"] = self.name
        return model

# Define a plugin
class MyPlugin(MCPPlugin[MyModel, MyControllerConfig]):
    def __init__(self, config: PluginConfig = None):
        super().__init__(
            model_class=MyModel,
            controllers=[MyController()],
            config=config
        )

    @property
    def name(self) -> str:
        return "my_plugin"

    @property
    def description(self) -> str:
        return "A simple plugin that processes content"

    def pre_process(self, input_data: AgentInput) -> AgentInput:
        # Pre-process input data
        return input_data

    def post_process(self, output_data: AgentOutput) -> AgentOutput:
        # Post-process output data
        return output_data
```

See the `examples` directory for more detailed examples.

## License

MIT
