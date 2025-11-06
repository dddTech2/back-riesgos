from fastapi import APIRouter

from app.api.v1.endpoints import example, organizations, login

api_router = APIRouter()
api_router.include_router(example.router, prefix="/example", tags=["example"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(login.router, tags=["login"])