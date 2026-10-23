from fastapi import APIRouter

from app.routers import admin, auth, courier, health, shipments, uploads

api_router = APIRouter()
for module in (health, auth, shipments, courier, uploads, admin):
    api_router.include_router(module.router)
