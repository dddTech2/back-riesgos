from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_lower_string, random_email

def test_create_area(client: TestClient, db: Session) -> None:
    # 1. Create superadmin to create organization
    admin_email = random_email()
    headers = authentication_token_from_email(client=client, email=admin_email, db=db)
    
    # 2. Create organization
    org_admin_email = random_email()
    # admin_password not needed in input for org creation via API usually if auto-generated, 
    # but we need to know it to login.
    # Wait, the API generates a random password and returns it!
    # So we should capture it from response.
    
    org_data = {
        "name": random_lower_string(),
        "admin_email": org_admin_email,
        "admin_full_name": random_lower_string()
    }
    response = client.post(
        f"{settings.API_V1_STR}/organizations/", headers=headers, json=org_data
    )
    assert response.status_code == 201, response.text
    org_content = response.json()
    org_id = org_content["organization"]["id"]
    org_admin_password = org_content["temporary_password"]

    # 3. Login as org admin
    login_data = {
        "username": org_admin_email,
        "password": org_admin_password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    org_admin_token = r.json()["access_token"]
    org_admin_headers = {"Authorization": f"Bearer {org_admin_token}"}

    # 4. Create area
    area_data = {
        "name": random_lower_string(),
    }
    response = client.post(
        f"{settings.API_V1_STR}/areas/", headers=org_admin_headers, json=area_data
    )
    assert response.status_code == 201
    content = response.json()
    assert content["name"] == area_data["name"]
    assert content["organization_id"] == org_id

