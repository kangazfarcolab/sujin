"""
Agent schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str
    description: Optional[str] = None
    model: str = "gpt-4"
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


class AgentCreate(AgentBase):
    """Agent creation schema."""
    pass


class AgentUpdate(BaseModel):
    """Agent update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class Agent(AgentBase):
    """Agent schema."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True
