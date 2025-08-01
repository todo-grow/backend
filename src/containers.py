from dependency_injector import containers, providers

from src.database import Database, create_db_engine
from src.domain.repositories.todo_repository import ITodoRepository
from src.domain.repositories.task_repository import ITaskRepository
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.sqlalchemy_todo_repository import (
    SQLAlchemyTodoRepository,
)
from src.infrastructure.database.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from src.infrastructure.database.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from src.application.services.todo_service import TodoService
from src.application.services.task_service import TaskService
from src.application.services.auth_service import AuthService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src.presentation.api"])

    # Configuration
    config = providers.Configuration()

    # Database
    db_engine = providers.Callable(
        create_db_engine,
        db_user=config.db.user,
        db_pwd=config.db.password,
        db_host=config.db.host,
        db_name=config.db.name,
    )

    database = providers.Singleton(Database, engine=db_engine)

    # Repositories
    todo_repository: providers.Provider[ITodoRepository] = providers.Singleton(
        SQLAlchemyTodoRepository, session_factory=database.provided.session
    )
    task_repository: providers.Provider[ITaskRepository] = providers.Singleton(
        SQLAlchemyTaskRepository, session_factory=database.provided.session
    )
    user_repository: providers.Provider[UserRepository] = providers.Singleton(
        SqlAlchemyUserRepository, session_factory=database.provided.session
    )

    # Services
    task_service = providers.Singleton(TaskService, task_repository=task_repository)
    todo_service = providers.Singleton(TodoService, todo_repository=todo_repository, task_service=task_service)
    auth_service = providers.Singleton(AuthService, user_repository=user_repository)
