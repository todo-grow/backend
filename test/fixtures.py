from datetime import datetime
from typing import Optional
from src.domain.models.user import User
from src.infrastructure.database.sqlalchemy_models import UserORM
import random
import string


def rand_str(length: int = 8) -> str:
    """랜덤 문자열 생성"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class UserFixture:
    @staticmethod
    def fixture_user(
        id: Optional[int] = None,
        kakao_id: Optional[str] = None,
        email: Optional[str] = None,
        nickname: Optional[str] = None,
        profile_image: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> User:
        """테스트용 User 엔티티 생성"""
        return User(
            id=id,
            kakao_id=kakao_id or rand_str(),
            email=email or f"{rand_str()}@example.com",
            nickname=nickname or f"테스트유저_{rand_str()}",
            profile_image=profile_image or f"https://example.com/profile_{rand_str()}.jpg",
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
        )

    @staticmethod
    def create_user_orm(
        session,
        id: Optional[int] = None,
        kakao_id: Optional[str] = None,
        email: Optional[str] = None,
        nickname: Optional[str] = None,
        profile_image: Optional[str] = None,
    ) -> UserORM:
        """테스트용 UserORM 생성 및 DB 저장"""
        user_orm = UserORM(
            id=id,
            kakao_id=kakao_id or rand_str(),
            email=email or f"{rand_str()}@example.com",
            nickname=nickname or f"테스트유저_{rand_str()}",
            profile_image=profile_image or f"https://example.com/profile_{rand_str()}.jpg",
        )
        session.add(user_orm)
        session.commit()
        session.refresh(user_orm)
        return user_orm


class KakaoUserInfoFixture:
    @staticmethod
    def fixture_kakao_user_info(
        user_id: int = 12345,
        nickname: Optional[str] = "카카오유저",
        profile_image: Optional[str] = "https://profile.kakao.com/user.jpg",
        email: Optional[str] = "user@example.com",
        include_properties: bool = True,
        include_kakao_account: bool = True,
    ) -> dict:
        """테스트용 카카오 사용자 정보 응답 생성"""
        kakao_info = {
            "id": user_id
        }
        
        if include_properties:
            properties = {}
            if nickname is not None:
                properties["nickname"] = nickname
            if profile_image is not None:
                properties["profile_image"] = profile_image
            kakao_info["properties"] = properties
        
        if include_kakao_account:
            kakao_account = {}
            if email is not None:
                kakao_account["email"] = email
            kakao_info["kakao_account"] = kakao_account
        
        return kakao_info

    @staticmethod
    def fixture_kakao_user_info_no_profile_consent(
        user_id: int = 12345,
        email: Optional[str] = "user@example.com",
    ) -> dict:
        """프로필 정보 비동의 상황의 카카오 사용자 정보"""
        return {
            "id": user_id,
            "properties": {},
            "kakao_account": {
                "email": email,
                "profile_needs_agreement": True,
                "profile_nickname_needs_agreement": True,
                "profile_image_needs_agreement": True,
            }
        }

    @staticmethod
    def fixture_kakao_user_info_partial_consent(
        user_id: int = 12345,
        nickname: Optional[str] = "카카오유저",
        email: Optional[str] = "user@example.com",
    ) -> dict:
        """일부 프로필 정보만 동의한 상황"""
        return {
            "id": user_id,
            "properties": {
                "nickname": nickname,
            },
            "kakao_account": {
                "email": email,
                "profile_image_needs_agreement": True,
            }
        }