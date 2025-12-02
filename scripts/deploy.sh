#!/bin/bash
# Financial Data Service - 배포 스크립트

set -e  # 에러 발생 시 중단

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 배포 타입 확인
DEPLOY_TYPE=${1:-"production"}

if [ "$DEPLOY_TYPE" != "production" ] && [ "$DEPLOY_TYPE" != "development" ]; then
    log_error "Invalid deploy type. Use 'production' or 'development'"
    echo "Usage: $0 [production|development]"
    exit 1
fi

log_info "Starting deployment (${DEPLOY_TYPE} mode)..."

# 1. 환경 확인
log_info "Step 1: Checking environment..."

# Docker 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose is not installed"
    exit 1
fi

log_info "✓ Docker and Docker Compose are installed"

# 2. .env 파일 확인
log_info "Step 2: Checking .env file..."

if [ ! -f .env ]; then
    log_warn ".env file not found. Creating from .env.example..."
    cp .env.example .env
    log_warn "Please edit .env file and run this script again"
    exit 1
fi

# FLASK_SECRET_KEY 확인
if grep -q "INSECURE-PLEASE-CHANGE-THIS-IMMEDIATELY" .env; then
    log_error "FLASK_SECRET_KEY is not changed in .env file!"
    log_error "Please generate a secure secret key:"
    echo "  python -c 'import secrets; print(secrets.token_hex(32))'"
    exit 1
fi

log_info "✓ .env file exists and configured"

# 3. 이전 컨테이너 중지 (있는 경우)
log_info "Step 3: Stopping existing containers..."

if [ "$DEPLOY_TYPE" == "production" ]; then
    docker-compose -f docker-compose.prod.yml down || true
else
    docker-compose down || true
fi

log_info "✓ Stopped existing containers"

# 4. 이미지 빌드
log_info "Step 4: Building Docker images..."

if [ "$DEPLOY_TYPE" == "production" ]; then
    docker-compose -f docker-compose.prod.yml build --no-cache
else
    docker-compose build
fi

log_info "✓ Built Docker images"

# 5. 컨테이너 시작
log_info "Step 5: Starting containers..."

if [ "$DEPLOY_TYPE" == "production" ]; then
    docker-compose -f docker-compose.prod.yml up -d
else
    docker-compose up -d
fi

log_info "✓ Started containers"

# 6. Elasticsearch가 준비될 때까지 대기
log_info "Step 6: Waiting for Elasticsearch to be ready..."

MAX_WAIT=60
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:9200 > /dev/null 2>&1; then
        log_info "✓ Elasticsearch is ready"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo -n "."
done

if [ $WAITED -ge $MAX_WAIT ]; then
    log_error "Elasticsearch did not start in time"
    docker-compose logs elasticsearch
    exit 1
fi

# 7. 인덱스 초기화 (처음 배포 시)
log_info "Step 7: Initializing Elasticsearch indices..."

if [ "$DEPLOY_TYPE" == "production" ]; then
    docker-compose -f docker-compose.prod.yml exec -T web python scripts/setup_es.py || log_warn "Indices may already exist"
else
    docker-compose exec -T web python scripts/setup_es.py || log_warn "Indices may already exist"
fi

log_info "✓ Indices initialized"

# 8. 상태 확인
log_info "Step 8: Checking service health..."

sleep 5  # 서비스 시작 대기

# Elasticsearch 상태
ES_STATUS=$(curl -s http://localhost:9200/_cluster/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
log_info "Elasticsearch status: $ES_STATUS"

# Web 서비스 상태
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    log_info "✓ Web service is running"
else
    log_warn "Web service is not responding yet"
fi

# 9. 컨테이너 상태 출력
log_info "Step 9: Container status..."

if [ "$DEPLOY_TYPE" == "production" ]; then
    docker-compose -f docker-compose.prod.yml ps
else
    docker-compose ps
fi

# 완료
echo ""
log_info "=========================================="
log_info "Deployment completed successfully!"
log_info "=========================================="
log_info "Web Interface: http://localhost:5000"
log_info "Elasticsearch: http://localhost:9200"
echo ""
log_info "View logs:"
if [ "$DEPLOY_TYPE" == "production" ]; then
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
else
    echo "  docker-compose logs -f"
fi
echo ""
log_info "Stop services:"
if [ "$DEPLOY_TYPE" == "production" ]; then
    echo "  docker-compose -f docker-compose.prod.yml down"
else
    echo "  docker-compose down"
fi
echo ""
