from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.db.models.risk_control import risk_controls

class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    process_name = Column(String(255), nullable=False)
    risk_description = Column(Text, nullable=False)
    inherent_probability = Column(Integer, nullable=False)
    inherent_impact = Column(Integer, nullable=False)
    residual_probability = Column(Integer)
    residual_impact = Column(Integer)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization")
    owner = relationship("User")
    area = relationship("Area")
    controls = relationship("Control", secondary=risk_controls, back_populates="risks")