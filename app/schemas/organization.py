from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# Esquema para la respuesta del usuario administrador
class AdminUserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    class Config:
        orm_mode = True

# Esquema para la respuesta de la organización
class OrganizationResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Esquema para el cuerpo de la petición (Request Body)
class OrganizationCreate(BaseModel):
    name: str
    admin_email: EmailStr
    admin_full_name: str

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

# Esquema para la respuesta completa del endpoint
class NewOrganizationResponse(BaseModel):
    organization: OrganizationResponse
    admin_user: AdminUserResponse
    temporary_password: str
