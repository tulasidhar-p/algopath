import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.services.jwt_service import JWTService

@pytest.fixture(name="client")
def client_fixture(db_session):
    """Fixture to generate a TestClient with database session overrides."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_api_register_success(client, seeded_topics):
    payload = {
        "name": "API User",
        "email": "api@example.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API User"
    assert data["email"] == "api@example.com"
    assert "id" in data
    assert "password" not in data

def test_api_register_duplicate(client, seeded_topics):
    payload = {
        "name": "API User",
        "email": "api@example.com",
        "password": "strongpassword123"
    }
    client.post("/api/auth/register", json=payload)
    
    # Attempting duplicate registration
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "exists" in response.json()["detail"].lower()

def test_api_register_validation_error(client):
    # Invalid email format
    payload = {
        "name": "User",
        "email": "invalid_email",
        "password": "strongpassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    
    # Password too short (min_length=8)
    payload = {
        "name": "User",
        "email": "valid@example.com",
        "password": "short"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422

def test_api_login_success(client, seeded_topics):
    # Register first
    client.post("/api/auth/register", json={
        "name": "Login Test",
        "email": "logintest@example.com",
        "password": "strongpassword123"
    })
    
    # Try successful login
    response = client.post("/api/auth/login", json={
        "email": "logintest@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_api_login_invalid_credentials(client, seeded_topics):
    client.post("/api/auth/register", json={
        "name": "Login Test",
        "email": "logintest@example.com",
        "password": "strongpassword123"
    })
    
    # Login with wrong password
    response = client.post("/api/auth/login", json={
        "email": "logintest@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()
    
    # Login with unknown email
    response = client.post("/api/auth/login", json={
        "email": "unknown@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_api_get_me_success(client, seeded_topics):
    # Register and login
    client.post("/api/auth/register", json={
        "name": "Me User",
        "email": "me@example.com",
        "password": "strongpassword123"
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "me@example.com",
        "password": "strongpassword123"
    })
    token = login_resp.json()["access_token"]
    
    # Retrieve current user profile
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Me User"
    assert data["email"] == "me@example.com"
    assert "password" not in data

def test_api_get_me_unauthorized_token_failures(client, seeded_topics, monkeypatch):
    # 1. Missing Authorization header
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    
    # 2. Malformed token
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_format_token"})
    assert response.status_code == 401
    
    # 3. Expired token
    monkeypatch.setattr(JWTService, "ACCESS_TOKEN_EXPIRE_MINUTES", -5)
    expired_token = JWTService.create_access_token("me@example.com")
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401

def test_api_get_me_invalid_scheme(client, seeded_topics):
    # Register and login
    client.post("/api/auth/register", json={
        "name": "Scheme User",
        "email": "scheme@example.com",
        "password": "strongpassword123"
    })
    login_resp = client.post("/api/auth/login", json={
        "email": "scheme@example.com",
        "password": "strongpassword123"
    })
    token = login_resp.json()["access_token"]
    
    # Verify rejection of Basic schema (Refinement 6)
    response1 = client.get("/api/auth/me", headers={"Authorization": f"Basic {token}"})
    assert response1.status_code == 401
    
    # Verify rejection of custom Token schema
    response2 = client.get("/api/auth/me", headers={"Authorization": f"Token {token}"})
    assert response2.status_code == 401
    
    # Verify rejection of plain token value without scheme prefix
    response3 = client.get("/api/auth/me", headers={"Authorization": f"{token}"})
    assert response3.status_code == 401
