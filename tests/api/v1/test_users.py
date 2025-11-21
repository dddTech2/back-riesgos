from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_lower_string, random_email

def test_create_user(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)
    
    # Retrieve current user to get organization_id
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    # The schemas.User model might return organization_id. 
    # If not returned by API, we need to fetch it from DB or ensure schema includes it.
    # Assuming schema returns it. If KeyError, schema needs update.
    current_user_org_id = r.json().get("organization_id")
    if current_user_org_id is None:
        # Fallback: fetch from DB directly if API doesn't expose it, or update API schema.
        # For now, let's assume we need to update User schema or getting it from DB.
        # Since this is an integration test, better to rely on API if possible, 
        # but if API hides it, we must know it to create other users.
        # Let's check the schema in app/schemas/user.py.
        pass 

    username = random_email()
    password = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "full_name": random_lower_string(),
        "role": "user",
        "organization_id": current_user_org_id
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/", headers=headers, json=data
    )
    assert response.status_code == 201
    content = response.json()
    assert content["email"] == username
    assert "id" in content

def test_read_users(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Retrieve current user to get organization_id
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    current_user_org_id = r.json()["organization_id"]

    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=headers
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)

def test_read_user_by_id(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Retrieve current user to get organization_id
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    current_user_org_id = r.json()["organization_id"]

    # Create a user
    username = random_email()
    password = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "full_name": random_lower_string(),
        "role": "user",
        "organization_id": current_user_org_id
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/", headers=headers, json=data
    )
    user_id = response.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}", headers=headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == user_id
    assert content["email"] == username

def test_update_user(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Retrieve current user to get organization_id
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    current_user_org_id = r.json()["organization_id"]

    # Create a user
    username = random_email()
    password = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "full_name": random_lower_string(),
        "role": "user",
        "organization_id": current_user_org_id
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/", headers=headers, json=data
    )
    user_id = response.json()["id"]

    new_name = random_lower_string()
    update_data = {"full_name": new_name}
    response = client.put(
        f"{settings.API_V1_STR}/users/{user_id}", headers=headers, json=update_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == user_id
    # The update response should contain the new name.
    assert content["full_name"] == new_name

def test_delete_user(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Retrieve current user to get organization_id
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    current_user_org_id = r.json()["organization_id"]

    # Create a user
    username = random_email()
    password = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "full_name": random_lower_string(),
        "role": "user",
        "organization_id": current_user_org_id
    }
    response = client.post(
        f"{settings.API_V1_STR}/users/", headers=headers, json=data
    )
    user_id = response.json()["id"]

    response = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}", headers=headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == user_id

    # Verify deletion
    # The CRUD remove implementation performs a soft delete (is_active=False).
    # The read_user_by_id endpoint should probably return 404 if user is inactive or handle it.
    # If read_user_by_id returns the user but is_active is false, we should assert that.
    # Let's check if the user is still accessible but inactive, or if the endpoint filters inactive users.
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}", headers=headers
    )
    # If soft delete, it might return 200 with is_active=False, OR 404 if get() filters.
    # Given CRUDUser.remove sets is_active=False, let's see what get() does.
    # CRUDUser.get uses CRUDBase.get which uses db.query(model).filter(model.id == id).first().
    # It does NOT filter by is_active by default.
    # So we expect 200 and is_active=False.
    assert response.status_code == 200
    content = response.json()
    assert content["is_active"] is False

