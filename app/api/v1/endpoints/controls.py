from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import crud_control, crud_risk
from app.api import deps
from app.db.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.control.Control])
def read_controls(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    sort: Optional[str] = None,
    search: Optional[str] = None,
    fields: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retrieve controls.
    """
    controls = crud_control.control.get_multi(
        db, skip=skip, limit=limit, sort=sort, search=search
    )
    
    if fields:
        selected_fields = fields.split(',')
        output = []
        for control in controls:
            data = {}
            for field in selected_fields:
                if hasattr(control, field):
                    data[field] = getattr(control, field)
            output.append(data)
        return output
        
    return controls

@router.post(
    "/",
    response_model=schemas.control.Control,
    status_code=status.HTTP_201_CREATED,
)
def create_control(
    *,
    db: Session = Depends(deps.get_db),
    control_in: schemas.control.ControlCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new control.
    """
    control = crud_control.control.create_with_organization_and_risks(
        db=db, obj_in=control_in, organization_id=current_user.organization_id
    )
    return control


@router.put("/{control_id}", response_model=schemas.control.Control)
def update_control(
    *,
    db: Session = Depends(deps.get_db),
    control_id: int,
    control_in: schemas.control.ControlUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Update a control.
    """
    control = crud_control.control.get(db=db, id=control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The control with this ID does not exist in the system.",
        )
    # Add authorization logic here if needed

    control = crud_control.control.update(db=db, db_obj=control, obj_in=control_in)
    return control


@router.post("/{control_id}/risks/{risk_id}", response_model=schemas.control.Control)
def add_risk_to_control(
    *,
    db: Session = Depends(deps.get_db),
    control_id: int,
    risk_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Associate an existing risk with a control.
    """
    control = crud_control.control.get(db=db, id=control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The control with this ID does not exist in the system.",
        )
    risk = crud_risk.risk.get(db=db, id=risk_id)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The risk with this ID does not exist in the system.",
        )
    # Add authorization logic here if needed

    control = crud_control.control.add_risk(
        db=db, control_obj=control, risk_obj=risk
    )
    return control