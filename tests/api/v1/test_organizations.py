from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_lower_string, random_email

def test_create_organization(client: TestClient, db: Session) -> None:
    # Create superuser
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db) # Creates superadmin by default in my util implementation

    data = {
        "name": random_lower_string(),
        "admin_email": random_email(),
        "admin_full_name": random_lower_string()
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/", headers=headers, json=data
    )
    assert response.status_code == 201
    content = response.json()
    assert content["organization"]["name"] == data["name"]
    assert "organization" in content
    assert "admin_user" in content
    assert content["admin_user"]["email"] == data["admin_email"]

def test_read_organizations(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    response = client.get(
        f"{settings.API_V1_STR}/organizations/", headers=headers
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)

def test_read_organization(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Create organization first
    data = {
        "name": random_lower_string(),
        "admin_email": random_email(),
        "admin_full_name": random_lower_string()
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/", headers=headers, json=data
    )
    org_id = response.json()["organization"]["id"]

    response = client.get(
        f"{settings.API_V1_STR}/organizations/{org_id}", headers=headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == org_id
    assert content["name"] == data["name"]

def test_update_organization(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Create organization first
    data = {
        "name": random_lower_string(),
        "admin_email": random_email(),
        "admin_full_name": random_lower_string()
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/", headers=headers, json=data
    )
    org_id = response.json()["organization"]["id"]

    update_data = {"name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/organizations/{org_id}", headers=headers, json=update_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == org_id
    assert content["name"] == update_data["name"]

def test_delete_organization(client: TestClient, db: Session) -> None:
    email = random_email()
    headers = authentication_token_from_email(client=client, email=email, db=db)

    # Create organization first
    data = {
        "name": random_lower_string(),
        "admin_email": random_email(),
        "admin_full_name": random_lower_string()
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/", headers=headers, json=data
    )
    org_id = response.json()["organization"]["id"]

    response = client.delete(
        f"{settings.API_V1_STR}/organizations/{org_id}", headers=headers
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == org_id
    
    # Verify deletion
    response = client.get(
        f"{settings.API_V1_STR}/organizations/{org_id}", headers=headers
    )
    assert response.status_code == 404

