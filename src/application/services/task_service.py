from typing import List, Optional

from src.domain.models.task import Task
from src.domain.repositories.task_repository import ITaskRepository


class TaskService:
    def __init__(self, task_repository: ITaskRepository):
        self.task_repository = task_repository

    def create_task(self, task: Task) -> Task:
        # 서브태스크가 또 다른 서브태스크를 가지는 것을 방지
        if task.parent_id is not None:
            parent_task = self.task_repository.get_by_id(task.parent_id)
            if parent_task and parent_task.parent_id is not None:
                raise ValueError("서브태스크는 또 다른 서브태스크를 가질 수 없습니다.")
        
        return self.task_repository.create(task)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return self.task_repository.get_by_id(task_id)

    def get_tasks_by_todo_id(self, todo_id: int) -> List[Task]:
        return self.task_repository.get_by_todo_id(todo_id)
    
    def get_task_with_subtasks(self, task_id: int) -> Optional[Task]:
        task = self.task_repository.get_by_id(task_id)
        if task:
            task.subtasks = self.task_repository.get_subtasks_by_parent_id(task_id)
        return task
    
    def get_tasks_with_subtasks_by_todo_id(self, todo_id: int) -> List[Task]:
        tasks = self.task_repository.get_by_todo_id(todo_id)
        # 부모 태스크만 필터링 (parent_id가 None인 것들)
        parent_tasks = [task for task in tasks if task.parent_id is None]
        
        # 각 부모 태스크에 subtask들을 추가
        for task in parent_tasks:
            task.subtasks = self.task_repository.get_subtasks_by_parent_id(task.id)
        
        return parent_tasks

    def update_task(
        self, task_id: int, title: Optional[str] = None, points: Optional[int] = None, completed: Optional[bool] = None, parent_id: Optional[int] = None
    ) -> Task:
        """태스크의 기본 정보를 전체 수정합니다."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        # parent_id 변경 시 서브태스크 depth 검증
        if parent_id is not None and parent_id != task.parent_id:
            parent_task = self.task_repository.get_by_id(parent_id)
            if parent_task and parent_task.parent_id is not None:
                raise ValueError("서브태스크는 또 다른 서브태스크를 가질 수 없습니다.")

        if title is not None:
            task.update_title(title)
        if points is not None:
            task.update_points(points)
        if completed is not None:
            task.completed = completed
        if parent_id is not None:
            task.parent_id = parent_id

        return self.task_repository.update(task)

    def toggle_task_completion(self, task_id: int) -> Task:
        """태스크의 완료 상태를 토글합니다."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        task.toggle_completion()
        return self.task_repository.update(task)

    def delete_task(self, task_id: int) -> None:
        """태스크와 모든 하위 태스크를 연쇄 삭제합니다."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")
        
        self.task_repository.delete_with_descendants(task_id)
