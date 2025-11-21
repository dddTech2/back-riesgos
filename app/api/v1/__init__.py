from fastapi import APIRouter

from app.api.v1.endpoints import example, organizations, login, areas, risks, controls, users, forms

api_router = APIRouter()
api_router.include_router(example.router, prefix="/example", tags=["example"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(areas.router, prefix="/areas", tags=["areas"])
api_router.include_router(risks.router, prefix="/risks", tags=["risks"])
api_router.include_router(controls.router, prefix="/controls", tags=["controls"])
api_router.include_router(forms.router, prefix="/forms", tags=["forms"])