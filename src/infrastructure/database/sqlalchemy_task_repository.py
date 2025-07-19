from typing import List, Optional

from src.domain.models.task import Task
from src.domain.repositories.task_repository import ITaskRepository
from src.infrastructure.database.sqlalchemy_models import TaskORM


class SQLAlchemyTaskRepository(ITaskRepository):
    def __init__(self, session_factory):
        self.__session_factory = session_factory

    def create(self, task: Task) -> Task:
        with self.__session_factory() as session:
            task_orm = TaskORM(
                title=task.title,
                points=task.points,
                todo_id=task.todo_id,
                completed=task.completed,
                parent_id=task.parent_id,
            )
            session.add(task_orm)
            session.commit()
            session.refresh(task_orm)
            return self._to_domain_task(task_orm)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        with self.__session_factory() as session:
            task_orm = session.query(TaskORM).filter(TaskORM.id == task_id).first()
            if task_orm:
                return self._to_domain_task(task_orm)
            return None

    def get_by_todo_id(self, todo_id: int) -> List[Task]:
        with self.__session_factory() as session:
            task_orms = session.query(TaskORM).filter(
                TaskORM.todo_id == todo_id, 
                TaskORM.parent_id.is_(None)
            ).all()
            return [self._to_domain_task(task_orm) for task_orm in task_orms]
    
    def get_subtasks_by_parent_id(self, parent_id: int) -> List[Task]:
        with self.__session_factory() as session:
            task_orms = session.query(TaskORM).filter(TaskORM.parent_id == parent_id).all()
            return [self._to_domain_task(task_orm) for task_orm in task_orms]

    def update(self, task: Task) -> Task:
        with self.__session_factory() as session:
            task_orm = session.query(TaskORM).filter(TaskORM.id == task.id).first()
            if task_orm:
                # subtasks 필드를 제외하고 업데이트
                task_orm.title = task.title
                task_orm.points = task.points
                task_orm.todo_id = task.todo_id
                task_orm.completed = task.completed
                task_orm.parent_id = task.parent_id
                
                session.commit()
                session.refresh(task_orm)
                return self._to_domain_task(task_orm)
            raise ValueError(f"Task with id {task.id} not found")

    def delete(self, task_id: int) -> None:
        with self.__session_factory() as session:
            task_orm = session.query(TaskORM).filter(TaskORM.id == task_id).first()
            if task_orm:
                session.delete(task_orm)
                session.commit()

    def delete_with_descendants(self, task_id: int) -> None:
        """태스크와 모든 하위 태스크를 연쇄 삭제합니다."""
        with self.__session_factory() as session:
            self._delete_task_and_descendants_recursive(session, task_id)
            session.commit()
    
    def _delete_task_and_descendants_recursive(self, session, task_id: int) -> None:
        """재귀적으로 태스크와 하위 태스크들을 삭제합니다."""
        # 먼저 하위 태스크들을 찾아서 재귀적으로 삭제
        subtasks = session.query(TaskORM).filter(TaskORM.parent_id == task_id).all()
        for subtask in subtasks:
            self._delete_task_and_descendants_recursive(session, subtask.id)
        
        # 현재 태스크 삭제
        task_orm = session.query(TaskORM).filter(TaskORM.id == task_id).first()
        if task_orm:
            session.delete(task_orm)

    def _to_domain_task(self, task_orm: TaskORM) -> Task:
        return Task(
            id=task_orm.id,
            title=task_orm.title,
            points=task_orm.points,
            todo_id=task_orm.todo_id,
            completed=task_orm.completed,
            parent_id=task_orm.parent_id,
        )
