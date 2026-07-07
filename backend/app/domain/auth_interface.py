from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class IAuthenticationProvider(ABC):
    """
    Decoupled interface representing the Authentication/Authorization service.
    Allows easy plug-and-play switching to standard SSO providers
    (such as OIDC/SAML, Google Workspace, Okta, Microsoft Entra ID) in the future.
    """
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a plain text password securely."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password matching."""
        pass

    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: Optional[int] = None) -> str:
        """Generate JWT Access Token containing user metadata and role permissions."""
        pass

    @abstractmethod
    def create_refresh_token(self, data: Dict[str, Any], expires_delta_days: Optional[int] = None) -> str:
        """Generate long-lived rotation-enabled Refresh Token."""
        pass

    @abstractmethod
    def decode_token(self, token: str, is_refresh: bool = False) -> Dict[str, Any]:
        """Decode and validate access/refresh tokens. Raises invalid credentials exceptions if invalid."""
        pass
