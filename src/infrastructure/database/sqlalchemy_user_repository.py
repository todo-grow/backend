from typing import Optional
from sqlalchemy.orm import Session
from src.domain.models.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.sqlalchemy_models import UserORM


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self._session_factory() as session:
            user_orm = session.query(UserORM).filter(UserORM.id == user_id).first()
            if user_orm:
                return self._to_domain(user_orm)
            return None

    def get_by_kakao_id(self, kakao_id: str) -> Optional[User]:
        with self._session_factory() as session:
            user_orm = session.query(UserORM).filter(UserORM.kakao_id == kakao_id).first()
            if user_orm:
                return self._to_domain(user_orm)
            return None

    def create(self, user: User) -> User:
        with self._session_factory() as session:
            user_orm = UserORM(
                kakao_id=user.kakao_id,
                email=user.email,
                nickname=user.nickname,
                profile_image=user.profile_image
            )
            session.add(user_orm)
            session.commit()
            session.refresh(user_orm)
            return self._to_domain(user_orm)

    def update(self, user: User) -> User:
        with self._session_factory() as session:
            user_orm = session.query(UserORM).filter(UserORM.id == user.id).first()
            if user_orm:
                user_orm.email = user.email
                user_orm.nickname = user.nickname
                user_orm.profile_image = user.profile_image
                session.commit()
                session.refresh(user_orm)
                return self._to_domain(user_orm)
            raise ValueError(f"User with id {user.id} not found")

    def delete(self, user_id: int) -> bool:
        with self._session_factory() as session:
            user_orm = session.query(UserORM).filter(UserORM.id == user_id).first()
            if user_orm:
                session.delete(user_orm)
                session.commit()
                return True
            return False

    def _to_domain(self, user_orm: UserORM) -> User:
        return User(
            id=user_orm.id,
            kakao_id=user_orm.kakao_id,
            email=user_orm.email,
            nickname=user_orm.nickname,
            profile_image=user_orm.profile_image,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at
        )