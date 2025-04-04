"""
Base Tool class for the Sujin framework.
"""

import inspect
from typing import Dict, List, Optional, Any, Callable, Type, get_type_hints
from pydantic import create_model, Field

from ..core.models import ToolSchema, ToolParameter


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

    def get_schema(self) -> ToolSchema:
        """
        Get the schema for this tool.

        Returns:
            A ToolSchema describing the tool's interface
        """
        parameters = []

        # Get function signature
        sig = inspect.signature(self.func)
        type_hints = get_type_hints(self.func)

        # Get function docstring
        doc = inspect.getdoc(self.func) or ""
        param_docs = {}

        # Parse docstring for parameter descriptions
        if doc:
            lines = doc.split("\n")
            in_args = False
            current_param = None
            current_desc = []

            for line in lines:
                line = line.strip()
                if line.lower().startswith("args:") or line.lower().startswith("parameters:"):
                    in_args = True
                    continue

                if in_args:
                    if line.startswith("Returns:") or line.startswith("Raises:") or not line:
                        if current_param and current_desc:
                            param_docs[current_param] = " ".join(current_desc)
                        in_args = False
                        continue

                    if line and line[0].isalnum() and ":" in line:
                        if current_param and current_desc:
                            param_docs[current_param] = " ".join(current_desc)

                        parts = line.split(":", 1)
                        current_param = parts[0].strip()
                        current_desc = [parts[1].strip()] if len(parts) > 1 else []
                    elif current_param and line:
                        current_desc.append(line)

            if in_args and current_param and current_desc:
                param_docs[current_param] = " ".join(current_desc)

        # Create parameters from function signature
        for name, param in sig.parameters.items():
            # Skip self parameter for methods
            if name == "self":
                continue

            param_type = type_hints.get(name, Any).__name__
            description = param_docs.get(name, f"Parameter: {name}")
            required = param.default == inspect.Parameter.empty
            default = None if param.default == inspect.Parameter.empty else param.default

            parameters.append(ToolParameter(
                name=name,
                description=description,
                type=param_type,
                required=required,
                default=default
            ))

        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters=parameters
        )
