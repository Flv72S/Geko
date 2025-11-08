"""Endpoint di health-check per il backend Geko."""

import time

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Health Check")
async def health_check() -> dict:
    """Restituisce lo stato di salute del servizio."""
    return {
        "status": "ok",
        "service": "geko-backend",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

