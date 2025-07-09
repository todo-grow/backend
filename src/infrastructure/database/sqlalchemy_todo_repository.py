from typing import List
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
            todo_orm = TodoORM(title=todo.title, base_date=todo.base_date)
            session.add(todo_orm)
            session.commit()
            session.refresh(todo_orm)
            return self._to_domain_todo(todo_orm)

    def _to_domain_todo(self, todo_orm: TodoORM) -> Todo:
        return Todo(id=todo_orm.id, title=todo_orm.title, base_date=todo_orm.base_date)
