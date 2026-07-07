import logging
from typing import Dict, Any, List
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution

logger = logging.getLogger("QualityOS.TestStrategy")

@trace_agent_execution("TestStrategy")
async def test_strategy_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Test Strategy Agent.
    Formulates a comprehensive testing strategy based on requirement maps and module risk levels.
    """
    logger.info("Executing Test Strategy Node...")
    requirements = state.get("requirements", [])
    risk_heatmap = state.get("risk_heatmap", {})
    
    strategy_plans: List[Dict[str, Any]] = []
    
    # Map requirements to appropriate test categories
    for req in requirements:
        req_id = req.get("id")
        target = req.get("target_module")
        criticality = req.get("criticality")
        
        # Get target module risk
        risk_profile = risk_heatmap.get(target, {"score": 10.0, "severity": "LOW"})
        
        # Determine test suites needed
        suites = []
        if "auth" in target or "middleware" in target:
            suites.extend(["PYTEST_UNIT", "API_CONTRACT", "SECURITY_AUTH_BYPASS"])
        if "sandbox" in target:
            suites.extend(["PYTEST_INTEGRATION", "PERFORMANCE_STRESS"])
            
        strategy_plans.append({
            "requirement_id": req_id,
            "module": target,
            "risk_score": risk_profile["score"],
            "recommended_suites": suites,
            "status": "PLANNED"
        })
        
    audit_msg = f"Generated enterprise testing strategy. Scheduled {sum(len(p['recommended_suites']) for p in strategy_plans)} individual test suites across requirements."
    
    return {
        "test_strategy": {
            "version": "1.0.0",
            "plans": strategy_plans
        },
        "current_agent": "PlaywrightGenerator",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
