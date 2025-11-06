from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models.area import Area
from app.schemas.area import AreaCreate

class CRUDArea(CRUDBase[Area, AreaCreate, AreaCreate]):
    def create_with_organization(self, db: Session, *, obj_in: AreaCreate, organization_id: int) -> Area:
        db_obj = Area(
            name=obj_in.name,
            organization_id=organization_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

area = CRUDArea(Area)