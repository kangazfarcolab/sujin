"""
Data models for workflows and components.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
import uuid


class ComponentType(str, Enum):
    """Type of component in a workflow."""
    AGENT = "agent"
    PLUGIN = "plugin"
    DATA_SOURCE = "data_source"
    INPUT = "input"
    OUTPUT = "output"


class ConnectionType(str, Enum):
    """Type of connection between components."""
    DATA = "data"  # Data flow
    CONTROL = "control"  # Control flow
    CONTEXT = "context"  # Context sharing


class Component(BaseModel):
    """Base model for a workflow component."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: ComponentType
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Position in the workflow canvas
    position_x: float = 0
    position_y: float = 0
    
    class Config:
        use_enum_values = True


class Connection(BaseModel):
    """Connection between two components in a workflow."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None
    type: ConnectionType = ConnectionType.DATA
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class AgentComponent(Component):
    """Agent component in a workflow."""
    type: ComponentType = ComponentType.AGENT
    agent_id: Optional[str] = None  # Reference to an agent in the agent service
    
    # Agent-specific configuration
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None


class PluginComponent(Component):
    """Plugin component in a workflow."""
    type: ComponentType = ComponentType.PLUGIN
    plugin_type: str  # Type of plugin (e.g., "web_search", "database", "file_system")
    
    # Plugin-specific configuration
    # This will vary based on the plugin type


class DataSourceComponent(Component):
    """Data source component in a workflow."""
    type: ComponentType = ComponentType.DATA_SOURCE
    source_type: str  # Type of data source (e.g., "document", "database", "api")
    
    # Data source-specific configuration
    # This will vary based on the source type


class InputComponent(Component):
    """Input component in a workflow."""
    type: ComponentType = ComponentType.INPUT
    input_type: str = "text"  # Type of input (e.g., "text", "file", "image")


class OutputComponent(Component):
    """Output component in a workflow."""
    type: ComponentType = ComponentType.OUTPUT
    output_type: str = "text"  # Type of output (e.g., "text", "file", "image")


class Workflow(BaseModel):
    """Workflow definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    components: List[Component] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Workflow-specific configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("components", pre=True)
    def validate_components(cls, v):
        """Convert component dictionaries to the appropriate component type."""
        result = []
        for component in v:
            if isinstance(component, dict):
                component_type = component.get("type")
                if component_type == ComponentType.AGENT:
                    result.append(AgentComponent(**component))
                elif component_type == ComponentType.PLUGIN:
                    result.append(PluginComponent(**component))
                elif component_type == ComponentType.DATA_SOURCE:
                    result.append(DataSourceComponent(**component))
                elif component_type == ComponentType.INPUT:
                    result.append(InputComponent(**component))
                elif component_type == ComponentType.OUTPUT:
                    result.append(OutputComponent(**component))
                else:
                    result.append(Component(**component))
            else:
                result.append(component)
        return result


class WorkflowExecution(BaseModel):
    """Workflow execution state."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    # Execution results for each component
    results: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution errors
    errors: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution logs
    logs: List[Dict[str, Any]] = Field(default_factory=list)
