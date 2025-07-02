from typing import List, Optional
from src.domain.models.todo import Todo
from src.domain.repositories.todo_repository import TodoRepository

class InMemoryTodoRepository(TodoRepository):
    def __init__(self):
        self.todos: List[Todo] = []
        self.next_id = 1

    def get_all(self) -> List[Todo]:
        return self.todos

    def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return next((todo for todo in self.todos if todo.id == todo_id), None)

    def create(self, todo: Todo) -> Todo:
        todo.id = self.next_id
        self.todos.append(todo)
        self.next_id += 1
        return todo

    def update(self, todo: Todo) -> Todo:
        index = next((i for i, t in enumerate(self.todos) if t.id == todo.id), None)
        if index is not None:
            self.todos[index] = todo
            return todo
        return None

    def delete(self, todo_id: int) -> None:
        self.todos = [todo for todo in self.todos if todo.id != todo_id]
