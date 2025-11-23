from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get(
    "/health",
    summary="헬스 체크",
    description="""
    서버의 상태를 확인합니다.

    **용도:**
    - 서버가 정상적으로 실행 중인지 확인
    - 로드 밸런서나 모니터링 시스템에서 사용
    - 인증이 필요 없는 공개 엔드포인트

    **응답:**
    - 서버가 정상 작동 중이면 `{"status": "ok"}` 반환
    """,
    responses={
        200: {
            "description": "서버 정상 작동",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            },
        },
    },
)
def health_check():
    return {"status": "ok"}
