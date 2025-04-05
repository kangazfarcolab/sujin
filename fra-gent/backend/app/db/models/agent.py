"""
Agent database model.
"""

from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Agent(Base):
    """
    Agent database model.
    """
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    model = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=True)
    temperature = Column(Float, nullable=False, default=0.7)
    max_tokens = Column(Integer, nullable=False, default=1000)
