from src.domain.models.todo import Todo
from src.presentation.api.schemas import TodoResponse


class TodoMapper:
    @staticmethod
    def to_todo_response(todo: Todo) -> TodoResponse:
        return TodoResponse(
            id=todo.id,
            title=todo.title,
            base_date=todo.base_date
        )
