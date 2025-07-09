from typing import List, Optional

from src.domain.models.task import Task
from src.domain.repositories.task_repository import ITaskRepository


class TaskService:
    def __init__(self, task_repository: ITaskRepository):
        self.task_repository = task_repository

    def create_task(self, task: Task) -> Task:
        return self.task_repository.create(task)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return self.task_repository.get_by_id(task_id)

    def get_tasks_by_todo_id(self, todo_id: int) -> List[Task]:
        return self.task_repository.get_by_todo_id(todo_id)

    def update_task(
        self, task_id: int, title: Optional[str] = None, description: Optional[str] = None, points: Optional[int] = None, completed: Optional[bool] = None
    ) -> Task:
        """태스크의 기본 정보를 전체 수정합니다."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        if title is not None:
            task.update_title(title)
        if description is not None:
            task.update_description(description)
        if points is not None:
            task.update_points(points)
        if completed is not None:
            task.completed = completed

        return self.task_repository.update(task)

    def toggle_task_completion(self, task_id: int) -> Task:
        """태스크의 완료 상태를 토글합니다."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        task.toggle_completion()
        return self.task_repository.update(task)

    def delete_task(self, task_id: int) -> None:
        self.task_repository.delete(task_id)
