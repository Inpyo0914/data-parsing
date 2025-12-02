# Financial Data Parsing Service - Dockerfile
FROM python:3.10-slim

# 메타데이터
LABEL maintainer="Inpyo0914"
LABEL description="Financial Data Parsing & Display Service"
LABEL version="1.0.0"

# 환경 변수
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 로그 디렉토리 생성
RUN mkdir -p /app/logs && chmod 755 /app/logs

# 비root 사용자 생성
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 사용자 전환
USER appuser

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 포트 노출
EXPOSE 5000

# 기본 실행 명령
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "src.web.app:create_app()"]
