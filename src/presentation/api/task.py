from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.application.services.task_service import TaskService
from src.containers import Container
from src.domain.models.task import Task
from src.presentation.api.schemas import TaskCreate, TaskUpdate, TaskResponse
from src.presentation.api.auth import get_current_user
from src.domain.models.user import User

router = APIRouter(prefix="/api")


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Task 생성",
    description="""
    새로운 Task를 생성합니다.

    **요청 본문:**
    - `title`: Task 제목 (필수)
    - `points`: Task 점수 (필수)
    - `todo_id`: 연결될 Todo의 ID (필수)
    - `completed`: 완료 여부 (선택, 기본값: false)
    - `parent_id`: 부모 Task ID (선택, Subtask로 만들 경우)

    **주의:**
    - `parent_id`를 지정하면 해당 Task의 Subtask로 생성됩니다
    - 여러 Task를 한 번에 생성하려면 `/api/todos/bulk` 엔드포인트를 사용하세요
    """,
    responses={
        201: {
            "description": "Task 생성 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "회의 준비",
                        "points": 5,
                        "todo_id": 1,
                        "completed": False,
                        "subtasks": [],
                    }
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
    },
)
@inject
def create_task(
    task_create: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    task = Task(
        id=None,
        title=task_create.title,
        points=task_create.points,
        todo_id=task_create.todo_id,
        user_id=current_user.id,
        completed=task_create.completed,
        parent_id=task_create.parent_id,
    )
    created_task = task_service.create_task(task)
    return created_task


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Task 상세 조회",
    description="""
    특정 Task의 상세 정보를 조회합니다.

    **권한:**
    - 본인이 생성한 Task만 조회 가능합니다

    **응답 데이터:**
    - Task 정보와 함께 모든 Subtask를 포함합니다
    """,
    responses={
        200: {
            "description": "Task 조회 성공",
            "content": {
                "application/json": {
                    "example": {
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
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "Task를 찾을 수 없거나 접근 권한이 없음"},
    },
)
@inject
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    task = task_service.get_task_with_subtasks(task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.get(
    "/todos/{todo_id}/tasks",
    response_model=List[TaskResponse],
    summary="Todo의 모든 Task 조회",
    description="""
    특정 Todo에 속한 모든 Task를 조회합니다.

    **권한:**
    - 본인이 생성한 Todo의 Task만 조회 가능합니다

    **응답 데이터:**
    - 각 Task는 모든 Subtask를 포함합니다
    - 부모 Task만 반환되며, Subtask는 각 부모의 `subtasks` 배열에 포함됩니다
    """,
    responses={
        200: {
            "description": "Task 목록 조회 성공",
            "content": {
                "application/json": {
                    "example": [
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
                    ]
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
    },
)
@inject
def get_tasks_by_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    tasks = task_service.get_tasks_with_subtasks_by_todo_id(todo_id, current_user.id)
    return tasks


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Task 수정",
    description="""
    기존 Task의 정보를 수정합니다.

    **수정 가능한 필드:**
    - `title`: Task 제목
    - `points`: Task 점수
    - `completed`: 완료 여부
    - `parent_id`: 부모 Task ID (Subtask 관계 변경)

    **주의:**
    - 모든 필드는 선택 사항입니다
    - 제공된 필드만 업데이트됩니다
    - 본인이 생성한 Task만 수정 가능합니다
    """,
    responses={
        200: {
            "description": "Task 수정 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "회의 준비 (수정됨)",
                        "points": 7,
                        "todo_id": 1,
                        "completed": True,
                        "subtasks": [],
                    }
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "Task를 찾을 수 없거나 접근 권한이 없음"},
    },
)
@inject
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    try:
        updated_task = task_service.update_task(
            task_id=task_id,
            title=task_update.title,
            points=task_update.points,
            completed=task_update.completed,
            parent_id=task_update.parent_id,
            user_id=current_user.id,
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/tasks/{task_id}/toggle",
    response_model=TaskResponse,
    summary="Task 완료 상태 토글",
    description="""
    Task의 완료 상태를 토글합니다.

    **동작:**
    - `completed`가 `true`이면 `false`로 변경
    - `completed`가 `false`이면 `true`로 변경

    **편의성:**
    - 현재 상태를 확인하지 않고 간단하게 완료 상태를 전환할 수 있습니다
    - 본인이 생성한 Task만 수정 가능합니다
    """,
    responses={
        200: {
            "description": "Task 완료 상태 토글 성공",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "회의 준비",
                        "points": 5,
                        "todo_id": 1,
                        "completed": True,
                        "subtasks": [],
                    }
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "Task를 찾을 수 없거나 접근 권한이 없음"},
    },
)
@inject
def toggle_task_completion(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    try:
        updated_task = task_service.toggle_task_completion(task_id, current_user.id)
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Task 삭제",
    description="""
    Task를 삭제합니다.

    **주의:**
    - 이 작업은 되돌릴 수 없습니다
    - 부모 Task를 삭제하면 모든 Subtask도 함께 삭제됩니다
    - 본인이 생성한 Task만 삭제 가능합니다
    """,
    responses={
        204: {"description": "Task 삭제 성공 (응답 본문 없음)"},
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "Task를 찾을 수 없거나 접근 권한이 없음"},
    },
)
@inject
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    try:
        task_service.delete_task(task_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
