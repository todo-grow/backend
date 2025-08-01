from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.task import Task

class ITaskRepository(ABC):
    @abstractmethod
    def create(self, task: Task) -> Task:
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def get_by_todo_id(self, todo_id: int) -> List[Task]:
        pass

    @abstractmethod
    def get_by_todo_id_and_user(self, todo_id: int, user_id: int) -> List[Task]:
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> None:
        pass
    
    @abstractmethod
    def get_subtasks_by_parent_id(self, parent_id: int) -> List[Task]:
        pass
    
    @abstractmethod
    def delete_with_descendants(self, task_id: int) -> None:
        """태스크와 모든 하위 태스크를 연쇄 삭제합니다."""
        pass
