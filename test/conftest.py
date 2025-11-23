import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.application.services.ai_service import AIService
from src.application.services.social_auth_provider import SocialAuthProvider
from src.database import Database
from src.infrastructure.database.sqlalchemy_models import Base
from src.main import app, container
from test.fake_ai_model_service import FakeAIModelService


class TestSocialAuthProvider(SocialAuthProvider):
    """Fake social auth provider used during testing to avoid external calls."""

    async def get_user_info(self, access_token: str):
        return {
            "id": "test_provider_user_id",
            "properties": {
                "nickname": "테스트유저",
                "profile_image": "https://example.com/test-profile.jpg",
            },
            "kakao_account": {
                "email": "test@example.com",
            },
        }

    async def get_access_token_from_code(
        self, code: str, client_id: str, client_secret: str, redirect_uri: str
    ):
        return "test_access_token"

    async def unlink_account(self, provider_user_id: str) -> bool:
        return True


@pytest.fixture
def test_social_auth_provider():
    return TestSocialAuthProvider()


@pytest.fixture(scope="function")
def in_memory_sqlite_db():
    """SQLite 인메모리 데이터베이스 생성"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def session_factory(in_memory_sqlite_db):
    """세션 팩토리 생성"""
    yield sessionmaker(bind=in_memory_sqlite_db)


@pytest.fixture(scope="function")
def db_session(session_factory):
    """데이터베이스 세션 fixture"""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def app_container(in_memory_sqlite_db, test_social_auth_provider):
    """애플리케이션 컨테이너를 테스트용 데이터베이스로 오버라이드"""
    container = app.container
    test_database = Database(in_memory_sqlite_db)

    container.db_engine.override(providers.Object(in_memory_sqlite_db))
    container.database.override(providers.Object(test_database))
    container.kakao_auth_provider.override(providers.Object(test_social_auth_provider))

    try:
        yield container
    finally:
        container.db_engine.reset_override()
        container.database.reset_override()
        container.kakao_auth_provider.reset_override()


@pytest.fixture(scope="function")
def test_client(app_container):
    """FastAPI 테스트 클라이언트"""
    # AI 서비스를 Fake로 오버라이드
    fake_model_service = FakeAIModelService()
    fake_ai_service = AIService(model_service=fake_model_service)
    container.ai_service.override(providers.Object(fake_ai_service))
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(autouse=True)
def enable_dev_auth(monkeypatch):
    monkeypatch.setenv("DISABLE_AUTH", "true")
    monkeypatch.setenv("DEV_USER_ID", "9999999")
    monkeypatch.setenv("DEV_KAKAO_ID", "dev_kakao_id")
    monkeypatch.setenv("DEV_NICKNAME", "개발자")
