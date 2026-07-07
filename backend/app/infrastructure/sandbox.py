import os
import subprocess
import logging
from typing import Dict, Any, Optional, Tuple
import docker
from app.core.config import settings

logger = logging.getLogger(settings.APP_NAME)

class SandboxManager:
    """
    Spawns isolated sandboxes to execute untrusted code (Playwright, Pytest, security tools, performance scripts).
    Uses Docker daemon in production/staging environments, with host-process fallback for developer machine setups.
    """
    def __init__(self):
        self.docker_client: Optional[docker.DockerClient] = None
        self.use_docker = False
        
        try:
            # Connect to local/remote Docker environment
            self.docker_client = docker.from_env()
            # Test docker connection
            self.docker_client.ping()
            self.use_docker = True
            logger.info("Docker SDK connected successfully. Sandboxed execution enabled.")
        except Exception as e:
            logger.warning(
                f"Could not connect to Docker daemon: {str(e)}. "
                "Falling back to local host subprocesses for test execution. "
                "WARNING: Local execution is NOT sandboxed and lacks secure isolation!"
            )

    def execute_in_sandbox(
        self, 
        command: str, 
        workspace_dir: str, 
        env_vars: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        """
        Executes a test execution command within the workspace directory.
        
        Returns:
            Tuple[exit_code, stdout, stderr]
        """
        if self.use_docker and self.docker_client:
            return self._run_docker(command, workspace_dir, env_vars or {})
        else:
            return self._run_local_subprocess(command, workspace_dir, env_vars or {})

    def _run_docker(self, command: str, workspace_dir: str, env_vars: Dict[str, str]) -> Tuple[int, str, str]:
        """Execute command in a disposable Docker container."""
        container = None
        try:
            # Mount the workspace directory to /workspace inside the container
            absolute_workspace = os.path.abspath(workspace_dir)
            
            logger.info(f"Spawning sandbox container for command: {command}")
            container = self.docker_client.containers.create(
                image=settings.SANDBOX_IMAGE,
                command=f"sh -c '{command}'",
                working_dir="/workspace",
                volumes={
                    absolute_workspace: {
                        "bind": "/workspace",
                        "mode": "rw"
                    }
                },
                environment=env_vars,
                network_mode="bridge",
                mem_limit="1g", # Restrict resources
                nano_cpus=1000000000, # Limit to 1 CPU core
                detach=True
            )
            
            container.start()
            # Wait for execution (timeout 5 minutes)
            result = container.wait(timeout=300)
            exit_code = result.get("StatusCode", -1)
            
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="ignore")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="ignore")
            
            return exit_code, stdout, stderr
            
        except Exception as e:
            logger.error(f"Docker sandbox execution error: {str(e)}")
            return -1, "", f"Failed to execute command in sandbox: {str(e)}"
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    def _run_local_subprocess(self, command: str, workspace_dir: str, env_vars: Dict[str, str]) -> Tuple[int, str, str]:
        """Execute command directly in a local shell process (fallback)."""
        logger.info(f"Executing command locally (Non-sandboxed): {command}")
        
        # Merge environment variables
        current_env = os.environ.copy()
        current_env.update(env_vars)
        
        try:
            result = subprocess.run(
                command,
                cwd=workspace_dir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=current_env,
                timeout=300
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as e:
            return -1, e.stdout.decode() if e.stdout else "", "Execution timeout exceeded (300s)."
        except Exception as e:
            return -1, "", f"Subprocess exception: {str(e)}"

sandbox_manager = SandboxManager()
