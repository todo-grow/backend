from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Task:
    id: Optional[int]
    title: str
    points: int
    todo_id: int
    user_id: Optional[int] = None
    completed: bool = False
    parent_id: Optional[int] = None
    subtasks: List['Task'] = field(default_factory=list)

    def update_title(self, title: str) -> None:
        """태스크 제목을 수정합니다."""
        if not title.strip():
            raise ValueError("제목은 비어있을 수 없습니다.")
        self.title = title.strip()


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
    
    def is_subtask(self) -> bool:
        """서브태스크인지 확인합니다."""
        return self.parent_id is not None
    
    def is_parent_task(self) -> bool:
        """부모 태스크인지 확인합니다."""
        return self.parent_id is None
    
    def get_all_descendant_ids(self) -> List[int]:
        """현재 태스크의 모든 하위 태스크 ID를 재귀적으로 반환합니다."""
        descendant_ids = []
        
        for subtask in self.subtasks:
            if subtask.id:
                descendant_ids.append(subtask.id)
                descendant_ids.extend(subtask.get_all_descendant_ids())
        
        return descendant_ids
