import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint_protection_unauthorized(client: AsyncClient):
    # Attempting to fetch jobs list without a token
    response = await client.get("/api/v1/jobs/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_rbac_forbidden_operation(client: AsyncClient):
    # 1. Register a Viewer user
    viewer_payload = {
        "username": "viewer_user",
        "email": "viewer@qualityos.io",
        "password": "Password123!",
        "role": "Viewer"
    }
    await client.post("/api/v1/auth/register", json=viewer_payload)
    
    # 2. Login as Viewer
    login_res = await client.post("/api/v1/auth/login", data={
        "username": "viewer_user",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    # 3. Attempt to trigger a job (requires Developer or higher)
    headers = {"Authorization": f"Bearer {token}"}
    job_payload = {
        "repository_url": "https://github.com/test/repo",
        "branch": "main"
    }
    response = await client.post("/api/v1/jobs/trigger", json=job_payload, headers=headers)
    assert response.status_code == 403
    assert "Operation forbidden" in response.json()["detail"]

@pytest.mark.asyncio
async def test_rbac_authorized_operation(client: AsyncClient):
    # 1. Register a Developer user
    dev_payload = {
        "username": "developer_user",
        "email": "dev@qualityos.io",
        "password": "Password123!",
        "role": "Developer"
    }
    await client.post("/api/v1/auth/register", json=dev_payload)
    
    # 2. Login as Developer
    login_res = await client.post("/api/v1/auth/login", data={
        "username": "developer_user",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    
    # 3. Trigger a job (requires Developer or higher)
    headers = {"Authorization": f"Bearer {token}"}
    job_payload = {
        "repository_url": "https://github.com/test/repo",
        "branch": "main"
    }
    response = await client.post("/api/v1/jobs/trigger", json=job_payload, headers=headers)
    assert response.status_code == 201
    
    data = response.json()
    assert data["repository_url"] == "https://github.com/test/repo"
    assert data["status"] == "PENDING"
