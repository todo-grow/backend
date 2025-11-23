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
@router.get(
    "/todos",
    response_model=List[TodoResponse],
    summary="Todo 목록 조회",
    description="""
    현재 로그인한 사용자의 Todo 목록을 조회합니다.

    **필터링 옵션:**
    - `target_date` 파라미터를 사용하여 특정 날짜의 Todo만 조회 가능
    - 파라미터를 생략하면 모든 Todo를 반환

    **응답 데이터:**
    - 각 Todo는 연결된 Task 및 Subtask를 포함합니다
    """,
    responses={
        200: {
            "description": "Todo 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "base_date": "2025-12-25",
                            "tasks": [
                                {
                                    "id": 1,
                                    "title": "회의 준비",
                                    "points": 5,
                                    "todo_id": 1,
                                    "completed": False,
                                    "subtasks": [],
                                }
                            ],
                        }
                    ]
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
    },
)
@inject
def get_all_todos(
    target_date: Optional[date] = Query(
        None, description="특정 날짜의 Todo만 필터링 (YYYY-MM-DD 형식)"
    ),
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(Provide[Container.todo_service]),
):
    if target_date:
        todos = service.get_todos_by_date_with_tasks(target_date, current_user.id)
    else:
        todos = service.get_all_todos_with_tasks(current_user.id)
    return [TodoMapper.to_todo_response(todo) for todo in todos]


@router.get(
    "/todos/{todo_id}",
    response_model=TodoResponse,
    summary="Todo 상세 조회",
    description="""
    특정 Todo의 상세 정보를 조회합니다.

    **권한:**
    - 본인이 생성한 Todo만 조회 가능합니다

    **응답 데이터:**
    - Todo 정보와 함께 모든 Task 및 Subtask를 포함합니다
    """,
    responses={
        200: {
            "description": "Todo 조회 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "base_date": "2025-12-25",
                        "tasks": [
                            {
                                "id": 1,
                                "title": "회의 준비",
                                "points": 5,
                                "todo_id": 1,
                                "completed": False,
                                "subtasks": [
                                    {
                                        "id": 2,
                                        "title": "안건 작성",
                                        "points": 2,
                                        "todo_id": 1,
                                        "completed": False,
                                    }
                                ],
                            }
                        ],
                    }
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "Todo를 찾을 수 없거나 접근 권한이 없음"},
    },
)
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


@router.post(
    "/todos",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Todo 생성",
    description="""
    새로운 Todo를 생성합니다.

    **요청 본문:**
    - `base_date`: Todo의 기준 날짜 (선택 사항, 기본값: 오늘 날짜)

    **주의:**
    - 이 엔드포인트는 빈 Todo만 생성합니다
    - Task를 함께 생성하려면 `/api/todos/bulk` 엔드포인트를 사용하세요
    """,
    responses={
        201: {
            "description": "Todo 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "base_date": "2025-12-25",
                        "tasks": [],
                    }
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
    },
)
@inject
def create_todo(
    todo_create: TodoCreate,
    current_user: User = Depends(get_current_user),
    service: TodoService = Depends(Provide[Container.todo_service]),
):
    todo = service.create_todo(base_date=todo_create.base_date, user_id=current_user.id)
    return TodoMapper.to_todo_response(todo)


@router.post(
    "/todos/ai",
    response_model=AITodoResponse,
    summary="AI를 활용한 Todo 구조 생성",
    description="""
    자연어 입력을 받아 AI가 Todo와 Task 구조를 생성합니다.

    **중요:**
    - 이 엔드포인트는 데이터를 저장하지 않습니다
    - 생성된 구조를 확인 후 `/api/todos/bulk` 엔드포인트로 실제 저장하세요

    **요청 본문:**
    - `user_input`: 할 일에 대한 자연어 설명
    - `base_date`: Todo 기준 날짜 (선택 사항)

    **AI 처리:**
    - 입력된 텍스트를 분석하여 적절한 Task와 Subtask로 구조화
    - 각 Task와 Subtask에 점수(points) 자동 할당
    """,
    responses={
        200: {
            "description": "AI Todo 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "base_date": "2025-12-25",
                        "tasks": [
                            {
                                "title": "회의 준비",
                                "points": 5,
                                "subtasks": [
                                    {"title": "회의 자료 정리", "points": 3},
                                    {"title": "발표 자료 작성", "points": 4},
                                ],
                            },
                            {"title": "보고서 작성", "points": 7, "subtasks": []},
                        ],
                    }
                }
            },
        },
    },
)
@inject
def create_todo_with_ai(
    ai_todo_create: AITodoCreate,
    ai_service: AIService = Depends(Provide[Container.ai_service]),
):
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
    "/todos/bulk",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Todo와 Task 일괄 생성",
    description="""
    Todo와 여러 Task를 한 번에 생성합니다.

    **기능:**
    - Todo 생성과 동시에 여러 Task 생성
    - `parent_id`를 사용하여 Task 간 부모-자식 관계 설정 가능

    **parent_id 사용법:**
    - `parent_id`는 `tasks` 배열의 인덱스를 의미합니다 (0부터 시작)
    - 부모 Task는 자식 Task보다 먼저 배열에 위치해야 합니다
    - 예: `parent_id: 0`은 첫 번째 Task의 자식임을 의미

    **요청 본문 예시:**
    ```json
    {
        "base_date": "2025-01-15",
        "tasks": [
            {"title": "회의 준비", "points": 3, "completed": false},
            {"title": "안건 작성", "points": 1, "completed": false, "parent_id": 0},
            {"title": "자료 수집", "points": 1, "completed": false, "parent_id": 0}
        ]
    }
    ```

    **주의:**
    - `parent_id`가 유효하지 않으면 400 오류 반환
    - 빈 `tasks` 배열로 요청하면 Task 없는 Todo만 생성됩니다
    """,
    responses={
        201: {
            "description": "Todo와 Task 일괄 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "base_date": "2025-01-15",
                        "tasks": [
                            {
                                "id": 1,
                                "title": "회의 준비",
                                "points": 3,
                                "todo_id": 1,
                                "completed": False,
                                "subtasks": [
                                    {
                                        "id": 2,
                                        "title": "안건 작성",
                                        "points": 1,
                                        "todo_id": 1,
                                        "completed": False,
                                    },
                                    {
                                        "id": 3,
                                        "title": "자료 수집",
                                        "points": 1,
                                        "todo_id": 1,
                                        "completed": False,
                                    },
                                ],
                            }
                        ],
                    }
                }
            },
        },
        400: {"description": "잘못된 parent_id 값"},
        401: {"description": "인증되지 않은 사용자"},
    },
)
@inject
def create_todo_bulk(
    bulk_todo_create: BulkTodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(Provide[Container.todo_service]),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
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
