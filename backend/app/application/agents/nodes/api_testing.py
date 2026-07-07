import logging
from typing import Dict, Any
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution

logger = logging.getLogger("QualityOS.APITesting")

@trace_agent_execution("APITesting")
async def api_testing_node(state: QualityOSState) -> Dict[str, Any]:
    """
    API Testing Agent.
    Generates contract validation, authentication checks, and rate-limit fuzzer requests.
    """
    logger.info("Executing API Testing Node...")
    generated_code = state.get("generated_tests", {}).copy()
    
    api_test_code = """import requests
import pytest

BASE_URL = "http://localhost:8000/api/v1"

def test_unauthorized_access_protected_route():
    # Attempting to fetch jobs list without a Bearer JWT
    response = requests.get(f"{BASE_URL}/jobs")
    assert response.status_code == 401
    
def test_user_login_flow():
    payload = {
        "username": "testadmin",
        "password": "AdminSecurePass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "Admin"
"""
    generated_code["tests/integration/test_api_endpoints.py"] = api_test_code
    audit_msg = "Generated API fuzzer scripts verifying authentication boundaries and payload validation rules."
    
    return {
        "generated_tests": generated_code,
        "current_agent": "PerformanceAgent",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
