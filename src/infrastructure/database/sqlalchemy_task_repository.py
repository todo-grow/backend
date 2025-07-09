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
                description=task.description,
                points=task.points,
                todo_id=task.todo_id,
                completed=task.completed,
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
            task_orms = session.query(TaskORM).filter(TaskORM.todo_id == todo_id).all()
            return [self._to_domain_task(task_orm) for task_orm in task_orms]

    def update(self, task: Task) -> Task:
        with self.__session_factory() as session:
            task_orm = session.query(TaskORM).filter(TaskORM.id == task.id).first()
            if task_orm:
                for key, value in task.__dict__.items():
                    setattr(task_orm, key, value)
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

    def _to_domain_task(self, task_orm: TaskORM) -> Task:
        return Task(
            id=task_orm.id,
            title=task_orm.title,
            description=task_orm.description,
            points=task_orm.points,
            todo_id=task_orm.todo_id,
            completed=task_orm.completed,
        )
