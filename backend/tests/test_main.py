"""
Test per il backend Geko
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test endpoint root"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


