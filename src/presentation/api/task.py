from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.application.services.task_service import TaskService
from src.containers import Container
from src.domain.models.task import Task
from src.presentation.api.schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_task(
    task_create: TaskCreate,
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    task = Task(
        id=None,
        title=task_create.title,
        points=task_create.points,
        todo_id=task_create.todo_id,
        completed=task_create.completed,
        parent_id=task_create.parent_id,
    )
    created_task = task_service.create_task(task)
    return created_task


@router.get("/tasks/{task_id}", response_model=TaskResponse)
@inject
def get_task(
    task_id: int, task_service: TaskService = Depends(Provide[Container.task_service])
):
    task = task_service.get_task_with_subtasks(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.get("/todos/{todo_id}/tasks", response_model=List[TaskResponse])
@inject
def get_tasks_by_todo(
    todo_id: int, task_service: TaskService = Depends(Provide[Container.task_service])
):
    tasks = task_service.get_tasks_with_subtasks_by_todo_id(todo_id)
    return tasks


@router.put("/tasks/{task_id}", response_model=TaskResponse)
@inject
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    try:
        updated_task = task_service.update_task(
            task_id=task_id,
            title=task_update.title,
            points=task_update.points,
            completed=task_update.completed,
            parent_id=task_update.parent_id,
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/tasks/{task_id}/toggle", response_model=TaskResponse)
@inject
def toggle_task_completion(
    task_id: int,
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    try:
        updated_task = task_service.toggle_task_completion(task_id)
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_task(
    task_id: int, task_service: TaskService = Depends(Provide[Container.task_service])
):
    try:
        task_service.delete_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
