import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.auth_provider import auth_provider
from app.domain.models import User

@pytest.mark.asyncio
async def test_auth_provider_password_cryptography():
    password = "SuperSecretPassword123!"
    hashed = auth_provider.hash_password(password)
    
    assert hashed != password
    assert auth_provider.verify_password(password, hashed)
    assert not auth_provider.verify_password("WrongPassword123", hashed)

@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    payload = {
        "username": "qa_tester",
        "email": "tester@qualityos.io",
        "password": "SecurePassword123!",
        "role": "QA Engineer"
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "qa_tester"
    assert data["email"] == "tester@qualityos.io"
    assert data["role"] == "QA Engineer"
    assert "id" in data

@pytest.mark.asyncio
async def test_duplicate_user_registration(client: AsyncClient):
    payload = {
        "username": "duplicate_user",
        "email": "dup@qualityos.io",
        "password": "SecurePassword123!",
        "role": "Developer"
    }
    
    # First try
    response1 = await client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201
    
    # Second try
    response2 = await client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 400
    assert "already registered" in response2.json()["detail"]

@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient):
    # Setup user
    reg_payload = {
        "username": "login_test",
        "email": "login@qualityos.io",
        "password": "TestPassword123!",
        "role": "Developer"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)
    
    # Login try
    login_payload = {
        "username": "login_test",
        "password": "TestPassword123!"
    }
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "Developer"

@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient):
    login_payload = {
        "username": "non_existent",
        "password": "SomePassword"
    }
    response = await client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 401
    assert "Incorrect username" in response.json()["detail"]
