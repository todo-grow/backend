from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    base_date: Optional[date] = None


class TodoResponse(BaseModel):
    id: int
    title: str
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


class TaskResponse(BaseModel):
    id: int
    title: str
    points: int
    todo_id: int
    completed: bool
    subtasks: List['TaskResponse'] = []

    class Config:
        from_attributes = True
