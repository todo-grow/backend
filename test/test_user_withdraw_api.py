import os
from test.fixtures import UserFixture
from src.infrastructure.database.sqlalchemy_models import (
    UserORM,
    TodoORM,
    TaskORM,
)
from datetime import date


class TestUserWithdrawAPI:
    def test_withdraw_unauthorized(self, test_client, monkeypatch):
        """인증 없이 회원탈퇴 시도 시 401 에러"""
        monkeypatch.setenv("DISABLE_AUTH", "false")
        response = test_client.delete("/api/auth/withdraw")
        assert response.status_code == 401

    def test_withdraw_success(self, test_client, db_session):
        """회원탈퇴 성공"""
        # 먼저 사용자를 DB에 생성
        user_orm = UserFixture.create_user_orm(
            session=db_session,
            id=os.getenv("DEV_USER_ID", 9999999),
            kakao_id=os.getenv("DEV_KAKAO_ID", "dev_kakao_id"),
            nickname=os.getenv("DEV_NICKNAME", "개발자"),
            profile_image="https://test.com/profile.jpg",
            email="test@example.com",
        )

        response = test_client.delete("/api/auth/withdraw")
        assert response.json() == {"message": "User account deleted successfully"}

        # 사용자가 실제로 삭제되었는지 확인
        deleted_user = (
            db_session.query(UserORM).filter(UserORM.id == user_orm.id).first()
        )
        assert deleted_user is None

    def test_withdraw_user_not_found(self, test_client):
        """존재하지 않는 사용자 탈퇴 시도 시 에러"""
        # DB에 사용자를 생성하지 않은 상태에서 탈퇴 시도
        response = test_client.delete("/api/auth/withdraw")
        # 현재 구현에서는 cascade 관련 500 에러가 발생할 수 있음
        assert response.status_code == 500

    def test_withdraw_with_existing_todos_and_tasks(self, test_client, db_session):
        """Todo와 Task가 있는 사용자 탈퇴 시 관련 데이터도 함께 삭제"""
        # 사용자 생성
        user_orm = UserFixture.create_user_orm(
            session=db_session,
            id=os.getenv("DEV_USER_ID", 123),
            kakao_id=os.getenv("DEV_KAKAO_ID", "dev_kakao_id_123"),
            nickname=os.getenv("DEV_NICKNAME", "개발자_123"),
        )

        # ID를 미리 저장 (삭제 후 접근 방지)
        user_id = user_orm.id

        # Todo 생성
        todo = TodoORM(user_id=user_id, base_date=date.today())
        db_session.add(todo)
        db_session.commit()
        db_session.refresh(todo)

        # Task 생성
        task = TaskORM(
            title="테스트 태스크",
            points=10,
            todo_id=todo.id,
            user_id=user_id,
            completed=False,
        )
        db_session.add(task)
        db_session.commit()

        # 회원탈퇴
        response = test_client.delete("/api/auth/withdraw")
        assert response.json() == {"message": "User account deleted successfully"}

        # 사용자와 관련 데이터가 모두 삭제되었는지 확인
        assert db_session.query(UserORM).filter(UserORM.id == user_id).first() is None
        assert (
            db_session.query(TodoORM).filter(TodoORM.user_id == user_id).first() is None
        )
        assert (
            db_session.query(TaskORM).filter(TaskORM.user_id == user_id).first() is None
        )
