import logging
from langgraph.graph import StateGraph, END
from app.application.agents.state import QualityOSState

# Import node functions
from app.application.agents.nodes.repo_understanding import repo_understanding_node
from app.application.agents.nodes.requirement_intelligence import requirement_intelligence_node
from app.application.agents.nodes.risk_prediction import risk_prediction_node
from app.application.agents.nodes.strategy_agent import test_strategy_node
from app.application.agents.nodes.playwright_generator import playwright_generator_node
from app.application.agents.nodes.pytest_generator import pytest_generator_node
from app.application.agents.nodes.api_testing import api_testing_node
from app.application.agents.nodes.performance_agent import performance_agent_node
from app.application.agents.nodes.security_agent import security_agent_node
from app.application.agents.nodes.exploratory_agent import exploratory_agent_node
from app.application.agents.nodes.failure_reproduction import failure_reproduction_node
from app.application.agents.nodes.rca_agent import rca_node
from app.application.agents.nodes.debugging_copilot import debugging_copilot_node
from app.application.agents.nodes.coverage_intelligence import coverage_intelligence_node
from app.application.agents.nodes.learning_agent import learning_agent_node

logger = logging.getLogger("QualityOS.Orchestrator")

def route_after_reproduction(state: QualityOSState) -> str:
    """
    Conditional router that checks if failures were reproduced.
    Routs to RootCauseAnalysis if issues exist, otherwise continues to CoverageIntelligence.
    """
    failures = state.get("failures_reproduced", [])
    if len(failures) > 0:
        logger.info("Test failures detected. Routing to Root Cause Analysis...")
        return "RootCauseAnalysis"
    logger.info("All tests passed. Routing to Coverage Intelligence...")
    return "CoverageIntelligence"

def build_workflow() -> StateGraph:
    """Compiles the multi-agent execution pipeline in LangGraph."""
    workflow = StateGraph(QualityOSState)
    
    # 1. Register all specialized agents as Graph nodes
    workflow.add_node("RepositoryUnderstanding", repo_understanding_node)
    workflow.add_node("RequirementIntelligence", requirement_intelligence_node)
    workflow.add_node("RiskPrediction", risk_prediction_node)
    workflow.add_node("TestStrategy", test_strategy_node)
    workflow.add_node("PlaywrightGenerator", playwright_generator_node)
    workflow.add_node("PytestGenerator", pytest_generator_node)
    workflow.add_node("APITesting", api_testing_node)
    workflow.add_node("PerformanceAgent", performance_agent_node)
    workflow.add_node("SecurityAgent", security_agent_node)
    workflow.add_node("ExploratoryAgent", exploratory_agent_node)
    workflow.add_node("FailureReproduction", failure_reproduction_node)
    workflow.add_node("RootCauseAnalysis", rca_node)
    workflow.add_node("DebuggingCopilot", debugging_copilot_node)
    workflow.add_node("CoverageIntelligence", coverage_intelligence_node)
    workflow.add_node("LearningAgent", learning_agent_node)
    
    # 2. Define static execution edges
    workflow.set_entry_point("RepositoryUnderstanding")
    workflow.add_edge("RepositoryUnderstanding", "RequirementIntelligence")
    workflow.add_edge("RequirementIntelligence", "RiskPrediction")
    workflow.add_edge("RiskPrediction", "TestStrategy")
    workflow.add_edge("TestStrategy", "PlaywrightGenerator")
    workflow.add_edge("PlaywrightGenerator", "PytestGenerator")
    workflow.add_edge("PytestGenerator", "APITesting")
    workflow.add_edge("APITesting", "PerformanceAgent")
    workflow.add_edge("PerformanceAgent", "SecurityAgent")
    workflow.add_edge("SecurityAgent", "ExploratoryAgent")
    workflow.add_edge("ExploratoryAgent", "FailureReproduction")
    
    # 3. Add conditional router after execution phase
    workflow.add_conditional_edges(
        "FailureReproduction",
        route_after_reproduction,
        {
            "RootCauseAnalysis": "RootCauseAnalysis",
            "CoverageIntelligence": "CoverageIntelligence"
        }
    )
    
    workflow.add_edge("RootCauseAnalysis", "DebuggingCopilot")
    workflow.add_edge("DebuggingCopilot", "CoverageIntelligence")
    workflow.add_edge("CoverageIntelligence", "LearningAgent")
    workflow.add_edge("LearningAgent", END)
    
    return workflow

# Compiled runnable graph
quality_os_graph = build_workflow().compile()
