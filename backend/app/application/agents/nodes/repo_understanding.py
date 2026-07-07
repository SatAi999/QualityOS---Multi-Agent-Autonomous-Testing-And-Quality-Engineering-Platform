import os
import ast
import logging
from typing import Dict, Any
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution
from app.infrastructure.graph_db import async_graph_db

logger = logging.getLogger("QualityOS.RepoUnderstanding")

class RepoAnalyzer:
    """
    Statically analyzes source code repositories.
    Parses Python ASTs, maps packages, and discovers system modules.
    """
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.modules = []
        self.dependencies = []

    def scan(self) -> Dict[str, Any]:
        """Traverse directory, identify file structures and build dependency trees."""
        if not os.path.exists(self.workspace_path):
            return {"error": f"Workspace path {self.workspace_path} does not exist."}

        for root, dirs, files in os.walk(self.workspace_path):
            # Exclude standard directories
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules", "venv", ".venv")]
            
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.workspace_path)
                    self._analyze_python_file(full_path, rel_path)
                    
        return {
            "modules": self.modules,
            "dependencies": self.dependencies,
            "complexity_summary": "Scan completed. Modules analyzed: " + str(len(self.modules))
        }

    def _analyze_python_file(self, full_path: str, rel_path: str):
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            tree = ast.parse(content)
            imports = []
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Extract imports
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        imports.append(f"{node.module or ''}.{node.names[0].name}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    
            self.modules.append({
                "path": rel_path.replace("\\", "/"),
                "classes": classes,
                "functions": functions,
                "lines_of_code": len(content.splitlines())
            })
            
            for imp in imports:
                self.dependencies.append({
                    "source": rel_path.replace("\\", "/"),
                    "target": imp
                })
        except Exception as e:
            logger.error(f"Error parsing AST for file {rel_path}: {str(e)}")

@trace_agent_execution("RepositoryUnderstanding")
async def repo_understanding_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Repository Understanding Agent.
    Orchestrates AST parsing, records dependency graphs inside Neo4j.
    """
    logger.info("Executing Repository Understanding Node...")
    job_id = state.get("job_id")
    repo_url = state.get("repository_url")
    branch = state.get("branch", "main")
    
    # Resolve workspace dynamically
    workspace_runs_dir = "/workspace/workspace_runs"
    os.makedirs(workspace_runs_dir, exist_ok=True)
    job_workspace = os.path.join(workspace_runs_dir, job_id)
    
    actual_workspace = None
    
    # 1. Check if repo_url is an existing local folder path
    if os.path.exists(repo_url) and os.path.isdir(repo_url):
        actual_workspace = repo_url
        logger.info(f"Scanning local path: {actual_workspace}")
    # 2. Check if repo_url is a Git URL
    elif repo_url.startswith(("http://", "https://", "git@")):
        import subprocess
        try:
            logger.info(f"Cloning Git URL: {repo_url} (branch: {branch}) to {job_workspace}")
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, job_workspace],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=45
            )
            actual_workspace = job_workspace
        except Exception as clone_err:
            logger.error(f"Failed to clone repo, falling back: {str(clone_err)}")
            actual_workspace = "/workspace"
    else:
        actual_workspace = "/workspace"
        
    logger.info(f"Resolved workspace target to: {actual_workspace}")
    analyzer = RepoAnalyzer(actual_workspace)
    scan_results = analyzer.scan()
    
    # Save graph relationships into Neo4j
    try:
        await async_graph_db.connect()
        # Seed Repo node
        await async_graph_db.execute_query(
            "MERGE (r:Repository {url: $url}) ON CREATE SET r.job_id = $job_id",
            {"url": repo_url, "job_id": job_id}
        )
        # Store module dependencies
        for module in scan_results.get("modules", []):
            await async_graph_db.execute_query(
                "MATCH (r:Repository {url: $url}) "
                "MERGE (m:Module {path: $path}) "
                "SET m.lines_of_code = $loc "
                "MERGE (r)-[:CONTAINS]->(m)",
                {"url": repo_url, "path": module["path"], "loc": module["lines_of_code"]}
            )
    except Exception as e:
        logger.warning(f"Failed to persist dependency graph to Neo4j: {str(e)}")
        
    audit_msg = f"Completed repository understanding scan. Discovered {len(scan_results.get('modules', []))} modules."
    
    return {
        "repo_info": scan_results,
        "current_agent": "RequirementIntelligence",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
