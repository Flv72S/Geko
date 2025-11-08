"""Applicazione FastAPI principale per il backend Geko."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router as api_router
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.logging_config import setup_logging

try:  # Manteniamo l'integrazione con l'AI Core se disponibile
    from app.ai_core.ai_routes import router as ai_router
except ImportError:  # pragma: no cover
    ai_router = None

# Inizializza logging prima di creare l'app
setup_logging()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
if ai_router is not None:
    app.include_router(ai_router)

register_error_handlers(app)


@app.get("/", tags=["System"], summary="Root API status")
async def root_status() -> dict:
    """Endpoint base per verificare lo stato del backend."""
    return {
        "message": "Geko Backend ready",
        "service": settings.APP_NAME,
        "environment": settings.ENV,
    }
