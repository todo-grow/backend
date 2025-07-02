from fastapi.testclient import TestClient
from src.main import app

class TestTodoAPI:
    def setup_method(self):
        self.client = TestClient(app)

    def test_create_todo(self):
        response = self.client.post("/todos?title=Test Todo")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Todo"
        assert data["completed"] is False

    def test_get_all_todos(self):
        response = self.client.get("/todos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_todo_by_id(self):
        response = self.client.post("/todos?title=Test Todo")
        todo_id = response.json()["id"]
        response = self.client.get(f"/todos/{todo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id

    def test_update_todo(self):
        response = self.client.post("/todos?title=Test Todo")
        todo_id = response.json()["id"]
        response = self.client.put(f"/todos/{todo_id}?title=Updated Todo&completed=true")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Todo"
        assert data["completed"] is True

    def test_delete_todo(self):
        response = self.client.post("/todos?title=Test Todo")
        todo_id = response.json()["id"]
        response = self.client.delete(f"/todos/{todo_id}")
        assert response.status_code == 200
        response = self.client.get(f"/todos/{todo_id}")
        assert response.status_code == 404
