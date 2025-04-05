# MCP Architecture Documentation

The Model-Controller-Plugin (MCP) architecture is a core feature of the Sujin Agent Framework, providing a structured approach to processing data.

## Overview

The MCP architecture consists of three main components:

1. **Model**: Data structures using Pydantic
2. **Controller**: Business logic for processing models
3. **Plugin**: Integration with the agent framework

This architecture allows for:

- Separation of concerns
- Reusable components
- Extensible processing pipelines
- Type safety with Pydantic

## Components

### Model

Models are Pydantic classes that define the structure of data:

```python
from pydantic import BaseModel, Field
from src.sujin.plugins.mcp.base import MCPModel

class MyModel(MCPModel):
    content: str = Field(..., description="Content to process")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
```

### Controller

Controllers contain the business logic for processing models:

```python
from src.sujin.plugins.mcp.base import MCPController, MCPControllerConfig
from pydantic import Field

class MyControllerConfig(MCPControllerConfig):
    prefix: str = Field(default="[MCP] ", description="Prefix to add to content")
    suffix: str = Field(default=" [End]", description="Suffix to add to content")

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
```

### Plugin

Plugins integrate controllers with the agent framework:

```python
from src.sujin.plugins.mcp.base import MCPPlugin
from src.sujin.plugins.base import PluginConfig
from src.sujin.core.models import AgentInput, AgentOutput

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

## Usage

### Registering a Plugin with an Agent

```python
from src.sujin.core.agent import Agent
from my_plugins import MyPlugin

# Create an agent
agent = Agent("MyAgent", "An agent with MCP")

# Register the plugin
agent.register_plugin(MyPlugin())
```

### Processing Flow

1. When an agent receives input, it calls `process`
2. The `process` method calls `plugin_manager.run_pre_process`
3. Each plugin's `pre_process` method is called
4. The agent processes the modified input
5. The `process` method calls `plugin_manager.run_post_process`
6. Each plugin's `post_process` method is called
7. The agent returns the processed output

## Example: Text Processing Plugin

Here's a complete example of a plugin that processes text:

```python
from src.sujin.plugins.mcp.base import MCPModel, MCPController, MCPControllerConfig, MCPPlugin
from src.sujin.plugins.base import PluginConfig
from src.sujin.core.models import Message, AgentInput, AgentOutput
from pydantic import BaseModel, Field
from typing import Dict, Any

# Define a model for text processing
class TextModel(MCPModel):
    content: str = Field(..., description="Text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata")

# Define a controller configuration
class TextFormatterConfig(MCPControllerConfig):
    prefix: str = Field(default="[Bot] ", description="Prefix to add")
    suffix: str = Field(default="", description="Suffix to add")

# Define a controller for formatting text
class TextFormatterController(MCPController[TextModel, TextFormatterConfig]):
    @classmethod
    def get_default_config(cls) -> TextFormatterConfig:
        return TextFormatterConfig()
        
    @property
    def name(self) -> str:
        return "text_formatter"
        
    @property
    def description(self) -> str:
        return "Formats text by adding a prefix and suffix"
        
    def process(self, model: TextModel, context: Dict[str, Any]) -> TextModel:
        model.content = f"{self.config.prefix}{model.content}{self.config.suffix}"
        model.metadata["formatted"] = True
        return model

# Define a plugin for text processing
class TextProcessingPlugin(MCPPlugin[TextModel, TextFormatterConfig]):
    def __init__(self, config: Optional[PluginConfig] = None):
        super().__init__(
            model_class=TextModel,
            controllers=[TextFormatterController()],
            config=config
        )
        
    @property
    def name(self) -> str:
        return "text_processing_plugin"
        
    @property
    def description(self) -> str:
        return "Processes text using the MCP architecture"
        
    def pre_process(self, input_data: AgentInput) -> AgentInput:
        # This plugin doesn't modify input data
        return input_data
        
    def post_process(self, output_data: AgentOutput) -> AgentOutput:
        # Create and process a model
        model = self.create_model(
            content=output_data.message.content,
            metadata=output_data.message.metadata or {}
        )
        
        processed_model = self.process_model(
            model,
            context={"output_data": output_data}
        )
        
        # Update the message with the processed content
        output_data.message.content = processed_model.content
        if output_data.message.metadata is None:
            output_data.message.metadata = {}
        output_data.message.metadata.update(processed_model.metadata)
        
        return output_data
```

## Best Practices

1. **Keep Models Simple**: Models should represent data structures, not behavior
2. **Single Responsibility**: Each controller should have a single responsibility
3. **Composability**: Design controllers to be composable
4. **Type Safety**: Use Pydantic for type validation
5. **Error Handling**: Handle errors gracefully in controllers
6. **Testing**: Write tests for models, controllers, and plugins
7. **Documentation**: Document the purpose and behavior of each component
