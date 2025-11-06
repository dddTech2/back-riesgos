from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import crud_risk, crud_control
from app.api import deps
from app.db.models.user import User

router = APIRouter()

@router.get("/", response_model=List[schemas.risk.Risk])
def read_risks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    sort: Optional[str] = None,
    search: Optional[str] = None,
    fields: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
    # Filtering parameters could be added here, e.g. area_id: Optional[int] = None
):
    """
    Retrieve risks with pagination, sorting, searching, and field selection.
    """
    # A simple filter example, more can be added
    filters = {}
    # if area_id:
    #     filters["area_id"] = area_id
        
    risks = crud_risk.risk.get_multi(
        db, skip=skip, limit=limit, sort=sort, search=search, filters=filters
    )
    
    if fields:
        # This is a simplified implementation of sparse fieldsets.
        # For a more robust solution, consider using a library or a more complex parser.
        selected_fields = fields.split(',')
        output = []
        for risk in risks:
            data = {}
            for field in selected_fields:
                if hasattr(risk, field):
                    data[field] = getattr(risk, field)
            output.append(data)
        return output
        
    return risks

@router.post(
    "/",
    response_model=schemas.risk.Risk,
    status_code=status.HTTP_201_CREATED,
)
def create_risk(
    *,
    db: Session = Depends(deps.get_db),
    risk_in: schemas.risk.RiskCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Create new risk.
    """
    risk = crud_risk.risk.create_with_organization_and_owner(
        db=db,
        obj_in=risk_in,
        organization_id=current_user.organization_id,
        owner_id=current_user.id,
    )
    return risk


@router.put("/{risk_id}", response_model=schemas.risk.Risk)
def update_risk(
    *,
    db: Session = Depends(deps.get_db),
    risk_id: int,
    risk_in: schemas.risk.RiskUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Update a risk.
    """
    risk = crud_risk.risk.get(db=db, id=risk_id)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The risk with this ID does not exist in the system.",
        )
    # Add authorization logic here if needed, e.g.
    # if risk.owner_id != current_user.id and not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    risk = crud_risk.risk.update(db=db, db_obj=risk, obj_in=risk_in)
    return risk


@router.post("/{risk_id}/controls/{control_id}", response_model=schemas.risk.Risk)
def add_control_to_risk(
    *,
    db: Session = Depends(deps.get_db),
    risk_id: int,
    control_id: int,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Associate an existing control with a risk.
    """
    risk = crud_risk.risk.get(db=db, id=risk_id)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The risk with this ID does not exist in the system.",
        )
    control = crud_control.control.get(db=db, id=control_id)
    if not control:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The control with this ID does not exist in the system.",
        )
    # Add authorization logic here if needed

    risk = crud_risk.risk.add_control(db=db, risk_obj=risk, control_obj=control)
    return risk