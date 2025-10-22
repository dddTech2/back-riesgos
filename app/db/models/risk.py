from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    risk_code = Column(String(20), nullable=False)
    process = Column(String(255))
    process_stage = Column(Text)
    description = Column(Text, nullable=False)
    cause = Column(Text)
    inherent_probability = Column(Integer, nullable=False)
    inherent_impact = Column(Integer, nullable=False)
    residual_probability = Column(Integer)
    residual_impact = Column(Integer)
    status = Column(String(50), default='Activo')
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization")
    owner = relationship("User")

    __table_args__ = (UniqueConstraint('organization_id', 'risk_code', name='_organization_risk_code_uc'),)