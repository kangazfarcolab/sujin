"""
Base Tool class for the Sujin framework.
"""

from typing import Dict, List, Optional, Any, Callable


class Tool:
    """Base Tool class that all tools should inherit from."""
    
    def __init__(self, name: str, description: str, func: Callable):
        """
        Initialize a new Tool.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            func: The function to call when the tool is used
        """
        self.name = name
        self.description = description
        self.func = func
        
    def __call__(self, *args, **kwargs) -> Any:
        """Call the tool's function with the provided arguments."""
        return self.func(*args, **kwargs)
        
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool.
        
        Returns:
            A dictionary describing the tool's interface
        """
        # This is a placeholder - in a real implementation,
        # this would return a proper schema based on the function signature
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {}
        }
