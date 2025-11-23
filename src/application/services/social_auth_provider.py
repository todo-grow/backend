from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class SocialAuthProvider(ABC):
    """Interface for social authentication providers (Kakao, Google, Naver, etc.)."""

    @abstractmethod
    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile data using a provider-issued access token."""

    @abstractmethod
    async def get_access_token_from_code(
        self, code: str, client_id: str, client_secret: str, redirect_uri: str
    ) -> Optional[str]:
        """Exchange an authorization code for an access token."""

    @abstractmethod
    async def unlink_account(self, provider_user_id: str) -> bool:
        """Unlink or disconnect a provider account."""
