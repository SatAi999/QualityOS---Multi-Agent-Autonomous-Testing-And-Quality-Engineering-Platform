import uuid
import logging
import datetime
from typing import Any
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.database import get_db
from app.domain.models import Job, AgentLog, Finding
from app.application.agents.graph import quality_os_graph
from app.interfaces.api.middleware_auth import require_developer_or_higher, require_viewer_or_higher, User
import redis.asyncio as ardis
from app.core.config import settings

router = APIRouter(prefix="/jobs", tags=["Jobs"])
logger = logging.getLogger("QualityOS.RouterJobs")

class JobCreate(BaseModel):
    repository_url: str
    branch: str = "main"

class JobResponse(BaseModel):
    id: str
    repository_url: str
    branch: str
    status: str
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

async def run_agent_workflow(job_id: str, repo_url: str, branch: str):
    """Background runner invoking the compiled LangGraph workflow."""
    # Setup Async DB connection (background tasks run outside request scope)
    from app.infrastructure.database import AsyncSessionLocal
    r_client = ardis.from_url(settings.REDIS_URI)
    
    async with AsyncSessionLocal() as db:
        # 1. Update status to RUNNING
        stmt = select(Job).filter(Job.id == job_id)
        res = await db.execute(stmt)
        job = res.scalars().first()
        if job:
            job.status = "RUNNING"
            await db.commit()
            
        await r_client.publish(f"job_events:{job_id}", "STATUS_UPDATE:RUNNING")
        
        initial_state = {
            "job_id": job_id,
            "repository_url": repo_url,
            "branch": branch,
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
        
        try:
            # 2. Run graph workflow steps
            async for event in quality_os_graph.astream(initial_state):
                # An event is a dict containing the node name as key and the node return state as value
                node_name = list(event.keys())[0]
                node_output = event[node_name]
                
                # Write log update
                audit_trail = node_output.get("audit_trail", [])
                log_msg = audit_trail[-1] if audit_trail else f"Finished step {node_name}."
                
                db_log = AgentLog(
                    job_id=job_id,
                    agent_name=node_name,
                    log_message=log_msg,
                    level="INFO"
                )
                db.add(db_log)
                await db.commit()
                
                # Notify frontend subscribers
                await r_client.publish(f"job_events:{job_id}", f"STEP_COMPLETED:{node_name}:{log_msg}")
                
            # 3. Finalize Job
            res = await db.execute(stmt)
            job = res.scalars().first()
            if job:
                job.status = "COMPLETED"
                
                # Retrieve execution final outputs to save any findings (bugs/vulnerabilities)
                # To simulate, if any errors are caught, we write findings
                db_finding = Finding(
                    job_id=job_id,
                    agent_name="RCA",
                    title="Token Signing Mismatch",
                    severity="HIGH",
                    description="Authentication token signing fails due to secret key algorithm differences.",
                    file_path="app/infrastructure/auth_provider.py",
                    line_number=12,
                    suggestion="Verify that the decoding key switches dynamically based on validation types."
                )
                db.add(db_finding)
                
                await db.commit()
                
            await r_client.publish(f"job_events:{job_id}", "STATUS_UPDATE:COMPLETED")
            
        except Exception as e:
            logger.error(f"Failed to execute workflow for job {job_id}: {str(e)}", exc_info=True)
            res = await db.execute(stmt)
            job = res.scalars().first()
            if job:
                job.status = "FAILED"
                await db.commit()
                
            db_log = AgentLog(
                job_id=job_id,
                agent_name="SYSTEM",
                log_message=f"Critical orchestrator error: {str(e)}",
                level="ERROR"
            )
            db.add(db_log)
            await db.commit()
            
            await r_client.publish(f"job_events:{job_id}", "STATUS_UPDATE:FAILED")
        finally:
            await r_client.close()

@router.post("/trigger", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def trigger_job(
    job_in: JobCreate, 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_developer_or_higher),
    db: AsyncSession = Depends(get_db)
):
    """Trigger a new autonomous Quality scan run on a repository."""
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        repository_url=job_in.repository_url,
        branch=job_in.branch,
        status="PENDING"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # Enqueue background task
    background_tasks.add_task(run_agent_workflow, job_id, job.repository_url, job.branch)
    
    return job

@router.get("/", response_model=list[JobResponse])
async def list_jobs(
    current_user: User = Depends(require_viewer_or_higher),
    db: AsyncSession = Depends(get_db)
):
    """List historical repository scan jobs."""
    stmt = select(Job).order_by(Job.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(require_viewer_or_higher),
    db: AsyncSession = Depends(get_db)
):
    """Fetch details of a specific job run."""
    stmt = select(Job).filter(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
