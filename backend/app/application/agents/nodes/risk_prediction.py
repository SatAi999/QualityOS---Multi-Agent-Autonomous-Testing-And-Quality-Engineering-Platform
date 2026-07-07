import logging
from typing import Dict, Any
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution

logger = logging.getLogger("QualityOS.RiskPrediction")

@trace_agent_execution("RiskPrediction")
async def risk_prediction_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Risk Prediction Agent.
    Evaluates file changes, dependency density, and complexity to compute risk heatmaps.
    """
    logger.info("Executing Risk Prediction Node...")
    repo_info = state.get("repo_info", {})
    modules = repo_info.get("modules", [])
    
    heatmap = {}
    
    # Calculate risk score based on Lines of Code (LOC) and relative module connections.
    # Higher complexity & size raises the risk profile.
    for mod in modules:
        path = mod.get("path")
        loc = mod.get("lines_of_code", 0)
        class_count = len(mod.get("classes", []))
        func_count = len(mod.get("functions", []))
        
        # Calculate dynamic risk score (out of 100)
        base_score = min(loc * 0.1, 50.0) # LOC weight
        complexity_score = min((class_count * 5) + (func_count * 2), 30.0) # structure weight
        churn_factor = 15.0 # mock git modification churn factor
        
        risk_score = round(base_score + complexity_score + churn_factor, 1)
        
        severity = "LOW"
        if risk_score > 75.0:
            severity = "CRITICAL"
        elif risk_score > 55.0:
            severity = "HIGH"
        elif risk_score > 30.0:
            severity = "MEDIUM"
            
        heatmap[path] = {
            "score": risk_score,
            "severity": severity,
            "metrics": {
                "loc": loc,
                "complexity_index": class_count + func_count
            }
        }
        
    audit_msg = f"Calculated risk heatmap scores for {len(heatmap)} system modules. Found {sum(1 for v in heatmap.values() if v['severity'] in ('HIGH', 'CRITICAL'))} high-risk modules."
    
    return {
        "risk_heatmap": heatmap,
        "current_agent": "TestStrategy",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
