import datetime
import bcrypt
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from app.core.config import settings
from app.domain.auth_interface import IAuthenticationProvider

ALGORITHM = "HS256"

class AuthenticationProvider(IAuthenticationProvider):
    """
    Production-grade implementation of IAuthenticationProvider.
    Uses direct BCrypt library hashing to ensure compatibility across all Python versions.
    """
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            return False

    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: Optional[int] = None) -> str:
        to_encode = data.copy()
        if expires_delta_minutes:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta_minutes)
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any], expires_delta_days: Optional[int] = None) -> str:
        to_encode = data.copy()
        if expires_delta_days:
            expire = datetime.datetime.utcnow() + datetime.timedelta(days=expires_delta_days)
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str, is_refresh: bool = False) -> Dict[str, Any]:
        """
        Validates, decodes and returns the payload of the JWT token.
        Raises JWTError if invalid signature/expired.
        """
        secret = settings.REFRESH_SECRET_KEY if is_refresh else settings.SECRET_KEY
        try:
            payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
            # Extra safety check on token purpose
            expected_type = "refresh" if is_refresh else "access"
            if payload.get("type") != expected_type:
                raise JWTError("Token type mismatch")
            return payload
        except JWTError as e:
            raise ValueError(f"Invalid or expired credentials: {str(e)}")

# Singleton instance
auth_provider = AuthenticationProvider()
