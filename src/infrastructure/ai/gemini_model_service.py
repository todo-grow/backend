import os
import json
from typing import Dict, Any
import google.generativeai as genai
from datetime import date

from src.infrastructure.ai.base_model_service import AIModelService


class GeminiModelService(AIModelService):
    """Google Gemini API를 사용하는 AI 모델 서비스"""

    def __init__(self, api_key: str = None):
        """
        GeminiModelService 초기화

        Args:
            api_key: Google Gemini API 키. 제공되지 않으면 환경 변수에서 로드
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')

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

        prompt = self._build_prompt(user_input, target_date)

        try:
            response = self.model.generate_content(prompt)

            # 응답 전체 구조 확인
            print(f"[DEBUG] Response object: {response}")
            print(f"[DEBUG] Response dir: {dir(response)}")

            # 응답 디버깅
            if not response:
                raise RuntimeError("Gemini 응답이 None입니다")

            # text 속성 확인
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text
                print(f"[DEBUG] Gemini 원본 응답: {response_text}")
            elif hasattr(response, 'candidates') and response.candidates:
                # candidates를 통해 접근
                response_text = response.candidates[0].content.parts[0].text
                print(f"[DEBUG] Gemini 원본 응답 (candidates): {response_text}")
            else:
                raise RuntimeError(f"응답에서 텍스트를 찾을 수 없습니다. Response 속성: {dir(response)}")

            if not response_text or response_text.strip() == "":
                raise RuntimeError("Gemini가 빈 응답을 반환했습니다")

            result = self._parse_response(response_text)
            return result
        except Exception as e:
            raise RuntimeError(f"Gemini API 호출 중 오류 발생: {str(e)}")

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Gemini 응답을 파싱합니다.

        Args:
            response_text: Gemini API 응답 텍스트

        Returns:
            파싱된 딕셔너리
        """
        try:
            # JSON 코드 블록에서 추출 (```json ... ``` 형식)
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            result = json.loads(response_text)

            # 데이터 검증
            if "tasks" not in result:
                raise ValueError("응답에 'tasks' 필드가 없습니다")

            for task in result["tasks"]:
                if "title" not in task or "points" not in task:
                    raise ValueError("태스크에 필수 필드가 없습니다")

                # points 범위 확인 및 조정
                task["points"] = max(1, min(10, int(task["points"])))

                # subtasks 검증
                if "subtasks" not in task:
                    task["subtasks"] = []

                for subtask in task["subtasks"]:
                    if "title" not in subtask or "points" not in subtask:
                        raise ValueError("서브태스크에 필수 필드가 없습니다")
                    subtask["points"] = max(1, min(10, int(subtask["points"])))

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {str(e)}")
        except Exception as e:
            raise ValueError(f"응답 파싱 오류: {str(e)}")