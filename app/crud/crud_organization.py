import random
import string
from typing import Dict, Union, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.db.models.organization import Organization
from app.db.models.user import User
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.core.security import get_password_hash

def generate_temporary_password(length: int = 12) -> str:
    """Genera una contraseña temporal segura sin caracteres especiales problemáticos."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))

class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    def create_with_initial_admin(self, db: Session, *, org_in: OrganizationCreate):
        """
        Crea una nueva organización y su usuario administrador inicial en una transacción.
        """
        # 1. Verificar si la organización o el email ya existen
        existing_org = db.query(Organization).filter(Organization.name == org_in.name).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An organization with this name already exists.",
            )

        existing_user = db.query(User).filter(User.email == org_in.admin_email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        # La sesión actúa como una transacción
        try:
            # 2. Crear la organización
            new_organization = Organization(name=org_in.name)
            db.add(new_organization)
            db.flush()  # Para obtener el ID de la nueva organización

            # 3. Generar contraseña y crear el usuario administrador
            temp_password = generate_temporary_password()
            hashed_password = get_password_hash(temp_password)

            new_admin = User(
                organization_id=new_organization.id,
                email=org_in.admin_email,
                password_hash=hashed_password,
                full_name=org_in.admin_full_name,
                role="admin",
                is_active=True,
            )
            db.add(new_admin)

            db.commit()
            db.refresh(new_organization)
            db.refresh(new_admin)
            
            return {
                "organization": new_organization, 
                "admin_user": new_admin,
                "temporary_password": temp_password
            }

        except Exception as e:
            db.rollback()
            # Log the exception e
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during organization creation.",
            )

organization = CRUDOrganization(Organization)
