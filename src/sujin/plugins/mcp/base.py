"""
Base classes for the Model-Controller-Plugin (MCP) architecture.
"""

from typing import Dict, List, Optional, Any, Type, Generic, TypeVar
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

from ...core.models import Message, AgentInput, AgentOutput
from ..base import Plugin, PluginConfig


# Type variables for the MCP architecture
M = TypeVar('M', bound=BaseModel)  # Model
C = TypeVar('C', bound=BaseModel)  # Controller config


class MCPModel(BaseModel):
    """Base model for MCP architecture."""
    pass


class MCPControllerConfig(BaseModel):
    """Configuration for an MCP controller."""
    enabled: bool = Field(default=True, description="Whether the controller is enabled")
    priority: int = Field(default=0, description="Priority of the controller (higher values run first)")


class MCPController(Generic[M, C], ABC):
    """Base controller for MCP architecture."""
    
    def __init__(self, config: Optional[C] = None):
        """
        Initialize a new MCP controller.
        
        Args:
            config: Configuration for the controller
        """
        self.config = config or self.get_default_config()
        
    @classmethod
    @abstractmethod
    def get_default_config(cls) -> C:
        """Get the default configuration for the controller."""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the controller."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the description of the controller."""
        pass
        
    @property
    def priority(self) -> int:
        """Get the priority of the controller."""
        return self.config.priority if hasattr(self.config, 'priority') else 0
        
    @property
    def enabled(self) -> bool:
        """Check if the controller is enabled."""
        return self.config.enabled if hasattr(self.config, 'enabled') else True
        
    @abstractmethod
    def process(self, model: M, context: Dict[str, Any]) -> M:
        """
        Process the model.
        
        Args:
            model: The model to process
            context: Additional context for processing
            
        Returns:
            The processed model
        """
        pass


class MCPPlugin(Plugin, Generic[M, C]):
    """Plugin that implements the MCP architecture."""
    
    def __init__(
        self, 
        model_class: Type[M],
        controllers: List[MCPController[M, C]] = None,
        config: Optional[PluginConfig] = None
    ):
        """
        Initialize a new MCP plugin.
        
        Args:
            model_class: The model class to use
            controllers: List of controllers to use
            config: Configuration for the plugin
        """
        super().__init__(config)
        self.model_class = model_class
        self.controllers = controllers or []
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the plugin."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Get the description of the plugin."""
        pass
        
    def add_controller(self, controller: MCPController[M, C]) -> None:
        """
        Add a controller to the plugin.
        
        Args:
            controller: The controller to add
        """
        self.controllers.append(controller)
        
    def remove_controller(self, controller_name: str) -> None:
        """
        Remove a controller from the plugin.
        
        Args:
            controller_name: The name of the controller to remove
        """
        self.controllers = [c for c in self.controllers if c.name != controller_name]
        
    def get_controller(self, controller_name: str) -> Optional[MCPController[M, C]]:
        """
        Get a controller by name.
        
        Args:
            controller_name: The name of the controller to get
            
        Returns:
            The controller, or None if it's not found
        """
        for controller in self.controllers:
            if controller.name == controller_name:
                return controller
        return None
        
    def create_model(self, **kwargs) -> M:
        """
        Create a new model instance.
        
        Args:
            **kwargs: Arguments to pass to the model constructor
            
        Returns:
            A new model instance
        """
        return self.model_class(**kwargs)
        
    def process_model(self, model: M, context: Dict[str, Any] = None) -> M:
        """
        Process a model using all controllers.
        
        Args:
            model: The model to process
            context: Additional context for processing
            
        Returns:
            The processed model
        """
        context = context or {}
        
        # Sort controllers by priority (highest first)
        sorted_controllers = sorted(
            [c for c in self.controllers if c.enabled],
            key=lambda c: c.priority,
            reverse=True
        )
        
        result = model
        for controller in sorted_controllers:
            result = controller.process(result, context)
            
        return result
        
    @abstractmethod
    def pre_process(self, input_data: AgentInput) -> AgentInput:
        """
        Pre-process the input data before it's passed to the agent.
        
        This method should be implemented by subclasses to use the MCP architecture.
        """
        pass
        
    @abstractmethod
    def post_process(self, output_data: AgentOutput) -> AgentOutput:
        """
        Post-process the output data after it's generated by the agent.
        
        This method should be implemented by subclasses to use the MCP architecture.
        """
        pass
