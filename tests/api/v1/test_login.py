from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud.crud_user import user as crud_user
from app.schemas.user import UserCreate
from app.db.models.organization import Organization
from tests.utils.utils import random_email, random_lower_string

def _ensure_org(db: Session) -> int:
    org = db.query(Organization).first()
    if not org:
        org = Organization(name="Test Org Login")
        db.add(org)
        db.commit()
        db.refresh(org)
    return org.id

def test_get_access_token(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    org_id = _ensure_org(db)
    user_in = UserCreate(
        email=username, 
        password=password, 
        role="user", 
        organization_id=org_id,
        full_name=random_lower_string()
    )
    crud_user.create(db, obj_in=user_in)

    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]

def test_use_access_token(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    org_id = _ensure_org(db)
    user_in = UserCreate(
        email=username, 
        password=password, 
        role="user", 
        organization_id=org_id,
        full_name=random_lower_string()
    )
    crud_user.create(db, obj_in=user_in)

    login_data = {
        "username": username,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == username

