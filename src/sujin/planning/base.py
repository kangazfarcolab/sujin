"""
Base Planner class for the Sujin framework.
"""

from typing import Dict, List, Optional, Any


class Planner:
    """Base Planner class that all planning systems should inherit from."""
    
    def __init__(self, name: str):
        """
        Initialize a new Planner.
        
        Args:
            name: The name of the planner
        """
        self.name = name
        
    def create_plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Create a plan to achieve a goal.
        
        Args:
            goal: The goal to achieve
            context: Additional context that may be useful for planning
            
        Returns:
            A list of steps to achieve the goal
        """
        raise NotImplementedError("Subclasses must implement create_plan()")
        
    def refine_plan(self, plan: List[str], feedback: str) -> List[str]:
        """
        Refine a plan based on feedback.
        
        Args:
            plan: The current plan
            feedback: Feedback on the plan
            
        Returns:
            A refined plan
        """
        raise NotImplementedError("Subclasses must implement refine_plan()")
