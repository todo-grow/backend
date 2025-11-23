import os
from typing import Any, Dict, Optional

import httpx

from src.application.services.social_auth_provider import SocialAuthProvider


class KakaoAuthProvider(SocialAuthProvider):
    """Kakao-specific implementation of the social auth provider interface."""

    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers=headers,
            )

            if response.status_code == 200:
                return response.json()
            return None

    async def get_access_token_from_code(
        self, code: str, client_id: str, client_secret: str, redirect_uri: str
    ) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code": code,
                "client_secret": client_secret,
            }

            response = await client.post(
                "https://kauth.kakao.com/oauth/token",
                data=data,
            )

            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            return None

    async def unlink_account(self, provider_user_id: str) -> bool:
        admin_key = os.getenv("KAKAO_ADMIN_KEY")
        if not admin_key:
            raise ValueError("KAKAO_ADMIN_KEY가 설정되지 않았습니다.")

        try:
            timeout = httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                headers = {"Authorization": f"KakaoAK {admin_key}"}
                data = {"target_id_type": "user_id", "target_id": provider_user_id}
                response = await client.post(
                    "https://kapi.kakao.com/v1/user/unlink",
                    headers=headers,
                    data=data,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            # Treat network errors as unlink failures but allow higher-level flow to continue.
            return False
