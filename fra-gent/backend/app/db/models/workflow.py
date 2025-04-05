"""
Workflow database model.
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class Workflow(Base):
    """
    Workflow database model.
    """
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    definition = Column(JSONB, nullable=False, default={})
