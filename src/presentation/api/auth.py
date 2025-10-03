from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dependency_injector.wiring import inject, Provide
from src.containers import Container
from src.application.services.auth_service import AuthService
from src.domain.models.user import User
import os
from urllib.parse import urlencode
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/kakao")
@inject
async def kakao_login(
    code: str = Query(...),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    """카카오 OAuth 콜백 처리"""
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


@router.get("/kakao/url")
def get_kakao_login_url():
    """카카오 로그인 URL 반환"""
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


security = HTTPBearer()


@inject
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> User:
    """현재 인증된 사용자 가져오기"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 사용자 조회 로직이 필요하다면 여기에 추가
    user = User(
        id=int(user_id),
        kakao_id=payload.get("kakao_id"),
        nickname=payload.get("nickname"),
    )
    return user


@router.delete("/withdraw")
@inject
async def withdraw_user(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
):
    """회원탈퇴"""
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
