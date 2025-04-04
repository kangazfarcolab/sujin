"""
Base Agent class for the Sujin framework.
"""

from typing import Dict, List, Optional, Any


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
        self.tools = []
        self.memory = None
        self.planner = None
        
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)
        
    def set_memory(self, memory: Any) -> None:
        """Set the memory system for the agent."""
        self.memory = memory
        
    def set_planner(self, planner: Any) -> None:
        """Set the planning system for the agent."""
        self.planner = planner
        
    def run(self, input_data: Any) -> Any:
        """
        Process input and generate a response.
        
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement run()")
