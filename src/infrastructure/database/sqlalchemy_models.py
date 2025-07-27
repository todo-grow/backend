from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class TodoORM(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    base_date = Column(Date, default=date.today)

    user = relationship("UserORM", back_populates="todos")
    tasks = relationship("TaskORM", back_populates="todo")

class TaskORM(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    points = Column(Integer)
    todo_id = Column(Integer, ForeignKey("todos.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    todo = relationship("TodoORM", back_populates="tasks")
    user = relationship("UserORM", back_populates="tasks")
    parent = relationship("TaskORM", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("TaskORM", back_populates="parent")


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String(100), unique=True, nullable=True)
    email = Column(String(255), nullable=True)
    nickname = Column(String(100), nullable=True)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    todos = relationship("TodoORM", back_populates="user")
    tasks = relationship("TaskORM", back_populates="user")
