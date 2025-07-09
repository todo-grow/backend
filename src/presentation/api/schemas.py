from datetime import date
from typing import Optional

from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    base_date: Optional[date] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    base_date: date

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    points: int
    todo_id: int
    completed: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    points: Optional[int] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    points: int
    todo_id: int
    completed: bool

    class Config:
        from_attributes = True
