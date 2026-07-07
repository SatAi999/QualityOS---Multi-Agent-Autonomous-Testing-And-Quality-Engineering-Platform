import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.infrastructure.database import init_db, AsyncSessionLocal
from app.domain.models import User
from app.infrastructure.auth_provider import auth_provider
from sqlalchemy.future import select

# Import routers
from app.interfaces.api.router_auth import router as auth_router
from app.interfaces.api.router_jobs import router as jobs_router
from app.interfaces.api.router_observability import router as obs_router
from app.interfaces.api.router_websocket import router as ws_router

logger = logging.getLogger("QualityOS.Main")

app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous AI Quality Engineering Platform API Gateway",
    version="1.0.0"
)

# Configure CORS for local react client connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock down to the frontend domain name
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(obs_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initializes tables and seeds dummy admin credentials."""
    logger.info("Initializing PostgreSQL database...")
    await init_db()
    
    # Seed default Admin account if empty
    async with AsyncSessionLocal() as db:
        stmt = select(User).filter(User.username == "testadmin")
        result = await db.execute(stmt)
        admin = result.scalars().first()
        
        if not admin:
            logger.info("Seeding database with default Admin credentials...")
            hashed_pwd = auth_provider.hash_password("AdminSecurePass123!")
            default_admin = User(
                username="testadmin",
                email="admin@qualityos.io",
                hashed_password=hashed_pwd,
                role="Admin"
            )
            db.add(default_admin)
            await db.commit()
            logger.info("Database seeding completed.")

@app.get("/")
def read_root():
    return {"status": "QualityOS API Gateway Running", "version": "1.0.0"}
