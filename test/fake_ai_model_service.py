from typing import Dict, Any
from datetime import date

from src.infrastructure.ai.base_model_service import AIModelService


class FakeAIModelService(AIModelService):
    """테스트용 Fake AI 모델 서비스"""

    def __init__(self, mock_response: Dict[str, Any] = None):
        """
        Args:
            mock_response: 반환할 응답 (없으면 기본값 사용)
        """
        self.mock_response = mock_response or {
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
            ]
        }
        self.last_input = None
        self.last_target_date = None

    def generate_todos_from_text(self, user_input: str, target_date: date = None) -> Dict[str, Any]:
        """테스트용 응답 반환"""
        self.last_input = user_input
        self.last_target_date = target_date or date.today()
        return self.mock_response