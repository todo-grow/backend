from src.domain.models.todo import Todo
from src.presentation.api.schemas import TodoResponse, TaskResponse


class TodoMapper:
    @staticmethod
    def to_todo_response(todo: Todo) -> TodoResponse:
        return TodoResponse(
            id=todo.id,
            title=todo.title,
            base_date=todo.base_date,
            tasks=[TodoMapper._to_task_response(task) for task in todo.tasks]
        )
    
    @staticmethod
    def _to_task_response(task) -> TaskResponse:
        return TaskResponse(
            id=task.id,
            title=task.title,
            points=task.points,
            todo_id=task.todo_id,
            completed=task.completed,
            subtasks=[TodoMapper._to_task_response(subtask) for subtask in task.subtasks]
        )
