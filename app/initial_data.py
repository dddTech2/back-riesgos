import logging
import os
from sqlalchemy.orm import Session
from app.crud.crud_user import user
from app.schemas.user import UserCreate
from app.db.models.role import Role
from app.db.models.organization import Organization
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    logger.info("Creating initial data")
    # Create roles
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        logger.info("Creating admin role")
        admin_role = Role(name="admin")
        db.add(admin_role)
    else:
        logger.info("Admin role already exists")

    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        logger.info("Creating user role")
        user_role = Role(name="user")
        db.add(user_role)
    else:
        logger.info("User role already exists")

    # Create master organization
    master_org = db.query(Organization).filter(Organization.name == "Master").first()
    if not master_org:
        logger.info("Creating Master organization")
        master_org = Organization(name="Master")
        db.add(master_org)
    else:
        logger.info("Master organization already exists")

    db.commit()
    db.refresh(master_org)

    # Create superuser
    superuser_email = settings.SUPERUSER_EMAIL
    superuser_password = settings.SUPERUSER_PASSWORD
    logger.info(f"Attempting to create superuser with email: {superuser_email}")


    if superuser_email and superuser_password:
        superuser = user.get_by_email(db, email=superuser_email)
        if not superuser:
            logger.info(f"Creating superuser: {superuser_email} linked to Master organization (ID: {master_org.id})")
            user_in = UserCreate(
                email=superuser_email,
                password=superuser_password,
                is_superuser=True,
                organization_id=master_org.id,
                role="superuser",
            )
            superuser = user.create(db, obj_in=user_in)
            superuser.roles.append(admin_role)
            db.commit()
            logger.info(f"Superuser {superuser_email} created successfully")
        else:
            logger.info(f"Superuser {superuser_email} already exists")
    else:
        
        logger.warning(f"{superuser_email} and/or SUPERUSER_PASSWORD not set in environment variables. Skipping superuser creation.")
    logger.info("Initial data creation finished")


if __name__ == "__main__":
    from app.db.session import SessionLocal
    logger.info("Initializing database session")
    db = SessionLocal()
    init_db(db)
    logger.info("Database session closed")