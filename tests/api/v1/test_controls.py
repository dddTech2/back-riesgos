from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_lower_string, random_email

def test_create_control(client: TestClient, db: Session) -> None:
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

    control_data = {
        "description": random_lower_string(),
        "type": "Manual",
        "eff_prob_question_1": 1.0,
        "eff_prob_question_2": 1.0,
        "eff_prob_question_3": 1.0,
        "eff_imp_question_1": 1.0,
        "eff_imp_question_2": 1.0,
        "eff_imp_question_3": 1.0
    }
    response = client.post(
        f"{settings.API_V1_STR}/controls/", headers=org_admin_headers, json=control_data
    )
    assert response.status_code == 201
    content = response.json()
    assert content["description"] == control_data["description"]

def test_read_controls(client: TestClient, db: Session) -> None:
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

    response = client.get(f"{settings.API_V1_STR}/controls/", headers=org_admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_control(client: TestClient, db: Session) -> None:
    # Setup Org, Admin, Control
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

    control_data = {
        "description": random_lower_string(),
        "type": "Manual",
        "eff_prob_question_1": 1.0,
        "eff_prob_question_2": 1.0,
        "eff_prob_question_3": 1.0,
        "eff_imp_question_1": 1.0,
        "eff_imp_question_2": 1.0,
        "eff_imp_question_3": 1.0
    }
    r_control = client.post(
        f"{settings.API_V1_STR}/controls/", headers=org_admin_headers, json=control_data
    )
    control_id = r_control.json()["id"]

    update_data = {"description": random_lower_string()}
    response = client.put(
        f"{settings.API_V1_STR}/controls/{control_id}", headers=org_admin_headers, json=update_data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["description"] == update_data["description"]

