from src.domain.models.task import Task

class TaskMapper:
    @staticmethod
    def to_domain(task_data: dict) -> Task:
        return Task(
            id=task_data.get("id"),
            title=task_data["title"],
            description=task_data.get("description"),
            points=task_data["points"],
            todo_id=task_data["todo_id"]
        )

    @staticmethod
    def to_dict(task: Task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "points": task.points,
            "todo_id": task.todo_id
        }
