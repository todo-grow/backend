from typing import List, Optional
from src.domain.models.todo import Todo
from src.domain.repositories.todo_repository import TodoRepository

class TodoService:
    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    def get_all_todos(self) -> List[Todo]:
        return self.todo_repository.get_all()

    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        return self.todo_repository.get_by_id(todo_id)

    def create_todo(self, title: str) -> Todo:
        todo = Todo(id=0, title=title, completed=False)
        return self.todo_repository.create(todo)

    def update_todo(self, todo_id: int, title: str, completed: bool) -> Optional[Todo]:
        todo = self.todo_repository.get_by_id(todo_id)
        if todo:
            todo.title = title
            todo.completed = completed
            return self.todo_repository.update(todo)
        return None

    def delete_todo(self, todo_id: int) -> None:
        self.todo_repository.delete(todo_id)
