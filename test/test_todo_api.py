from datetime import date


class TestTodoAPI:
    def test_get_all_todos_unauthorized(self, test_client, monkeypatch):
        """인증 없이 Todo 조회 시 401 에러"""
        monkeypatch.setenv("DISABLE_AUTH", "false")
        response = test_client.get("/api/todos")
        assert response.status_code == 401

    def test_get_all_todos_authorized(self, test_client):
        """인증된 사용자로 Todo 목록 조회"""
        response = test_client.get("/api/todos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_todo(self, test_client):
        """Todo 생성 테스트"""
        todo_data = {"base_date": date.today().isoformat()}
        response = test_client.post(
            "/api/todos", json=todo_data, headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["base_date"] == todo_data["base_date"]
        assert "tasks" in data

    def test_get_todo_by_id(self, test_client):
        """Todo ID로 조회 테스트"""
        # 먼저 Todo 생성
        todo_data = {"base_date": date.today().isoformat()}
        create_response = test_client.post("/api/todos", json=todo_data)
        todo_id = create_response.json()["id"]

        # ID로 조회
        response = test_client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id

    def test_get_todo_not_found(self, test_client):
        """존재하지 않는 Todo 조회 시 404"""
        response = test_client.get("/api/todos/99999")
        assert response.status_code == 404

    def test_get_todos_by_date(self, test_client):
        """날짜별 Todo 조회 테스트"""
        target_date = date.today()
        response = test_client.get(
            f"/api/todos?target_date={target_date.isoformat()}"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
