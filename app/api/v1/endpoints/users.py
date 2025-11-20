from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.crud.crud_user import user as crud_user
from app.api.deps import get_db, RoleChecker, get_current_active_user
from app.db.models.user import User

router = APIRouter()

@router.post(
    "/",
    response_model=schemas.user.User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RoleChecker(["admin"]))],
)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.user.UserCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create new user for the current user's organization.
    
    Only admins can create users.
    """
    # Ensure organization_id is set to current user's organization
    if not current_user.organization_id:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user must belong to an organization",
        )
    
    # Override organization_id in the input with the admin's organization
    user_in.organization_id = current_user.organization_id
    
    # Check if user exists
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
        
    user = crud_user.create(db, obj_in=user_in)
    return user
