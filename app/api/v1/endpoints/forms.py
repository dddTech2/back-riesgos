from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.api.deps import get_db, get_current_active_user
from app.crud import crud_form
from app.db.models.user import User
from app.schemas.submission import Submission, SubmissionCreate, AccessRequest

router = APIRouter()

# --- Admin Endpoints ---

@router.post("/", response_model=schemas.Form)
def create_form(
    *,
    db: Session = Depends(get_db),
    form_in: schemas.FormCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new form.
    """
    if not current_user.organization_id and current_user.role != "superadmin":
         raise HTTPException(status_code=400, detail="User must belong to an organization")

    form = crud_form.form.create_with_questions(
        db=db, obj_in=form_in, created_by=current_user.id, organization_id=current_user.organization_id
    )
    return form

@router.get("/", response_model=List[schemas.Form])
def read_forms(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve forms.
    """
    if not current_user.organization_id:
        # Superadmin logic or empty
        return []
    
    forms = crud_form.form.get_multi_by_organization(
        db=db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return forms

@router.get("/{form_id}", response_model=schemas.Form)
def read_form(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific form by id (Admin).
    """
    form = crud_form.form.get(db=db, id=form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return form

@router.get("/{form_id}/stats", response_model=schemas.FormStats) # Define specific schema if needed
def get_form_stats(
    form_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get form statistics and submissions.
    """
    form = crud_form.form.get(db=db, id=form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if form.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Simple stats
    total_submissions = len(form.submissions)
    avg_score = 0.0
    if total_submissions > 0 and form.is_graded:
        total_score = sum(s.score for s in form.submissions)
        avg_score = total_score / total_submissions
    
    return {
        "total_submissions": total_submissions,
        "average_score": avg_score,
        "submissions": form.submissions # returns list of FormSubmission
    }

# --- Public / Respondent Endpoints ---

@router.post("/access", response_model=Any)
def validate_access(
    *,
    db: Session = Depends(get_db),
    access_request: AccessRequest
) -> Any:
    """
    Validate access code and user eligibility.
    """
    form = crud_form.form.get_by_access_code(db=db, access_code=access_request.access_code)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found or invalid code")
    
    if not form.is_active:
        raise HTTPException(status_code=400, detail="Form is not active")
    
    now = datetime.utcnow()
    if form.start_date and now < form.start_date.replace(tzinfo=None): # Ensure naive comparison if needed or strict tz
        raise HTTPException(status_code=400, detail="Form has not started yet")
    if form.end_date and now > form.end_date.replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Form has expired")

    # Check attempts
    if form.max_attempts:
        submissions = crud_form.submission.get_by_respondent(
            db=db, form_id=form.id, identifier=access_request.respondent_identifier
        )
        if len(submissions) >= form.max_attempts:
            raise HTTPException(status_code=400, detail="Maximum attempts reached")

    return {
        "status": "valid",
        "form_id": form.id,
        "public_id": form.id # Using ID as public ref for now, could be uuid
    }

@router.get("/public/{form_id}/structure", response_model=schemas.FormPublic)
def get_form_structure(
    form_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get form structure (questions/options) without correct answers.
    """
    form = crud_form.form.get(db=db, id=form_id)
    if not form:
         raise HTTPException(status_code=404, detail="Form not found")
    
    # We rely on Pydantic FormPublic to filter out sensitive data like 'is_correct'
    return form

@router.post("/public/{form_id}/submit", response_model=schemas.Submission)
def submit_form(
    form_id: int,
    submission_in: SubmissionCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Submit form answers.
    """
    form = crud_form.form.get(db=db, id=form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # Verify validity again (double check)
    if not form.is_active:
         raise HTTPException(status_code=400, detail="Form is not active")

    # Create submission
    submission = crud_form.submission.create_submission(db=db, obj_in=submission_in, form=form)
    return submission

