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
    
    def get_all_todos_with_tasks(self, user_id: int) -> List[Todo]:
        todos = self.todo_repository.get_all_todos_by_user(user_id)
        for todo in todos:
            todo.tasks = self.task_service.get_tasks_with_subtasks_by_todo_id(todo.id, user_id)
        return todos
    
    def get_todos_by_date_with_tasks(self, target_date: date, user_id: int) -> List[Todo]:
        todos = self.todo_repository.get_todos_by_date_and_user(target_date, user_id)
        for todo in todos:
            todo.tasks = self.task_service.get_tasks_with_subtasks_by_todo_id(todo.id, user_id)
        return todos
    
    def get_todo_by_id(self, todo_id: int) -> Optional[Todo]:
        return self.todo_repository.get_by_id(todo_id)
    
    def get_todo_with_tasks(self, todo_id: int) -> Optional[Todo]:
        todo = self.todo_repository.get_by_id(todo_id)
        if todo:
            todo.tasks = self.task_service.get_tasks_with_subtasks_by_todo_id(todo_id, todo.user_id)
        return todo

    def create_todo(self, base_date: Optional[date] = None, user_id: int = None) -> Todo:
        if base_date is None:
            base_date = date.today()
        
        # Check if todo already exists for this date and user
        existing_todos = self.todo_repository.get_todos_by_date_and_user(base_date, user_id)
        if existing_todos:
            return existing_todos[0]
        
        todo = Todo(base_date=base_date, user_id=user_id)
        return self.todo_repository.create_todo(todo)
