from datetime import date


class TestBulkTodoAPI:
    """Bulk TODO 생성 API 테스트"""

    def test_create_bulk_todo_with_simple_tasks(self, test_client):
        """간단한 Task들을 한번에 생성"""
        # Given
        request_data = {
            "base_date": "2025-12-25",
            "tasks": [
                {"title": "회의 준비", "points": 5, "completed": False},
                {"title": "보고서 작성", "points": 7, "completed": False},
                {"title": "이메일 확인", "points": 2, "completed": False},
            ],
        }

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        assert response.json() == {
            "id": 1,
            "base_date": "2025-12-25",
            "tasks": [
                {
                    "id": 1,
                    "title": "회의 준비",
                    "points": 5,
                    "todo_id": 1,
                    "completed": False,
                    "subtasks": [],
                },
                {
                    "id": 2,
                    "title": "보고서 작성",
                    "points": 7,
                    "todo_id": 1,
                    "completed": False,
                    "subtasks": [],
                },
                {
                    "id": 3,
                    "title": "이메일 확인",
                    "points": 2,
                    "todo_id": 1,
                    "completed": False,
                    "subtasks": [],
                },
            ],
        }

    def test_create_bulk_todo_with_parent_child(self, test_client):
        """부모-자식 관계가 있는 Task 생성"""
        # Given
        request_data = {
            "base_date": "2025-12-25",
            "tasks": [
                {"title": "프로젝트 기획", "points": 8, "completed": False},
                {"title": "시장 조사", "points": 5, "completed": False, "parent_id": 0},
                {
                    "title": "경쟁사 분석",
                    "points": 4,
                    "completed": False,
                    "parent_id": 0,
                },
                {"title": "보고서 작성", "points": 6, "completed": False},
                {"title": "초안 작성", "points": 3, "completed": False, "parent_id": 3},
            ],
        }

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        assert response.json() == {
            "id": 1,
            "base_date": "2025-12-25",
            "tasks": [
                {
                    "id": 1,
                    "title": "프로젝트 기획",
                    "points": 8,
                    "todo_id": 1,
                    "completed": False,
                    "subtasks": [
                        {
                            "id": 2,
                            "title": "시장 조사",
                            "points": 5,
                            "todo_id": 1,
                            "completed": False,
                        },
                        {
                            "id": 3,
                            "title": "경쟁사 분석",
                            "points": 4,
                            "todo_id": 1,
                            "completed": False,
                        },
                    ],
                },
                {
                    "id": 4,
                    "title": "보고서 작성",
                    "points": 6,
                    "todo_id": 1,
                    "completed": False,
                    "subtasks": [
                        {
                            "id": 5,
                            "title": "초안 작성",
                            "points": 3,
                            "todo_id": 1,
                            "completed": False,
                        }
                    ],
                },
            ],
        }

    def test_create_bulk_todo_without_date(self, test_client):
        """날짜 없이 Bulk TODO 생성"""
        # Given
        request_data = {
            "tasks": [
                {"title": "긴급 업무", "points": 10, "completed": False},
            ]
        }

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        print(response.json())

    def test_create_bulk_todo_with_completed_tasks(self, test_client):
        """완료된 Task 포함하여 생성"""
        # Given
        request_data = {
            "base_date": "2025-12-25",
            "tasks": [
                {"title": "이미 완료한 작업", "points": 3, "completed": True},
                {"title": "진행 중인 작업", "points": 5, "completed": False},
            ],
        }

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        print(response.json())

    def test_create_bulk_todo_invalid_parent_id(self, test_client):
        """잘못된 parent_id로 생성 시 에러"""
        # Given: parent_id가 범위를 벗어남
        request_data = {
            "base_date": "2025-12-25",
            "tasks": [
                {"title": "부모 태스크", "points": 5, "completed": False},
                {
                    "title": "자식 태스크",
                    "points": 3,
                    "completed": False,
                    "parent_id": 10,
                },  # 잘못된 ID
            ],
        }

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        print(response.json())

    def test_create_bulk_todo_unauthorized(self, test_client):
        """인증 없이 Bulk TODO 생성 시 401 에러"""
        # Given: 인증되지 않은 클라이언트

        # When
        request_data = {"tasks": [{"title": "작업", "points": 5, "completed": False}]}
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        print(response.json())

    def test_create_bulk_todo_empty_tasks(self, test_client):
        """빈 tasks 배열로 생성"""
        # Given
        request_data = {"base_date": "2025-12-25", "tasks": []}

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then: TODO는 생성되지만 Task가 없음
        print(response.json())

    def test_create_bulk_todo_complex_hierarchy(self, test_client):
        """복잡한 계층 구조 생성"""
        # Given: 여러 부모에 여러 자식
        request_data = {
            "base_date": "2025-12-25",
            "tasks": [
                {"title": "백엔드 개발", "points": 10, "completed": False},
                {"title": "API 설계", "points": 5, "completed": False, "parent_id": 0},
                {
                    "title": "데이터베이스 설계",
                    "points": 6,
                    "completed": False,
                    "parent_id": 0,
                },
                {"title": "프론트엔드 개발", "points": 10, "completed": False},
                {"title": "UI 디자인", "points": 4, "completed": False, "parent_id": 3},
                {
                    "title": "컴포넌트 개발",
                    "points": 7,
                    "completed": False,
                    "parent_id": 3,
                },
                {"title": "테스트", "points": 8, "completed": False},
            ],
        }

        # When
        response = test_client.post("/api/todos/bulk", json=request_data)

        # Then
        print(response.json())
