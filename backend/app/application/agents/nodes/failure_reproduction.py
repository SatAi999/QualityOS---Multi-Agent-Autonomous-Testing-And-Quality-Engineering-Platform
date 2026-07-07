import os
import shutil
import logging
from typing import Dict, Any, List
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution
from app.infrastructure.sandbox import sandbox_manager

logger = logging.getLogger("QualityOS.FailureReproduction")

@trace_agent_execution("FailureReproduction")
async def failure_reproduction_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Failure Reproduction Agent.
    Executes the generated testing suites inside the Sandbox execution manager
    and parses stdout logs, trace maps, and exit codes.
    """
    logger.info("Executing Failure Reproduction Node...")
    generated_tests = state.get("generated_tests", {})
    job_id = state.get("job_id")
    
    # Establish a local run-context folder inside workspace
    run_dir = f"d:/Quality_OS/backend/run_{job_id}"
    os.makedirs(run_dir, exist_ok=True)
    
    results: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []
    
    try:
        # Write tests to directory
        for path, code in generated_tests.items():
            test_file_path = os.path.join(run_dir, os.path.basename(path))
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(code)
                
        # For simulation, we run pytest on the unit test files.
        # We invoke the sandbox manager to run 'pytest' inside run_dir
        logger.info(f"Triggering sandbox test suite run for job: {job_id}")
        exit_code, stdout, stderr = sandbox_manager.execute_in_sandbox(
            command="python -m pytest", 
            workspace_dir=run_dir
        )
        
        # Parse test outcomes
        # Since we're executing simulated tests, let's verify if they pass or fail.
        # To simulate a reproduction task, we insert a mock assertion failure if a trigger file exists,
        # otherwise we read the actual sandbox return values.
        status = "COMPLETED" if exit_code == 0 else "FAILED"
        
        results.append({
            "command": "python -m pytest",
            "exit_code": exit_code,
            "status": status,
            "stdout": stdout,
            "stderr": stderr
        })
        
        if exit_code != 0:
            failures.append({
                "type": "PYTEST_FAILURE",
                "error_log": stdout or stderr,
                "command": "python -m pytest"
            })
            
    except Exception as e:
        logger.error(f"Error during sandbox execution: {str(e)}")
        results.append({
            "command": "python -m pytest",
            "exit_code": -1,
            "status": "ERROR",
            "stderr": str(e)
        })
    finally:
        # Cleanup run context directory
        try:
            shutil.rmtree(run_dir, ignore_errors=True)
        except Exception:
            pass
            
    audit_msg = f"Executed testing suites inside container sandbox. Status: {results[0]['status']}. Exit Code: {results[0]['exit_code']}."
    
    return {
        "execution_results": results,
        "failures_reproduced": failures,
        "current_agent": "RootCauseAnalysis" if len(failures) > 0 else "CoverageIntelligence",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
