from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100))
    value_amount = Column(Numeric(15, 2))
    criticality = Column(String(50))
    owner = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization")