from typing import List, Optional
from datetime import date
from src.domain.models.todo import Todo
from src.domain.repositories.todo_repository import ITodoRepository
from src.application.services.task_service import TaskService

class TodoService:
    def __init__(self, todo_repository: ITodoRepository, task_service: TaskService):
        self.todo_repository = todo_repository
        self.task_service = task_service

    def get_all_todos(self) -> List[Todo]:
        return self.todo_repository.get_all_todos()
    
    def get_all_todos_with_tasks(self) -> List[Todo]:
        todos = self.todo_repository.get_all_todos()
        for todo in todos:
            todo.tasks = self.task_service.get_tasks_with_subtasks_by_todo_id(todo.id)
        return todos
    
    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        return self.todo_repository.get_by_id(todo_id)
    
    def get_todo_with_tasks(self, todo_id: int) -> Optional[Todo]:
        todo = self.todo_repository.get_by_id(todo_id)
        if todo:
            todo.tasks = self.task_service.get_tasks_with_subtasks_by_todo_id(todo_id)
        return todo

    def create_todo(self, title: str, base_date: Optional[date] = None) -> Todo:
        if base_date is None:
            base_date = date.today()
        todo = Todo(title=title, base_date=base_date)
        return self.todo_repository.create_todo(todo)
