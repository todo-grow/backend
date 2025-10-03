import httpx
import os
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from datetime import datetime, timedelta
from src.domain.models.user import User
from src.domain.repositories.user_repository import UserRepository


# 기본값 상수
DEFAULT_NICKNAME = "오소리"
DEFAULT_PROFILE_IMAGE = (
    "https://gift-s.kakaocdn.net/dn/gift/images/m960/profile_default.png"
)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
        self._secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self._algorithm = "HS256"
        self._access_token_expire_minutes = 30

    async def get_kakao_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """카카오 액세스 토큰으로 사용자 정보 가져오기"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                "https://kapi.kakao.com/v2/user/me", headers=headers
            )

            if response.status_code == 200:
                return response.json()
            return None

    async def get_access_token_from_code(
        self, code: str, client_id: str, client_secret: str, redirect_uri: str
    ) -> Optional[str]:
        """카카오 인증 코드로 액세스 토큰 가져오기"""
        async with httpx.AsyncClient() as client:
            data = {
                "grant_type": "authorization_code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code": code,
                "client_secret": client_secret,
            }

            response = await client.post(
                "https://kauth.kakao.com/oauth/token", data=data
            )

            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            return None

    def get_or_create_user(self, kakao_user_info: Dict[str, Any]) -> User:
        """카카오 사용자 정보로 유저 조회 또는 생성"""
        kakao_id = str(kakao_user_info["id"])
        existing_user = self._user_repository.get_by_kakao_id(kakao_id)

        if existing_user:
            return existing_user

        # 새 사용자 생성
        properties = kakao_user_info.get("properties", {})
        kakao_account = kakao_user_info.get("kakao_account", {})

        # 프로필 정보 비동의 시 기본값 설정
        nickname = properties.get("nickname") or DEFAULT_NICKNAME
        profile_image = properties.get("profile_image") or DEFAULT_PROFILE_IMAGE

        new_user = User(
            kakao_id=kakao_id,
            nickname=nickname,
            profile_image=profile_image,
            email=kakao_account.get("email"),
        )

        return self._user_repository.create(new_user)

    def create_access_token(self, user: User) -> str:
        """JWT 액세스 토큰 생성"""
        expire = datetime.utcnow() + timedelta(
            minutes=self._access_token_expire_minutes
        )
        to_encode = {
            "sub": str(user.id),
            "kakao_id": user.kakao_id,
            "nickname": user.nickname,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError:
            return None

    async def unlink_kakao_account(self, kakao_id: str) -> bool:
        """카카오 계정 연결 해제 (Admin Key 사용)"""
        admin_key = os.getenv("KAKAO_ADMIN_KEY")
        if not admin_key:
            raise ValueError("KAKAO_ADMIN_KEY가 설정되지 않았습니다.")

        try:
            timeout = httpx.Timeout(connect=5.0, read=5.0, write=5.0, pool=5.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                headers = {"Authorization": f"KakaoAK {admin_key}"}
                data = {"target_id_type": "user_id", "target_id": kakao_id}
                response = await client.post(
                    "https://kapi.kakao.com/v1/user/unlink",
                    headers=headers,
                    data=data,
                )
                return response.status_code == 200
        except httpx.HTTPError:
            # 네트워크 오류/타임아웃 등은 연결 해제 실패로 간주하고 탈퇴 플로우는 계속 진행
            return False

    def delete_user(self, user_id: int) -> bool:
        """사용자 계정 삭제 (회원탈퇴)"""
        return self._user_repository.delete(user_id)
