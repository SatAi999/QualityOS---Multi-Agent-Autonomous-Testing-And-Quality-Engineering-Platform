from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.database import get_db
from app.domain.models import User
from app.infrastructure.auth_provider import auth_provider

# oauth2 scheme configuration pointing to local login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency that decodes JWT access tokens and fetches the matching user.
    Raises 401 Unauthorized for invalid/expired tokens.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth_provider.decode_token(token, is_refresh=False)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception
        
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user account")
    return user

class RoleChecker:
    """
    Role-Based Access Control checker. Enforces endpoint protection
    based on User roles (Admin, QA Engineer, Developer, Viewer).
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation forbidden. Required roles: {self.allowed_roles}. Your role: {current_user.role}"
            )
        return current_user

# Predefined role dependency checks
require_admin = RoleChecker(["Admin"])
require_qa_or_higher = RoleChecker(["Admin", "QA Engineer"])
require_developer_or_higher = RoleChecker(["Admin", "QA Engineer", "Developer"])
require_viewer_or_higher = RoleChecker(["Admin", "QA Engineer", "Developer", "Viewer"])
