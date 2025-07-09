# Database Migrations

간단한 SQL 마이그레이션 파일들입니다.

## 마이그레이션 실행

```bash
# 마이그레이션 파일 실행
docker exec -i backend-db-1 mysql -u root -proot_password todo_grow < migrations/파일명.sql

# 테이블 구조 확인
docker exec -i backend-db-1 mysql -u root -proot_password todo_grow -e "DESCRIBE 테이블명;"

# 전체 테이블 목록 확인
docker exec -i backend-db-1 mysql -u root -proot_password todo_grow -e "SHOW TABLES;"
```

## 새 마이그레이션 파일 생성 규칙

- 파일명: `{순번:03d}_{설명}.sql` 형식
- 순번은 3자리 숫자로 패딩 (001, 002, 003...)
- 설명은 영어 소문자와 언더스코어 사용