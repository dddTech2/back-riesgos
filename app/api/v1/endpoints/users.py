from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import RoleChecker, get_current_active_user, get_db
from app.crud.crud_user import user as crud_user
from app.db.models.user import User

router = APIRouter()

# Common dependency for admin/super_admin access
admin_access = RoleChecker(["admin", "super_admin"])


@router.get("/", response_model=List[schemas.user.User], dependencies=[Depends(admin_access)])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    if current_user.role == "super_admin":
        users = crud_user.get_multi(db, skip=skip, limit=limit)
    else:
        # Admin can only see users from their organization
        if not current_user.organization_id:
             return [] # Or raise error depending on requirements. 
                       # If admin has no org, they technically shouldn't see any users.
        users = crud_user.get_multi_by_organization(
            db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
    return users


@router.post(
    "/",
    response_model=schemas.user.User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_access)],
)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.user.UserCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new user.
    """
    if current_user.role != "super_admin":
        # Ensure organization_id is set to current user's organization for non-superadmins
        if not current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin user must belong to an organization",
            )
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


@router.get("/{user_id}", response_model=schemas.user.User, dependencies=[Depends(admin_access)])
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if (
        current_user.role != "super_admin"
        and user.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user


@router.put("/{user_id}", response_model=schemas.user.User, dependencies=[Depends(admin_access)])
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: schemas.user.UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if (
        current_user.role != "super_admin"
        and user.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.user.User, dependencies=[Depends(admin_access)])
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a user.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if (
        current_user.role != "super_admin"
        and user.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    user = crud_user.remove(db, id=user_id)
    return user
