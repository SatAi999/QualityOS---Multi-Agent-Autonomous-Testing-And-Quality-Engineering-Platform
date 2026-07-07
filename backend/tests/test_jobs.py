import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_trigger_and_retrieve_job_details(client: AsyncClient):
    # 1. Register and login as Admin
    admin_payload = {
        "username": "admin_user",
        "email": "admin@qualityos.io",
        "password": "AdminPassword123!",
        "role": "Admin"
    }
    await client.post("/api/v1/auth/register", json=admin_payload)
    
    login_res = await client.post("/api/v1/auth/login", data={
        "username": "admin_user",
        "password": "AdminPassword123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Trigger repository run
    job_payload = {
        "repository_url": "https://github.com/mock/repo",
        "branch": "main"
    }
    trigger_res = await client.post("/api/v1/jobs/trigger", json=job_payload, headers=headers)
    assert trigger_res.status_code == 201
    job_id = trigger_res.json()["id"]
    
    # 3. Retrieve single run details
    get_res = await client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["repository_url"] == "https://github.com/mock/repo"
    
    # 4. List all historical scans
    list_res = await client.get("/api/v1/jobs/", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
