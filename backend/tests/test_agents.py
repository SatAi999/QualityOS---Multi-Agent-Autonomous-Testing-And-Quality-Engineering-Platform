import pytest
from app.application.agents.nodes.repo_understanding import repo_understanding_node
from app.application.agents.nodes.requirement_intelligence import requirement_intelligence_node
from app.application.agents.nodes.risk_prediction import risk_prediction_node
from app.application.agents.nodes.strategy_agent import test_strategy_node as run_strategy_node
from app.application.agents.nodes.playwright_generator import playwright_generator_node
from app.application.agents.nodes.pytest_generator import pytest_generator_node
from app.application.agents.state import QualityOSState

@pytest.mark.asyncio
async def test_repo_understanding_node_execution():
    initial_state: QualityOSState = {
        "job_id": "test-job-uuid",
        "repository_url": "https://github.com/mock/repo",
        "branch": "main",
        "commit_sha": None,
        "repo_info": {},
        "requirements": [],
        "risk_heatmap": {},
        "test_strategy": {},
        "generated_tests": {},
        "execution_results": [],
        "failures_reproduced": [],
        "rca_findings": [],
        "debugging_suggestions": [],
        "coverage_metrics": {},
        "current_agent": "RepositoryUnderstanding",
        "errors": [],
        "audit_trail": []
    }
    
    # Run RepositoryUnderstanding node
    result = await repo_understanding_node(initial_state)
    assert "repo_info" in result
    assert result["current_agent"] == "RequirementIntelligence"
    assert len(result["audit_trail"]) == 1

@pytest.mark.asyncio
async def test_requirement_intelligence_node_execution():
    initial_state: QualityOSState = {
        "job_id": "test-job-uuid",
        "repository_url": "https://github.com/mock/repo",
        "branch": "main",
        "commit_sha": None,
        "repo_info": {},
        "requirements": [],
        "risk_heatmap": {},
        "test_strategy": {},
        "generated_tests": {},
        "execution_results": [],
        "failures_reproduced": [],
        "rca_findings": [],
        "debugging_suggestions": [],
        "coverage_metrics": {},
        "current_agent": "RequirementIntelligence",
        "errors": [],
        "audit_trail": []
    }
    
    result = await requirement_intelligence_node(initial_state)
    assert "requirements" in result
    assert len(result["requirements"]) == 3
    assert result["current_agent"] == "RiskPrediction"

@pytest.mark.asyncio
async def test_risk_prediction_node_execution():
    initial_state: QualityOSState = {
        "job_id": "test-job-uuid",
        "repository_url": "https://github.com/mock/repo",
        "branch": "main",
        "commit_sha": None,
        "repo_info": {
            "modules": [
                {"path": "app/main.py", "lines_of_code": 50, "classes": [], "functions": ["read_root"]}
            ]
        },
        "requirements": [],
        "risk_heatmap": {},
        "test_strategy": {},
        "generated_tests": {},
        "execution_results": [],
        "failures_reproduced": [],
        "rca_findings": [],
        "debugging_suggestions": [],
        "coverage_metrics": {},
        "current_agent": "RiskPrediction",
        "errors": [],
        "audit_trail": []
    }
    
    result = await risk_prediction_node(initial_state)
    assert "risk_heatmap" in result
    assert "app/main.py" in result["risk_heatmap"]
    assert result["current_agent"] == "TestStrategy"

@pytest.mark.asyncio
async def test_strategy_node_execution():
    initial_state: QualityOSState = {
        "job_id": "test-job-uuid",
        "repository_url": "https://github.com/mock/repo",
        "branch": "main",
        "commit_sha": None,
        "repo_info": {},
        "requirements": [
            {"id": "REQ-001", "target_module": "app/infrastructure/auth_provider.py", "criticality": "CRITICAL"}
        ],
        "risk_heatmap": {
            "app/infrastructure/auth_provider.py": {"score": 79.2, "severity": "CRITICAL"}
        },
        "test_strategy": {},
        "generated_tests": {},
        "execution_results": [],
        "failures_reproduced": [],
        "rca_findings": [],
        "debugging_suggestions": [],
        "coverage_metrics": {},
        "current_agent": "TestStrategy",
        "errors": [],
        "audit_trail": []
    }
    
    result = await run_strategy_node(initial_state)
    assert "test_strategy" in result
    assert result["current_agent"] == "PlaywrightGenerator"
    assert len(result["test_strategy"]["plans"]) == 1
    assert "PYTEST_UNIT" in result["test_strategy"]["plans"][0]["recommended_suites"]
