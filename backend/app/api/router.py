"""Router principale del backend Geko."""

from fastapi import APIRouter

from app.api.routes import health

router = APIRouter()

router.include_router(health.router, prefix="/health", tags=["Health"])


