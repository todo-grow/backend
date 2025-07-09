from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class TodoORM(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    base_date = Column(Date, default=date.today)

    tasks = relationship("TaskORM", back_populates="todo")

class TaskORM(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    points = Column(Integer)
    todo_id = Column(Integer, ForeignKey("todos.id"))
    completed = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    todo = relationship("TodoORM", back_populates="tasks")
    parent = relationship("TaskORM", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("TaskORM", back_populates="parent")
