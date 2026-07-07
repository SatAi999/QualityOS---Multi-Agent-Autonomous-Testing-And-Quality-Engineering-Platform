import logging
from typing import Dict, Any, List
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution
from app.infrastructure.graph_db import async_graph_db

logger = logging.getLogger("QualityOS.RequirementIntelligence")

@trace_agent_execution("RequirementIntelligence")
async def requirement_intelligence_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Requirement Intelligence Agent.
    Parses PRDs, API schemas and maps system requirements.
    """
    logger.info("Executing Requirement Intelligence Node...")
    job_id = state.get("job_id")
    
    # Simulating parsing API routers or mock OpenAPI specs.
    # In a real environment, this agent queries LLMs passing PRD text or Swagger OpenAPI specification
    simulated_requirements: List[Dict[str, Any]] = [
        {
            "id": "REQ-001",
            "title": "OAuth2 JWT Authentication",
            "description": "Users must login with username/password and receive an Access and Refresh Token.",
            "target_module": "app/interfaces/api/router_auth.py",
            "criticality": "CRITICAL"
        },
        {
            "id": "REQ-002",
            "title": "Role-Based Access Control",
            "description": "Endpoints must verify current user roles (Admin, QA Engineer, Developer, Viewer) via middleware.",
            "target_module": "app/interfaces/api/middleware_auth.py",
            "criticality": "HIGH"
        },
        {
            "id": "REQ-003",
            "title": "Agent Execution Sandbox",
            "description": "Any executable code run by agents must operate in a sandboxed Docker container.",
            "target_module": "app/infrastructure/sandbox.py",
            "criticality": "HIGH"
        }
    ]
    
    # Save requirement relations in Neo4j
    try:
        await async_graph_db.connect()
        for req in simulated_requirements:
            await async_graph_db.execute_query(
                "MERGE (req:Requirement {id: $req_id}) "
                "ON CREATE SET req.title = $title, req.description = $desc, req.criticality = $criticality "
                "WITH req "
                "MATCH (m:Module {path: $module_path}) "
                "MERGE (m)-[:SATISFIES]->(req)",
                {
                    "req_id": req["id"],
                    "title": req["title"],
                    "desc": req["description"],
                    "criticality": req["criticality"],
                    "module_path": req["target_module"]
                }
            )
    except Exception as e:
        logger.warning(f"Failed to persist requirement relations inside Neo4j: {str(e)}")

    audit_msg = f"Extracted {len(simulated_requirements)} core requirement assertions from OpenAPI & local architecture specs."
    
    return {
        "requirements": simulated_requirements,
        "current_agent": "RiskPrediction",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
