# Todo-Grow Backend

FastAPI 기반의 Todo 애플리케이션 백엔드입니다.

## 개발 환경 설정

### 1. Docker로 실행

```bash
# Docker 컨테이너 실행
docker-compose up -d

# 백엔드 서버: http://localhost:8000
# MySQL: localhost:3306
```

### 2. 데이터베이스 초기화

```bash
# 방법 1: 기존 데이터 유지하면서 스키마만 적용
docker exec -i backend-db-1 mysql -u root -proot_password todo_grow < schema.sql

# 방법 2: 기존 데이터 완전 삭제 후 새로 시작 (개발 환경)
docker-compose down
rm -rf mysql_data/
docker-compose up -d
docker exec -i backend-db-1 mysql -u root -proot_password todo_grow < schema.sql

# 테이블 확인
docker exec -i backend-db-1 mysql -u root -proot_password todo_grow -e "SHOW TABLES;"
```

## 데이터베이스 구조

### todos 테이블
- `id`: 기본키
- `title`: 할일 제목
- `base_date`: 기준 날짜

### tasks 테이블
- `id`: 기본키
- `title`: 태스크 제목
- `points`: 포인트
- `todo_id`: 연결된 Todo ID (FK)
- `completed`: 완료 여부 (기본값: FALSE)
- `parent_id`: 부모 태스크 ID (서브태스크용, FK)

## API 문서

서버 실행 후 다음 주소에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주요 기능

- Todo 생성/조회/수정/삭제
- Task 생성/조회/수정/삭제
- Task 완료 상태 토글
- Subtask 지원 (parent_id 활용)