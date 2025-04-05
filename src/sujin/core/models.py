"""
Base Pydantic models for the Sujin framework.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a conversation."""
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant', 'system')")
    content: str = Field(..., description="The content of the message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the message")


class ToolParameter(BaseModel):
    """A parameter for a tool."""
    name: str = Field(..., description="The name of the parameter")
    description: str = Field(..., description="A description of the parameter")
    type: str = Field(..., description="The type of the parameter (e.g., 'string', 'number', 'boolean')")
    required: bool = Field(default=False, description="Whether the parameter is required")
    default: Optional[Any] = Field(default=None, description="The default value for the parameter")


class ToolSchema(BaseModel):
    """Schema for a tool."""
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="A description of what the tool does")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Parameters for the tool")


class ToolCall(BaseModel):
    """A call to a tool."""
    tool_name: str = Field(..., description="The name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool call")


class ToolResult(BaseModel):
    """The result of a tool call."""
    tool_name: str = Field(..., description="The name of the tool that was called")
    success: bool = Field(..., description="Whether the tool call was successful")
    result: Any = Field(..., description="The result of the tool call")
    error: Optional[str] = Field(default=None, description="Error message if the tool call failed")


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str = Field(..., description="The name of the agent")
    description: Optional[str] = Field(default=None, description="A description of the agent's purpose")
    model: Optional[str] = Field(default=None, description="The model to use for the agent")
    max_iterations: int = Field(default=10, description="Maximum number of iterations for the agent to run")
    temperature: float = Field(default=0.7, description="Temperature for model sampling")
    plugins: List[str] = Field(default_factory=list, description="List of plugin names to use")


class AgentInput(BaseModel):
    """Input to an agent."""
    messages: List[Message] = Field(default_factory=list, description="The conversation history")
    tools: List[ToolSchema] = Field(default_factory=list, description="Available tools")
    config: Optional[AgentConfig] = Field(default=None, description="Configuration for the agent")


class AgentOutput(BaseModel):
    """Output from an agent."""
    message: Message = Field(..., description="The agent's response message")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tool calls made by the agent")
    thinking: Optional[str] = Field(default=None, description="The agent's thinking process")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata for the output")
