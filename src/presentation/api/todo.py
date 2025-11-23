from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Optional
from datetime import date
from dependency_injector.wiring import inject, Provide

from src.application.services.todo_service import TodoService
from src.application.services.task_service import TaskService
from src.presentation.api.schemas import (
    TodoCreate,
    TodoResponse,
    AITodoCreate,
    AITodoResponse,
    AITaskData,
    AISubtaskData,
    BulkTodoCreate,
)
from src.application.mappers.todo_mapper import TodoMapper
from src.containers import Container
from src.presentation.api.auth import get_current_user
from src.domain.models.user import User
from src.application.services.ai_service import AIService
from src.domain.models.task import Task

router = APIRouter(prefix="/api")


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
    service: TodoService = Depends(Provide[Container.todo_service]),
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


@router.post("/todos/ai", response_model=AITodoResponse)
@inject
def create_todo_with_ai(
    ai_todo_create: AITodoCreate,
    ai_service: AIService = Depends(Provide[Container.ai_service]),
):
    """
    자연어 입력을 받아 AI가 TODO와 Task 구조를 생성합니다. (저장하지 않음)

    예시:
    {
        "user_input": "내일 회의 준비하고 보고서 작성해야 해",
        "base_date": "2024-01-15"  # Optional
    }
    """
    # AI로 TODO 구조 생성
    ai_result = ai_service.generate_todos_from_text(
        user_input=ai_todo_create.user_input, target_date=ai_todo_create.base_date
    )

    # AI 결과를 응답 형식으로 변환
    tasks = [
        AITaskData(
            title=task["title"],
            points=task["points"],
            subtasks=[
                AISubtaskData(title=subtask["title"], points=subtask["points"])
                for subtask in task.get("subtasks", [])
            ],
        )
        for task in ai_result["tasks"]
    ]

    return AITodoResponse(base_date=ai_todo_create.base_date, tasks=tasks)


@router.post(
    "/todos/bulk", response_model=TodoResponse, status_code=status.HTTP_201_CREATED
)
@inject
def create_todo_bulk(
    bulk_todo_create: BulkTodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(Provide[Container.todo_service]),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    """
    TODO와 여러 Task를 한번에 생성합니다. parent_id를 사용하여 부모-자식 관계를 설정할 수 있습니다.

    예시:
    {
        "base_date": "2024-01-15",
        "tasks": [
            {"title": "회의 준비", "points": 3, "completed": false},
            {"title": "안건 작성", "points": 1, "completed": false, "parent_id": 0},
            {"title": "자료 수집", "points": 1, "completed": false, "parent_id": 0}
        ]
    }

    parent_id는 tasks 배열의 인덱스를 의미합니다 (0부터 시작).
    """
    # TODO 생성
    todo = todo_service.create_todo(
        base_date=bulk_todo_create.base_date, user_id=current_user.id
    )

    created_tasks = []

    for task_data in bulk_todo_create.tasks:
        # parent_id가 있으면 이미 생성된 task의 실제 ID를 참조
        actual_parent_id = None
        if task_data.parent_id is not None:
            if 0 <= task_data.parent_id < len(created_tasks):
                actual_parent_id = created_tasks[task_data.parent_id].id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid parent_id: {task_data.parent_id}",
                )

        task = Task(
            id=None,
            title=task_data.title,
            points=task_data.points,
            todo_id=todo.id,
            user_id=current_user.id,
            completed=task_data.completed,
            parent_id=actual_parent_id,
        )
        created_task = task_service.create_task(task)
        created_tasks.append(created_task)

    # 생성된 TODO와 모든 Task를 함께 반환
    complete_todo = todo_service.get_todo_with_tasks(todo.id)
    return TodoMapper.to_todo_response(complete_todo)
