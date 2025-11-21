from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_lower_string, random_email

def test_create_risk(client: TestClient, db: Session) -> None:
    # 1. Setup Org and Admin
    admin_email = random_email()
    headers = authentication_token_from_email(client=client, email=admin_email, db=db)
    
    org_admin_email = random_email()
    org_data = {
        "name": random_lower_string(),
        "admin_email": org_admin_email,
        "admin_full_name": random_lower_string()
    }
    response = client.post(f"{settings.API_V1_STR}/organizations/", headers=headers, json=org_data)
    org_content = response.json()
    org_admin_password = org_content["temporary_password"]

    login_data = {"username": org_admin_email, "password": org_admin_password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    org_admin_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # 2. Create Area
    area_data = {"name": random_lower_string()}
    r_area = client.post(f"{settings.API_V1_STR}/areas/", headers=org_admin_headers, json=area_data)
    area_id = r_area.json()["id"]

    # 3. Create Risk
    risk_data = {
        "process_name": random_lower_string(),
        "risk_description": random_lower_string(),
        "area_id": area_id,
        "prob_question_1": 2,
        "prob_question_2": 2,
        "prob_question_3": 2,
        "imp_question_1": 2,
        "imp_question_2": 2,
        "imp_question_3": 2
    }
    response = client.post(
        f"{settings.API_V1_STR}/risks/", headers=org_admin_headers, json=risk_data
    )
    assert response.status_code == 201
    content = response.json()
    assert content["process_name"] == risk_data["process_name"]
    assert content["area_id"] == area_id

def test_read_risks(client: TestClient, db: Session) -> None:
    # Setup Org and Admin
    admin_email = random_email()
    headers = authentication_token_from_email(client=client, email=admin_email, db=db)
    
    org_admin_email = random_email()
    org_data = {
        "name": random_lower_string(),
        "admin_email": org_admin_email,
        "admin_full_name": random_lower_string()
    }
    response = client.post(f"{settings.API_V1_STR}/organizations/", headers=headers, json=org_data)
    org_content = response.json()
    org_admin_password = org_content["temporary_password"]

    login_data = {"username": org_admin_email, "password": org_admin_password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    org_admin_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    response = client.get(f"{settings.API_V1_STR}/risks/", headers=org_admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_risk(client: TestClient, db: Session) -> None:
    # Setup Org, Admin, Area, Risk
    admin_email = random_email()
    headers = authentication_token_from_email(client=client, email=admin_email, db=db)
    
    org_admin_email = random_email()
    org_data = {
        "name": random_lower_string(),
        "admin_email": org_admin_email,
        "admin_full_name": random_lower_string()
    }
    response = client.post(f"{settings.API_V1_STR}/organizations/", headers=headers, json=org_data)
    org_content = response.json()
    org_admin_password = org_content["temporary_password"]

    login_data = {"username": org_admin_email, "password": org_admin_password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    org_admin_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    area_data = {"name": random_lower_string()}
    r_area = client.post(f"{settings.API_V1_STR}/areas/", headers=org_admin_headers, json=area_data)
    area_id = r_area.json()["id"]

    risk_data = {
        "process_name": random_lower_string(),
        "risk_description": random_lower_string(),
        "area_id": area_id,
        "prob_question_1": 2,
        "prob_question_2": 2,
        "prob_question_3": 2,
        "imp_question_1": 2,
        "imp_question_2": 2,
        "imp_question_3": 2
    }
    r_risk = client.post(f"{settings.API_V1_STR}/risks/", headers=org_admin_headers, json=risk_data)
    risk_id = r_risk.json()["id"]

    update_data = {"process_name": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/risks/{risk_id}", headers=org_admin_headers, json=update_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["process_name"] == update_data["process_name"]

