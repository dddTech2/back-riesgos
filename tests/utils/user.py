from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.crud.crud_user import user as crud_user
from app.core.config import settings
from app.schemas.user import UserCreate, UserUpdate
from app.db.models.organization import Organization
from tests.utils.utils import random_email, random_lower_string

def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers

def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = "password"
    user = crud_user.get_by_email(db, email=email)
    if not user:
        # Ensure an organization exists
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="Test Organization")
            db.add(org)
            db.commit()
            db.refresh(org)
        
        user_in_create = UserCreate(
            email=email, 
            password=password, 
            role="superadmin", 
            is_superuser=True,
            organization_id=org.id,
            full_name="Test User"
        ) 
        user = crud_user.create(db, obj_in=user_in_create)
    else:
        user_in_update = UserUpdate(password=password)
        crud_user.update(db, db_obj=user, obj_in=user_in_update)

    return user_authentication_headers(client=client, email=email, password=password)

def get_superadmin_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.SUPERUSER_EMAIL,
        "password": settings.SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
