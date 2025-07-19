import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
import os

logger = logging.getLogger(__name__)


def create_db_engine(db_user: str, db_pwd: str, db_host: str, db_name: str):
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return create_engine(database_url)
    else:
        # Fallback for local development without docker-compose
        return create_engine(
            f"mysql+pymysql://{db_user}:{db_pwd}@{db_host}:3306/{db_name}"
        )


class Database:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        self._initialize_database()

    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
    
    def _initialize_database(self) -> None:
        """Initialize database tables if they don't exist"""
        from src.infrastructure.database.sqlalchemy_models import Base
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise