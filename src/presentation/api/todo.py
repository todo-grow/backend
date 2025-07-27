from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Optional
from datetime import date
from dependency_injector.wiring import inject, Provide

from src.application.services.todo_service import TodoService
from src.presentation.api.schemas import TodoCreate, TodoResponse
from src.application.mappers.todo_mapper import TodoMapper
from src.containers import Container
from src.presentation.api.auth import get_current_user
from src.domain.models.user import User

router = APIRouter()


# Todo CRUD operations
@router.get("/todos", response_model=List[TodoResponse])
@inject
def get_all_todos(
    target_date: Optional[date] = Query(
        None, description="Filter todos by date (YYYY-MM-DD)"
    ),
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(Provide[Container.todo_service]),
):
    if target_date:
        todos = service.get_todos_by_date_with_tasks(target_date, current_user.id)
    else:
        todos = service.get_all_todos_with_tasks(current_user.id)
    return [TodoMapper.to_todo_response(todo) for todo in todos]


@router.get("/todos/{todo_id}", response_model=TodoResponse)
@inject
def get_todo(
    todo_id: int, 
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(Provide[Container.todo_service])
):
    todo = service.get_todo_with_tasks(todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found"
        )
    return TodoMapper.to_todo_response(todo)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_todo(
    todo_create: TodoCreate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(Provide[Container.todo_service]),
):
    todo = service.create_todo(base_date=todo_create.base_date, user_id=current_user.id)
    return TodoMapper.to_todo_response(todo)
