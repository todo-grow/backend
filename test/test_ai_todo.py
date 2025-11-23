class TestAITodoAPI:
    """AI를 활용한 TODO 생성 API 테스트"""

    def test_create_todo_with_ai(self, test_client):
        """AI로 TODO 생성 테스트"""
        # When: AI TODO 생성 요청
        request_data = {
            "user_input": "내일 회의 준비하고 보고서 작성해야 해",
            "base_date": "2025-12-25",
        }
        response = test_client.post("/api/todos/ai", json=request_data)

        # Then: TODO가 생성되고 Task들이 포함됨
        assert response.json() == {
            "base_date": "2025-12-25",
            "tasks": [
                {
                    "title": "회의 준비",
                    "points": 5,
                    "subtasks": [
                        {"title": "회의 자료 정리", "points": 3},
                        {"title": "발표 자료 작성", "points": 4},
                    ],
                },
                {"title": "보고서 작성", "points": 7, "subtasks": []},
            ],
        }

    def test_create_todo_with_ai_default_date(self, test_client):
        """AI TODO 생성 시 날짜 기본값 테스트"""
        # When: base_date 없이 요청
        request_data = {"user_input": "프로젝트 기획서 작성"}
        response = test_client.post("/api/todos/ai", json=request_data)

        # Then: 오늘 날짜로 생성됨
        assert response.json() == {
            "base_date": None,
            "tasks": [
                {
                    "title": "회의 준비",
                    "points": 5,
                    "subtasks": [
                        {"title": "회의 자료 정리", "points": 3},
                        {"title": "발표 자료 작성", "points": 4},
                    ],
                },
                {"title": "보고서 작성", "points": 7, "subtasks": []},
            ],
        }
