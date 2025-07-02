from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.application.services.todo_service import TodoService
from src.domain.models.todo import Todo
from src.infrastructure.database.in_memory_todo_repository import InMemoryTodoRepository

router = APIRouter()

# Create a single repository instance to be shared across requests
todo_repository = InMemoryTodoRepository()

def get_todo_service():
    return TodoService(todo_repository)

@router.get("/todos", response_model=List[Todo])
def get_all_todos(service: TodoService = Depends(get_todo_service)):
    return service.get_all_todos()

@router.get("/todos/{todo_id}", response_model=Todo)
def get_todo_by_id(todo_id: int, service: TodoService = Depends(get_todo_service)):
    todo = service.get_todo_by_id(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.post("/todos", response_model=Todo)
def create_todo(title: str, service: TodoService = Depends(get_todo_service)):
    return service.create_todo(title)

@router.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, title: str, completed: bool, service: TodoService = Depends(get_todo_service)):
    todo = service.update_todo(todo_id, title, completed)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, service: TodoService = Depends(get_todo_service)):
    service.delete_todo(todo_id)
    return {"message": "Todo deleted successfully"}
