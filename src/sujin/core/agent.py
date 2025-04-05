"""
Base Agent class for the Sujin framework.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Type

from .models import Message, AgentInput, AgentOutput, ToolSchema, ToolCall, ToolResult
from ..plugins.manager import PluginManager
from ..tools.base import Tool

logger = logging.getLogger(__name__)


class Agent:
    """Base Agent class that all agents should inherit from."""

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a new Agent.

        Args:
            name: The name of the agent
            description: A description of the agent's purpose
        """
        self.name = name
        self.description = description
        self.tools: List[Tool] = []
        self.memory = None
        self.planner = None
        self.plugin_manager = PluginManager()

    def add_tool(self, tool: Tool) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)

    def set_memory(self, memory: Any) -> None:
        """Set the memory system for the agent."""
        self.memory = memory

    def set_planner(self, planner: Any) -> None:
        """Set the planning system for the agent."""
        self.planner = planner

    def register_plugin(self, plugin: Any) -> None:
        """
        Register a plugin with the agent.

        Args:
            plugin: The plugin to register
        """
        self.plugin_manager.register_plugin(plugin)

    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin from the agent.

        Args:
            plugin_name: The name of the plugin to unregister
        """
        self.plugin_manager.unregister_plugin(plugin_name)

    def discover_plugins(self, package_name: str = "sujin.plugins") -> None:
        """
        Discover and register plugins from a package.

        Args:
            package_name: The name of the package to search for plugins
        """
        self.plugin_manager.discover_plugins(package_name)

    def get_tool_schemas(self) -> List[ToolSchema]:
        """
        Get schemas for all tools.

        Returns:
            A list of tool schemas
        """
        return [tool.get_schema() for tool in self.tools]

    def call_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Call a tool.

        Args:
            tool_call: The tool call to execute

        Returns:
            The result of the tool call
        """
        for tool in self.tools:
            if tool.name == tool_call.tool_name:
                try:
                    result = tool(**tool_call.parameters)
                    return ToolResult(
                        tool_name=tool_call.tool_name,
                        success=True,
                        result=result,
                        error=None
                    )
                except Exception as e:
                    logger.error(f"Error calling tool {tool_call.tool_name}: {e}")
                    return ToolResult(
                        tool_name=tool_call.tool_name,
                        success=False,
                        result=None,
                        error=str(e)
                    )

        return ToolResult(
            tool_name=tool_call.tool_name,
            success=False,
            result=None,
            error=f"Tool {tool_call.tool_name} not found"
        )

    def process(self, input_data: Union[str, AgentInput]) -> AgentOutput:
        """
        Process input and generate a response.

        Args:
            input_data: The input data to process

        Returns:
            The agent's output
        """
        # Convert string input to AgentInput
        if isinstance(input_data, str):
            input_data = AgentInput(
                messages=[Message(role="user", content=input_data)],
                tools=self.get_tool_schemas()
            )

        # Run pre-processing plugins
        try:
            input_data = self.plugin_manager.run_pre_process(input_data)
        except Exception as e:
            logger.error(f"Error in plugin pre-processing: {e}")

        # Run the agent
        try:
            output_data = self.run(input_data)
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            # Try to handle the error with plugins
            output_data = self.plugin_manager.handle_error(e, input_data)
            if output_data is None:
                # If no plugin handled the error, raise it
                raise

        # Run post-processing plugins
        try:
            output_data = self.plugin_manager.run_post_process(output_data)
        except Exception as e:
            logger.error(f"Error in plugin post-processing: {e}")

        return output_data

    def run(self, input_data: AgentInput) -> AgentOutput:
        """
        Process input and generate a response.

        This method should be implemented by subclasses.

        Args:
            input_data: The input data to process

        Returns:
            The agent's output
        """
        raise NotImplementedError("Subclasses must implement run()")
