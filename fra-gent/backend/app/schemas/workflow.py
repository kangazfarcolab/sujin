"""
Workflow schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any] = Field(default_factory=lambda: {"nodes": [], "edges": []})


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema."""
    pass


class WorkflowUpdate(BaseModel):
    """Workflow update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None


class Workflow(WorkflowBase):
    """Workflow schema."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True
