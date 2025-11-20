from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import crud_organization
from app.api.deps import get_db, RoleChecker, get_current_user
from app.db.models.user import User

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
    result = crud_organization.organization.create_with_initial_admin(db=db, org_in=organization_in)
    return result

@router.get(
    "/",
    response_model=List[schemas.organization.OrganizationResponse],
    dependencies=[Depends(RoleChecker(["superadmin"]))],
)
def read_organizations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Recuperar todas las organizaciones.
    
    Solo accesible para superadmin.
    """
    organizations = crud_organization.organization.get_multi(db, skip=skip, limit=limit)
    return organizations

@router.get(
    "/{organization_id}",
    response_model=schemas.organization.OrganizationResponse,
)
def read_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtener una organización por ID.
    
    - Superadmin: puede ver cualquier organización.
    - Admin: solo puede ver su propia organización.
    """
    organization = crud_organization.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    if current_user.role == "superadmin":
        return organization
    
    if current_user.role == "admin" and current_user.organization_id == organization_id:
        return organization
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough privileges",
    )

@router.put(
    "/{organization_id}",
    response_model=schemas.organization.OrganizationResponse,
    dependencies=[Depends(RoleChecker(["superadmin"]))],
)
def update_organization(
    organization_id: int,
    organization_in: schemas.organization.OrganizationUpdate,
    db: Session = Depends(get_db),
):
    """
    Actualizar una organización.
    
    Solo accesible para superadmin.
    """
    organization = crud_organization.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    organization = crud_organization.organization.update(db, db_obj=organization, obj_in=organization_in)
    return organization

@router.delete(
    "/{organization_id}",
    response_model=schemas.organization.OrganizationResponse,
    dependencies=[Depends(RoleChecker(["superadmin"]))],
)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Eliminar una organización.
    
    Solo accesible para superadmin.
    """
    organization = crud_organization.organization.get(db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    
    organization = crud_organization.organization.remove(db, id=organization_id)
    return organization
