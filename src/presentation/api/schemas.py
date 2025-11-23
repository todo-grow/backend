from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class TodoCreate(BaseModel):
    base_date: Optional[date] = None


class AITodoCreate(BaseModel):
    user_input: str
    base_date: Optional[date] = None


class TodoResponse(BaseModel):
    id: int
    base_date: date
    tasks: List['TaskResponse'] = []

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    points: int
    todo_id: int
    completed: bool = False
    parent_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    points: Optional[int] = None
    completed: Optional[bool] = None
    parent_id: Optional[int] = None


class SubtaskResponse(BaseModel):
    id: int
    title: str
    points: int
    todo_id: int
    completed: bool

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    title: str
    points: int
    todo_id: int
    completed: bool
    subtasks: List[SubtaskResponse] = []

    class Config:
        from_attributes = True


class AITaskData(BaseModel):
    title: str
    points: int
    subtasks: List['AISubtaskData'] = []


class AISubtaskData(BaseModel):
    title: str
    points: int


class AITodoResponse(BaseModel):
    base_date: Optional[date] = None
    tasks: List[AITaskData] = []


class BulkTaskCreate(BaseModel):
    title: str
    points: int
    completed: bool = False
    parent_id: Optional[int] = None


class BulkTodoCreate(BaseModel):
    base_date: Optional[date] = None
    tasks: List[BulkTaskCreate] = []
