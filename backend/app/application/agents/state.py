from typing import Dict, List, Any, Optional, TypedDict

class QualityOSState(TypedDict):
    """
    State dictionary managed by the LangGraph orchestrator.
    Captures intermediate data, analysis outputs, test codes, and agent execution results.
    """
    job_id: str
    repository_url: str
    branch: str
    commit_sha: Optional[str]
    
    # 1. Repository Understanding Agent
    repo_info: Dict[str, Any]
    
    # 2. Requirement Intelligence Agent
    requirements: List[Dict[str, Any]]
    
    # 3. Risk Prediction Agent
    risk_heatmap: Dict[str, Any]
    
    # 4. Test Strategy Agent
    test_strategy: Dict[str, Any]
    
    # 5/6/7. Test Generation Agents (Playwright, Pytest, API testing)
    generated_tests: Dict[str, str] # Map of filename -> code content
    
    # Execution records
    execution_results: List[Dict[str, Any]]
    
    # 11/12/13. Failure reproduction, RCA, and Debugging
    failures_reproduced: List[Dict[str, Any]]
    rca_findings: List[Dict[str, Any]]
    debugging_suggestions: List[Dict[str, Any]]
    
    # 14. Coverage Intelligence
    coverage_metrics: Dict[str, Any]
    
    # Global execution metadata
    current_agent: str
    errors: List[str]
    audit_trail: List[str]
