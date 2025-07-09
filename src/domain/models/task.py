from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    id: Optional[int]
    title: str
    description: Optional[str]
    points: int
    todo_id: int
    completed: bool = False

    def update_title(self, title: str) -> None:
        """태스크 제목을 수정합니다."""
        if not title.strip():
            raise ValueError("제목은 비어있을 수 없습니다.")
        self.title = title.strip()

    def update_description(self, description: Optional[str]) -> None:
        """태스크 설명을 수정합니다."""
        self.description = description.strip() if description else None

    def update_points(self, points: int) -> None:
        """태스크 포인트를 수정합니다."""
        if points < 0:
            raise ValueError("포인트는 0 이상이어야 합니다.")
        self.points = points

    def toggle_completion(self) -> None:
        """태스크의 완료 상태를 토글합니다."""
        self.completed = not self.completed

    def is_completed(self) -> bool:
        """태스크가 완료되었는지 확인합니다."""
        return self.completed
