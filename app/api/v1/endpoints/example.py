from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=schemas.Example)
def read_example(db: Session = Depends(get_db)):
    """
    Retrieve an example.
    """
    return {"message": "This is an example endpoint."}