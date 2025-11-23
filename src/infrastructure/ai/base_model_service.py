from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import date


class AIModelService(ABC):
    """AI 모델 서비스의 추상 베이스 클래스"""

    @abstractmethod
    def generate_todos_from_text(self, user_input: str, target_date: date = None) -> Dict[str, Any]:
        """
        자연어 입력을 받아 TODO 목록을 생성합니다.

        Args:
            user_input: 사용자의 자연어 입력
            target_date: TODO의 기준 날짜 (없으면 오늘)

        Returns:
            생성된 TODO와 Task 목록을 담은 딕셔너리
            {
                "tasks": [
                    {
                        "title": str,
                        "points": int,
                        "subtasks": [{"title": str, "points": int}, ...]
                    },
                    ...
                ]
            }
        """
        pass

    def _build_prompt(self, user_input: str, target_date: date) -> str:
        """AI 프롬프트를 생성합니다."""
        return f"""당신은 TODO 목록을 생성하는 AI 어시스턴트입니다.

사용자의 자연어 입력을 분석하여 구조화된 TODO 목록을 생성해주세요.

입력: {user_input}
날짜: {target_date.isoformat()}

다음 JSON 형식으로 응답해주세요:
{{
  "tasks": [
    {{
      "title": "태스크 제목",
      "points": 포인트 (1-10 사이의 정수, 태스크의 중요도나 난이도를 나타냄),
      "subtasks": [
        {{
          "title": "서브태스크 제목",
          "points": 포인트
        }}
      ]
    }}
  ]
}}

규칙:
1. 사용자의 입력에서 실행 가능한 태스크들을 추출하세요
2. 태스크는 구체적이고 실행 가능해야 합니다
3. points는 1-10 사이의 정수입니다 (1=매우 쉬움, 10=매우 어려움)
4. 큰 태스크는 여러 개의 서브태스크로 나눌 수 있습니다
5. subtasks 배열은 선택사항입니다 (없으면 빈 배열)
6. JSON 형식만 응답하고 다른 설명은 포함하지 마세요
7. 태스크가 명확하지 않으면 합리적인 해석을 제공하세요

예시 입력: "내일 회의 준비하고 보고서 작성해야 해"
예시 출력:
{{
  "tasks": [
    {{
      "title": "회의 준비",
      "points": 5,
      "subtasks": [
        {{"title": "회의 자료 정리", "points": 3}},
        {{"title": "발표 자료 작성", "points": 4}}
      ]
    }},
    {{
      "title": "보고서 작성",
      "points": 7,
      "subtasks": []
    }}
  ]
}}
"""