import pytest
from fastapi.testclient import TestClient
from datetime import date
from src.main import app
from src.domain.models.user import User
from src.presentation.api.auth import get_current_user


@pytest.fixture
def mock_user():
    """테스트용 가짜 사용자"""
    return User(
        id=1,
        kakao_id="test123",
        nickname="테스트유저",
        profile_image="https://test.com/profile.jpg",
        email="test@example.com",
    )


@pytest.fixture
def authenticated_client(mock_user, in_memory_sqlite_db):
    """인증된 테스트 클라이언트"""

    def mock_get_current_user():
        return mock_user

    # FastAPI dependency override 사용
    app.dependency_overrides[get_current_user] = mock_get_current_user

    # 테스트용 데이터베이스로 오버라이드
    from src.database import Database

    test_database = Database(in_memory_sqlite_db)

    from src.containers import Container

    container = Container()
    container.database.override(test_database)

    client = TestClient(app)
    yield client

    # 테스트 후 원복
    app.dependency_overrides.clear()
    container.unwire()


class TestTodoAPI:
    def test_get_all_todos_unauthorized(self):
        """인증 없이 Todo 조회 시 403 에러"""
        client = TestClient(app)
        response = client.get("/api/todos")
        assert response.status_code == 403

    def test_get_all_todos_authorized(self, authenticated_client):
        """인증된 사용자로 Todo 목록 조회"""
        response = authenticated_client.get("/api/todos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_todo(self, authenticated_client):
        """Todo 생성 테스트"""
        todo_data = {"base_date": date.today().isoformat()}
        response = authenticated_client.post(
            "/api/todos", json=todo_data, headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["base_date"] == todo_data["base_date"]
        assert "tasks" in data

    def test_get_todo_by_id(self, authenticated_client):
        """Todo ID로 조회 테스트"""
        # 먼저 Todo 생성
        todo_data = {"base_date": date.today().isoformat()}
        create_response = authenticated_client.post("/api/todos", json=todo_data)
        todo_id = create_response.json()["id"]

        # ID로 조회
        response = authenticated_client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id

    def test_get_todo_not_found(self, authenticated_client):
        """존재하지 않는 Todo 조회 시 404"""
        response = authenticated_client.get("/api/todos/99999")
        assert response.status_code == 404

    def test_get_todos_by_date(self, authenticated_client):
        """날짜별 Todo 조회 테스트"""
        target_date = date.today()
        response = authenticated_client.get(
            f"/api/todos?target_date={target_date.isoformat()}"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
