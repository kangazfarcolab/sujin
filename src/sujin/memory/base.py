"""
Base Memory class for the Sujin framework.
"""

from typing import Dict, List, Optional, Any


class Memory:
    """Base Memory class that all memory systems should inherit from."""
    
    def __init__(self, capacity: Optional[int] = None):
        """
        Initialize a new Memory system.
        
        Args:
            capacity: Maximum number of items to store (None for unlimited)
        """
        self.capacity = capacity
        
    def add(self, item: Any) -> None:
        """
        Add an item to memory.
        
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement add()")
        
    def retrieve(self, query: Any) -> List[Any]:
        """
        Retrieve items from memory based on a query.
        
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement retrieve()")
        
    def clear(self) -> None:
        """
        Clear all items from memory.
        
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement clear()")
