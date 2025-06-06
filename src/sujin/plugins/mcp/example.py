"""
Example implementation of the MCP architecture.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ...core.models import Message, AgentInput, AgentOutput
from ..base import PluginConfig
from .base import MCPModel, MCPController, MCPControllerConfig, MCPPlugin


class ExampleModel(MCPModel):
    """Example model for MCP architecture."""
    content: str = Field(..., description="Content to process")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ExampleControllerConfig(MCPControllerConfig):
    """Configuration for the example controller."""
    prefix: str = Field(default="[Example] ", description="Prefix to add to content")
    suffix: str = Field(default=" [End]", description="Suffix to add to content")


class ExampleController(MCPController[ExampleModel, ExampleControllerConfig]):
    """Example controller for MCP architecture."""
    
    @classmethod
    def get_default_config(cls) -> ExampleControllerConfig:
        """Get the default configuration for the controller."""
        return ExampleControllerConfig()
        
    @property
    def name(self) -> str:
        """Get the name of the controller."""
        return "example_controller"
        
    @property
    def description(self) -> str:
        """Get the description of the controller."""
        return "An example controller that adds a prefix and suffix to content"
        
    def process(self, model: ExampleModel, context: Dict[str, Any]) -> ExampleModel:
        """
        Process the model by adding a prefix and suffix to the content.
        
        Args:
            model: The model to process
            context: Additional context for processing
            
        Returns:
            The processed model
        """
        model.content = f"{self.config.prefix}{model.content}{self.config.suffix}"
        model.metadata["processed_by"] = self.name
        return model


class ExampleMCPPlugin(MCPPlugin[ExampleModel, ExampleControllerConfig]):
    """Example plugin that implements the MCP architecture."""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """
        Initialize a new example MCP plugin.
        
        Args:
            config: Configuration for the plugin
        """
        super().__init__(
            model_class=ExampleModel,
            controllers=[
                ExampleController()
            ],
            config=config
        )
        
    @property
    def name(self) -> str:
        """Get the name of the plugin."""
        return "example_mcp_plugin"
        
    @property
    def description(self) -> str:
        """Get the description of the plugin."""
        return "An example plugin that implements the MCP architecture"
        
    def pre_process(self, input_data: AgentInput) -> AgentInput:
        """
        Pre-process the input data before it's passed to the agent.
        
        Args:
            input_data: The input data to pre-process
            
        Returns:
            The pre-processed input data
        """
        # Extract the last user message
        last_user_message = None
        for message in reversed(input_data.messages):
            if message.role == "user":
                last_user_message = message
                break
                
        if last_user_message is None:
            return input_data
            
        # Create and process a model
        model = self.create_model(
            content=last_user_message.content,
            metadata={}
        )
        
        processed_model = self.process_model(
            model,
            context={"input_data": input_data}
        )
        
        # Update the message with the processed content
        last_user_message.content = processed_model.content
        if last_user_message.metadata is None:
            last_user_message.metadata = {}
        last_user_message.metadata.update(processed_model.metadata)
        
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
