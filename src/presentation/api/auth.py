import os

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import inject, Provide
from src.containers import Container
from src.application.services.auth_service import AuthService
from src.domain.models.user import User

from urllib.parse import urlencode
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get(
    "/kakao",
    summary="카카오 OAuth 콜백 처리",
    description="""
    카카오 로그인 후 리다이렉트되는 콜백 엔드포인트입니다.

    **처리 과정:**
    1. 카카오로부터 받은 인증 코드로 액세스 토큰 요청
    2. 액세스 토큰으로 카카오 사용자 정보 조회
    3. 사용자 조회 또는 신규 사용자 생성
    4. JWT 토큰 생성
    5. 프론트엔드로 리다이렉트 (토큰 및 사용자 정보 포함)

    **리다이렉트 URL:**
    - 성공: `{FRONTEND_URL}/login?access_token={jwt}&user_id={id}&nickname={nickname}`
    - 실패: `{FRONTEND_URL}/login?error=auth_failed`
    """,
    responses={
        307: {"description": "프론트엔드로 리다이렉트"},
        500: {"description": "카카오 OAuth 설정이 누락되었거나 인증 처리 중 오류 발생"},
    },
)
@inject
async def kakao_login(
    code: str = Query(..., description="카카오로부터 받은 인증 코드"),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        # 환경변수에서 카카오 설정 가져오기
        client_id = os.getenv("KAKAO_CLIENT_ID")
        client_secret = os.getenv("KAKAO_CLIENT_SECRET")
        redirect_uri = os.getenv("KAKAO_REDIRECT_URI")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

        if not all([client_id, client_secret, redirect_uri]):
            raise HTTPException(
                status_code=500, detail="Kakao OAuth configuration missing"
            )

        # 카카오에서 액세스 토큰 가져오기
        access_token = await auth_service.get_access_token_from_code(
            code, client_id, client_secret, redirect_uri
        )

        if not access_token:
            raise HTTPException(
                status_code=400, detail="Failed to get access token from Kakao"
            )

        # 카카오 사용자 정보 가져오기
        kakao_user_info = await auth_service.get_kakao_user_info(access_token)

        if not kakao_user_info:
            raise HTTPException(
                status_code=400, detail="Failed to get user info from Kakao"
            )

        # 사용자 조회 또는 생성
        user = auth_service.get_or_create_user(kakao_user_info)

        # JWT 토큰 생성
        jwt_token = auth_service.create_access_token(user)

        # 프론트엔드로 리다이렉트 (토큰과 함께)
        params = {
            "access_token": jwt_token,
            "user_id": str(user.id),
            "nickname": user.nickname or "",
        }
        redirect_url = f"{frontend_url}/login?{urlencode(params)}"

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        error_url = f"{frontend_url}/login?error=auth_failed"
        return RedirectResponse(url=error_url)


@router.get(
    "/kakao/url",
    summary="카카오 로그인 URL 조회",
    description="""
    카카오 소셜 로그인을 위한 OAuth URL을 반환합니다.

    이 URL로 사용자를 리다이렉트하면 카카오 로그인 페이지로 이동합니다.
    로그인 완료 후 `/api/auth/kakao` 콜백 엔드포인트로 리다이렉트됩니다.
    """,
    responses={
        200: {
            "description": "카카오 로그인 URL 반환 성공",
            "content": {
                "application/json": {
                    "example": {
                        "login_url": "https://kauth.kakao.com/oauth/authorize?client_id=xxx&redirect_uri=xxx&response_type=code"
                    }
                }
            },
        },
        500: {"description": "카카오 OAuth 설정이 누락됨 (KAKAO_CLIENT_ID, KAKAO_REDIRECT_URI)"},
    },
)
def get_kakao_login_url():
    client_id = os.getenv("KAKAO_CLIENT_ID")
    redirect_uri = os.getenv("KAKAO_REDIRECT_URI")

    if not client_id or not redirect_uri:
        raise HTTPException(status_code=500, detail="Kakao OAuth configuration missing")

    kakao_login_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code"
    )

    return {"login_url": kakao_login_url}


# auto_error=False로 설정하면 토큰 없어도 에러 안남
security = HTTPBearer(auto_error=False)


@inject
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> User:
    """현재 인증된 사용자 가져오기"""
    # 로컬 개발 환경에서 인증 우회
    if os.getenv("DISABLE_AUTH", "false").lower() == "true":
        return User(
            id=int(os.getenv("DEV_USER_ID", 9999999)),
            kakao_id=os.getenv("DEV_KAKAO_ID", "dev_kakao_id"),
            nickname=os.getenv("DEV_NICKNAME", "개발자"),
        )

    # 프로덕션 환경에서는 토큰 필수
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = User(
        id=int(user_id),
        kakao_id=payload.get("kakao_id"),
        nickname=payload.get("nickname"),
    )
    return user


@router.delete(
    "/withdraw",
    summary="회원 탈퇴",
    description="""
    현재 로그인한 사용자의 계정을 삭제합니다.

    **처리 과정:**
    1. 카카오 계정 연결 해제 (카카오 ID가 있는 경우)
    2. 앱 내 사용자 데이터 삭제 (Todo, Task 등 모든 관련 데이터 포함)

    **주의:**
    - 이 작업은 되돌릴 수 없습니다
    - 모든 Todo와 Task 데이터가 함께 삭제됩니다
    - 카카오 연결 해제가 실패해도 앱 내 데이터는 삭제됩니다
    """,
    responses={
        200: {
            "description": "회원 탈퇴 성공",
            "content": {
                "application/json": {
                    "example": {"message": "User account deleted successfully"}
                }
            },
        },
        401: {"description": "인증되지 않은 사용자"},
        404: {"description": "사용자를 찾을 수 없음"},
        500: {"description": "회원 탈퇴 처리 중 오류 발생"},
    },
)
@inject
async def withdraw_user(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    try:
        # 카카오 계정 연결 해제
        kakao_unlink_success = (
            await auth_service.unlink_kakao_account(current_user.kakao_id)
            if current_user.kakao_id
            else True
        )

        # 앱 내 사용자 데이터 삭제
        user_delete_success = auth_service.delete_user(current_user.id)

        if not user_delete_success:
            raise HTTPException(status_code=404, detail="User not found")

        response_data = {"message": "User account deleted successfully"}
        if not kakao_unlink_success:
            response_data["warning"] = (
                "Kakao account unlink failed, but user data was deleted"
            )

        return response_data

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to delete user account")
