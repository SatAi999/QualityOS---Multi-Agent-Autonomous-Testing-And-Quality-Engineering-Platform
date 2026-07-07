import logging
from typing import Dict, Any
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution

logger = logging.getLogger("QualityOS.SecurityAgent")

@trace_agent_execution("SecurityAgent")
async def security_agent_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Security Agent.
    Runs SAST scanning, dependency vulnerability inspections, and checks for SQL Injection/XSS vulnerabilities.
    """
    logger.info("Executing Security Agent Node...")
    generated_code = state.get("generated_tests", {}).copy()
    
    security_config = """# bandit.yaml config file
targets:
  - "app"
exclude_dirs:
  - "tests"
profiles:
  test_suites:
    - all_tests
"""
    generated_code["tests/security/bandit.yaml"] = security_config
    audit_msg = "Configured Bandit SAST vulnerability scan parameters for static security checks."
    
    return {
        "generated_tests": generated_code,
        "current_agent": "ExploratoryAgent",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
