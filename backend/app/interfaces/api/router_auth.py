import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.infrastructure.database import get_db
from app.domain.models import User, RefreshToken
from app.infrastructure.auth_provider import auth_provider

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "Viewer" # Admin, QA Engineer, Developer, Viewer

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user inside the local DB."""
    # Check if user already exists
    stmt = select(User).filter((User.username == user_in.username) | (User.email == user_in.email))
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email already registered"
        )
    
    hashed_pwd = auth_provider.hash_password(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
        role=user_in.role
    )
    db.add(user)
    await db.flush()
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authenticate credentials and return tokens."""
    stmt = select(User).filter(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not auth_provider.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Generate tokens
    user_data = {"sub": user.username, "role": user.role}
    access_token = auth_provider.create_access_token(user_data)
    refresh_token = auth_provider.create_refresh_token(user_data)
    
    # Store refresh token
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    db_refresh = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(db_refresh)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": user.role
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_in: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    """Rotate Access and Refresh Tokens."""
    try:
        payload = auth_provider.decode_token(refresh_in.refresh_token, is_refresh=True)
        username = payload.get("sub")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    # Check if token exists in DB and is active
    stmt = select(RefreshToken).filter(RefreshToken.token == refresh_in.refresh_token, RefreshToken.revoked == False)
    result = await db.execute(stmt)
    db_refresh = result.scalars().first()
    if not db_refresh or db_refresh.expires_at < datetime.datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")
        
    # Fetch User
    stmt_user = select(User).filter(User.id == db_refresh.user_id)
    res_user = await db.execute(stmt_user)
    user = res_user.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive")
        
    # Rotate refresh tokens
    user_data = {"sub": user.username, "role": user.role}
    new_access = auth_provider.create_access_token(user_data)
    new_refresh = auth_provider.create_refresh_token(user_data)
    
    # Revoke old token
    db_refresh.revoked = True
    
    # Add new refresh token
    new_expires = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    new_db_refresh = RefreshToken(
        token=new_refresh,
        user_id=user.id,
        expires_at=new_expires
    )
    db.add(new_db_refresh)
    
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "role": user.role
    }

@router.post("/logout")
async def logout(refresh_in: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke refresh token to log out user."""
    stmt = select(RefreshToken).filter(RefreshToken.token == refresh_in.refresh_token)
    result = await db.execute(stmt)
    db_refresh = result.scalars().first()
    if db_refresh:
        db_refresh.revoked = True
    return {"message": "Successfully logged out"}
