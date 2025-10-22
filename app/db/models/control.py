from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Control(Base):
    __tablename__ = "controls"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    control_code = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50))
    effectiveness_probability = Column(Integer, default=0)
    effectiveness_impact = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization")
    owner = relationship("User")

    __table_args__ = (UniqueConstraint('organization_id', 'control_code', name='_organization_control_code_uc'),)