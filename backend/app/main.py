"""
Geko Backend - FastAPI Application
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.ai_core.ai_routes import router as ai_router

app = FastAPI(
    title="Geko API",
    description="API per il progetto Geko",
    version="1.0.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint root per test della API"""
    return {
        "message": "Geko API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    """Endpoint di test connessione database"""
    return {"status": "ok", "message": "Connessione database riuscita"}

# Include AI Core routes
app.include_router(ai_router)


