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
from src.application.services.ai_service import AIService
from src.infrastructure.ai.gemini_model_service import GeminiModelService
from src.infrastructure.auth import KakaoAuthProvider


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
    todo_repository: providers.Provider[ITodoRepository] = providers.Factory(
        SQLAlchemyTodoRepository, session_factory=database.provided.session
    )
    task_repository: providers.Provider[ITaskRepository] = providers.Factory(
        SQLAlchemyTaskRepository, session_factory=database.provided.session
    )
    user_repository: providers.Provider[UserRepository] = providers.Factory(
        SqlAlchemyUserRepository, session_factory=database.provided.session
    )

    # AI Model Services
    gemini_model_service = providers.Factory(
        GeminiModelService, api_key=config.gemini.api_key
    )

    # AI Service
    ai_service = providers.Factory(AIService, model_service=gemini_model_service)

    # Auth Providers
    kakao_auth_provider = providers.Factory(KakaoAuthProvider)

    # Services
    task_service = providers.Factory(TaskService, task_repository=task_repository)
    todo_service = providers.Factory(
        TodoService, todo_repository=todo_repository, task_service=task_service
    )
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        auth_provider=kakao_auth_provider,
    )
