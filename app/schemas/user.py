from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.schemas.role import Role

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    organization_id: Optional[int] = None
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserInDBBase(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    roles: List[Role] = []

class UserInDB(UserInDBBase):
    password_hash: str