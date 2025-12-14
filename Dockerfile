# Python 3.12 slim 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY flask_news_app.py .

# 포트 설정
ENV PORT=8080
EXPOSE 8080

# gunicorn으로 Flask 앱 실행
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 flask_news_app:app
