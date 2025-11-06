from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app import schemas
from app.crud import crud_area
from app.api import deps
from app.db.models.user import User

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.area.Area,
    status_code=status.HTTP_201_CREATED,
)
def create_area(
    *,
    db: Session = Depends(deps.get_db),
    area_in: schemas.area.AreaCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new area.
    """
    area = crud_area.area.create_with_organization(
        db=db, obj_in=area_in, organization_id=current_user.organization_id
    )
    return area