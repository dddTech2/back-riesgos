from pydantic import BaseModel

class AreaBase(BaseModel):
    name: str

class AreaCreate(AreaBase):
    pass

class Area(AreaBase):
    id: int
    organization_id: int

    class Config:
        orm_mode = True