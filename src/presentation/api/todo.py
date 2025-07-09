from fastapi import APIRouter, Depends, status
from typing import List
from dependency_injector.wiring import inject, Provide

from src.application.services.todo_service import TodoService
from src.presentation.api.schemas import TodoCreate, TodoResponse
from src.application.mappers.todo_mapper import TodoMapper
from src.containers import Container

router = APIRouter()

# Todo CRUD operations
@router.get("/todos", response_model=List[TodoResponse])
@inject
def get_all_todos(service: TodoService = Depends(Provide[Container.todo_service])):
    todos = service.get_all_todos()
    return [TodoMapper.to_todo_response(todo) for todo in todos]

@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_todo(todo_create: TodoCreate, service: TodoService = Depends(Provide[Container.todo_service])):
    todo = service.create_todo(title=todo_create.title, base_date=todo_create.base_date)
    return TodoMapper.to_todo_response(todo)

