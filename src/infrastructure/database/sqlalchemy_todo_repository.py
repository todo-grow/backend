from typing import List, Optional
from datetime import date
from src.domain.models.todo import Todo
from src.domain.repositories.todo_repository import ITodoRepository
from src.infrastructure.database.sqlalchemy_models import TodoORM


class SQLAlchemyTodoRepository(ITodoRepository):
    def __init__(self, session_factory):
        self.__session_factory = session_factory

    def get_all_todos(self) -> List[Todo]:
        with self.__session_factory() as session:
            todos_orm = session.query(TodoORM).all()
            return [self._to_domain_todo(todo_orm) for todo_orm in todos_orm]

    def create_todo(self, todo: Todo) -> Todo:
        with self.__session_factory() as session:
            # Check if todo already exists for this date and user
            existing_todo = (
                session.query(TodoORM)
                .filter(TodoORM.base_date == todo.base_date)
                .filter(TodoORM.user_id == todo.user_id)
                .first()
            )
            if existing_todo:
                return self._to_domain_todo(existing_todo)

            todo_orm = TodoORM(base_date=todo.base_date, user_id=todo.user_id)
            session.add(todo_orm)
            session.commit()
            session.refresh(todo_orm)
            return self._to_domain_todo(todo_orm)

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        with self.__session_factory() as session:
            todo_orm = session.query(TodoORM).filter(TodoORM.id == todo_id).first()
            if todo_orm:
                return self._to_domain_todo(todo_orm)
            return None

    def get_todos_by_date(self, target_date: date) -> List[Todo]:
        with self.__session_factory() as session:
            todos_orm = (
                session.query(TodoORM).filter(TodoORM.base_date == target_date).all()
            )
            return [self._to_domain_todo(todo_orm) for todo_orm in todos_orm]

    def get_all_todos_by_user(self, user_id: int) -> List[Todo]:
        with self.__session_factory() as session:
            todos_orm = session.query(TodoORM).filter(TodoORM.user_id == user_id).all()
            return [self._to_domain_todo(todo_orm) for todo_orm in todos_orm]

    def get_todos_by_date_and_user(self, target_date: date, user_id: int) -> List[Todo]:
        with self.__session_factory() as session:
            todos_orm = (
                session.query(TodoORM)
                .filter(TodoORM.base_date == target_date)
                .filter(TodoORM.user_id == user_id)
                .all()
            )
            return [self._to_domain_todo(todo_orm) for todo_orm in todos_orm]

    def _to_domain_todo(self, todo_orm: TodoORM) -> Todo:
        return Todo(id=todo_orm.id, user_id=todo_orm.user_id, base_date=todo_orm.base_date)
