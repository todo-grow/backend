import pytest
from src.application.services.auth_service import AuthService, DEFAULT_NICKNAME, DEFAULT_PROFILE_IMAGE
from src.application.services.social_auth_provider import SocialAuthProvider
from src.infrastructure.database.sqlalchemy_user_repository import SqlAlchemyUserRepository
from .fixtures import KakaoUserInfoFixture, UserFixture


class DummySocialAuthProvider(SocialAuthProvider):
    async def get_user_info(self, access_token: str):
        return None

    async def get_access_token_from_code(
        self, code: str, client_id: str, client_secret: str, redirect_uri: str
    ):
        return None

    async def unlink_account(self, provider_user_id: str) -> bool:
        return True


class TestAuthService:
    @pytest.fixture
    def auth_service(self, session_factory):
        """AuthService 인스턴스 생성"""
        user_repository = SqlAlchemyUserRepository(session_factory)
        return AuthService(user_repository, DummySocialAuthProvider())

    def test_get_or_create_user_with_full_profile_info(self, auth_service):
        """프로필 정보가 모두 제공된 경우 테스트"""
        kakao_user_info = KakaoUserInfoFixture.fixture_kakao_user_info(
            user_id=12345,
            nickname="카카오유저",
            profile_image="https://profile.kakao.com/user.jpg",
            email="user@example.com"
        )

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.kakao_id == "12345"
        assert result.nickname == "카카오유저"
        assert result.profile_image == "https://profile.kakao.com/user.jpg"
        assert result.email == "user@example.com"

    def test_get_or_create_user_with_no_profile_info(self, auth_service):
        """프로필 정보가 전혀 제공되지 않은 경우 테스트 (비동의)"""
        kakao_user_info = KakaoUserInfoFixture.fixture_kakao_user_info_no_profile_consent(
            user_id=12346,
            email="user2@example.com"
        )

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.kakao_id == "12346"
        assert result.nickname == DEFAULT_NICKNAME
        assert result.profile_image == DEFAULT_PROFILE_IMAGE
        assert result.email == "user2@example.com"

    def test_get_or_create_user_with_partial_profile_info(self, auth_service):
        """일부 프로필 정보만 제공된 경우 테스트"""
        kakao_user_info = KakaoUserInfoFixture.fixture_kakao_user_info_partial_consent(
            user_id=12347,
            nickname="부분동의유저",
            email="partial@example.com"
        )

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.kakao_id == "12347"
        assert result.nickname == "부분동의유저"
        assert result.profile_image == DEFAULT_PROFILE_IMAGE
        assert result.email == "partial@example.com"

    def test_get_or_create_user_with_none_values(self, auth_service):
        """프로필 정보가 None으로 제공된 경우 테스트"""
        kakao_user_info = KakaoUserInfoFixture.fixture_kakao_user_info(
            user_id=12348,
            nickname=None,
            profile_image=None,
            email="none@example.com"
        )

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.kakao_id == "12348"
        assert result.nickname == DEFAULT_NICKNAME
        assert result.profile_image == DEFAULT_PROFILE_IMAGE
        assert result.email == "none@example.com"

    def test_get_or_create_user_missing_properties_key(self, auth_service):
        """properties 키가 아예 없는 경우 테스트"""
        kakao_user_info = {
            "id": 12349,
            "kakao_account": {
                "email": "no_properties@example.com"
            }
        }

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.kakao_id == "12349"
        assert result.nickname == DEFAULT_NICKNAME
        assert result.profile_image == DEFAULT_PROFILE_IMAGE
        assert result.email == "no_properties@example.com"

    def test_get_or_create_existing_user(self, auth_service, db_session):
        """기존 사용자가 있는 경우 테스트"""
        from .fixtures import UserFixture
        
        existing_user_orm = UserFixture.create_user_orm(
            session=db_session,
            kakao_id="existing123",
            nickname="기존유저",
            profile_image="https://existing.com/profile.jpg"
        )

        kakao_user_info = KakaoUserInfoFixture.fixture_kakao_user_info(
            user_id=int(existing_user_orm.kakao_id.replace("existing", "")),
            nickname="새로운닉네임",
            profile_image="https://new.com/profile.jpg",
        )
        kakao_user_info["id"] = "existing123"

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.id == existing_user_orm.id
        assert result.kakao_id == "existing123"
        assert result.nickname == "기존유저"
        assert result.profile_image == "https://existing.com/profile.jpg"

    def test_get_or_create_user_empty_string_values(self, auth_service):
        """빈 문자열이 제공된 경우 테스트 (기본값으로 대체되어야 함)"""
        kakao_user_info = KakaoUserInfoFixture.fixture_kakao_user_info(
            user_id=12350,
            nickname="",
            profile_image="",
            email="empty@example.com"
        )

        result = auth_service.get_or_create_user(kakao_user_info)

        assert result.kakao_id == "12350"
        assert result.nickname == DEFAULT_NICKNAME
        assert result.profile_image == DEFAULT_PROFILE_IMAGE
        assert result.email == "empty@example.com"
