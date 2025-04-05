#!/usr/bin/env python
"""
Test of just the MCP architecture without API calls.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sujin.core.models import Message, AgentInput, AgentOutput
from src.sujin.plugins.mcp.base import MCPModel, MCPController, MCPControllerConfig, MCPPlugin
from src.sujin.plugins.base import PluginConfig


# Define a simple MCP model
class SimpleTextModel(MCPModel):
    """Model for processing text."""
    content: str = Field(..., description="The content of the text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# Define a simple controller configuration
class TextFormatterConfig(MCPControllerConfig):
    """Configuration for the text formatter controller."""
    prefix: str = Field(default="[MCP] ", description="Prefix to add to the text")
    suffix: str = Field(default=" [Processed]", description="Suffix to add to the text")


# Define a simple controller
class TextFormatterController(MCPController[SimpleTextModel, TextFormatterConfig]):
    """Controller for formatting text."""
    
    @classmethod
    def get_default_config(cls) -> TextFormatterConfig:
        """Get the default configuration for the controller."""
        return TextFormatterConfig()
        
    @property
    def name(self) -> str:
        """Get the name of the controller."""
        return "text_formatter"
        
    @property
    def description(self) -> str:
        """Get the description of the controller."""
        return "Simple formatter that adds a prefix and suffix to text"
        
    def process(self, model: SimpleTextModel, context: Dict[str, Any]) -> SimpleTextModel:
        """
        Process the model by formatting the text.
        
        Args:
            model: The model to process
            context: Additional context for processing
            
        Returns:
            The processed model
        """
        # Add prefix and suffix
        model.content = f"{self.config.prefix}{model.content}{self.config.suffix}"
        
        # Add metadata
        model.metadata["processed_by"] = self.name
        
        return model


# Define a simple MCP plugin
class TextProcessingPlugin(MCPPlugin[SimpleTextModel, TextFormatterConfig]):
    """Plugin for processing text."""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """
        Initialize a new text processing plugin.
        
        Args:
            config: Configuration for the plugin
        """
        super().__init__(
            model_class=SimpleTextModel,
            controllers=[
                TextFormatterController()
            ],
            config=config
        )
        
    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return "text_processing_plugin"
        
    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        return "Simple plugin for processing text"
        
    def pre_process(self, input_data: AgentInput) -> AgentInput:
        """
        Pre-process the input data before it's passed to the agent.
        
        Args:
            input_data: The input data to pre-process
            
        Returns:
            The pre-processed input data
        """
        # This plugin doesn't modify input data
        return input_data
        
    def post_process(self, output_data: AgentOutput) -> AgentOutput:
        """
        Post-process the output data after it's generated by the agent.
        
        Args:
            output_data: The output data to post-process
            
        Returns:
            The post-processed output data
        """
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


def main():
    # Create the MCP plugin
    plugin = TextProcessingPlugin()
    
    # Create a sample output
    output = AgentOutput(
        message=Message(
            role="assistant",
            content="The capital of France is Paris."
        )
    )
    
    print("Original text:")
    print("-" * 50)
    print(output.message.content)
    print("-" * 50)
    
    # Process the output through the MCP plugin
    processed_output = plugin.post_process(output)
    
    print("\nProcessed text (after MCP):")
    print("-" * 50)
    print(processed_output.message.content)
    print("-" * 50)
    
    # Print metadata
    if processed_output.message.metadata:
        print("\nMetadata:")
        for key, value in processed_output.message.metadata.items():
            print(f"  {key}: {value}")
    
    print("\nMCP test completed successfully!")


if __name__ == "__main__":
    main()
