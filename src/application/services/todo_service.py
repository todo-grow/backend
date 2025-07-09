from typing import List, Optional
from datetime import date
from src.domain.models.todo import Todo
from src.domain.repositories.todo_repository import ITodoRepository

class TodoService:
    def __init__(self, todo_repository: ITodoRepository):
        self.todo_repository = todo_repository

    def get_all_todos(self) -> List[Todo]:
        return self.todo_repository.get_all_todos()

    def create_todo(self, title: str, base_date: Optional[date] = None) -> Todo:
        if base_date is None:
            base_date = date.today()
        todo = Todo(title=title, base_date=base_date)
        return self.todo_repository.create_todo(todo)
