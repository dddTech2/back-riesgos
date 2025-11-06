from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.models.role import user_roles
from app.db.models.organization import Organization

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String(50), nullable=False, default="user") # Added to satisfy DB constraint
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    organization = relationship("Organization")