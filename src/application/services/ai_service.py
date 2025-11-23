from typing import Dict, Any
from datetime import date

from src.infrastructure.ai.base_model_service import AIModelService


class AIService:
    """AI 모델을 사용하여 TODO 생성 기능을 제공하는 서비스"""

    def __init__(self, model_service: AIModelService):
        """
        AIService 초기화

        Args:
            model_service: 사용할 AI 모델 서비스 (GeminiModelService, ClaudeModelService 등)
        """
        self.model_service = model_service

    def generate_todos_from_text(self, user_input: str, target_date: date = None) -> Dict[str, Any]:
        """
        자연어 입력을 받아 TODO 목록을 생성합니다.

        Args:
            user_input: 사용자의 자연어 입력
            target_date: TODO의 기준 날짜 (없으면 오늘)

        Returns:
            생성된 TODO와 Task 목록을 담은 딕셔너리
        """
        if target_date is None:
            target_date = date.today()

        result = self.model_service.generate_todos_from_text(user_input, target_date)
        result["base_date"] = target_date.isoformat()
        return result