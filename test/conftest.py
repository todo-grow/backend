import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.infrastructure.database.sqlalchemy_models import Base


@pytest.fixture
def in_memory_sqlite_db():
    """SQLite 인메모리 데이터베이스 생성"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_sqlite_db):
    """세션 팩토리 생성"""
    yield sessionmaker(bind=in_memory_sqlite_db)


@pytest.fixture
def db_session(session_factory):
    """데이터베이스 세션 fixture"""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()