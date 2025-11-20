from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import crud_organization
from app.api.deps import get_db, RoleChecker

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.organization.NewOrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["superadmin"]))],
)
def create_organization(
    *,
    db: Session = Depends(get_db),
    organization_in: schemas.organization.OrganizationCreate,
):
    """
    Crea una nueva organización y su administrador inicial.
    
    Este endpoint solo es accesible para usuarios con el rol 'super_admin'.
    """
    result = crud_organization.create_with_initial_admin(db=db, org_in=organization_in)
    return result