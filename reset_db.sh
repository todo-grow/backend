#!/bin/bash

# MySQL 데이터베이스 초기화 스크립트

echo "🔄 MySQL 데이터베이스 초기화를 시작합니다..."

# Docker 컨테이너 중지
echo "📦 Docker 컨테이너를 중지합니다..."
docker-compose down

# MySQL 데이터 디렉토리 삭제
echo "🗑️  MySQL 데이터 디렉토리를 삭제합니다..."
if [ -d "mysql_data" ]; then
    rm -rf mysql_data
    echo "✅ mysql_data 디렉토리가 삭제되었습니다."
else
    echo "ℹ️  mysql_data 디렉토리가 존재하지 않습니다."
fi

# Docker 컨테이너 재시작
echo "🚀 Docker 컨테이너를 재시작합니다..."
docker-compose up -d

echo "✅ MySQL 데이터베이스 초기화가 완료되었습니다!"
echo "📋 데이터베이스가 새로 생성되었으며, 모든 기존 데이터가 삭제되었습니다."