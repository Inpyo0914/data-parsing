# 배포 가이드

Financial Data Parsing Service 배포 가이드

---

## 목차

1. [배포 방법 선택](#배포-방법-선택)
2. [Docker Compose 배포 (권장)](#docker-compose-배포-권장)
3. [수동 배포](#수동-배포)
4. [프로덕션 체크리스트](#프로덕션-체크리스트)
5. [모니터링](#모니터링)
6. [백업](#백업)
7. [업데이트](#업데이트)

---

## 배포 방법 선택

### Docker Compose (권장)
- **장점**: 간단한 설정, 일관된 환경, 쉬운 관리
- **단점**: Docker 필요
- **추천 대상**: 대부분의 경우

### 수동 배포
- **장점**: 세밀한 제어, 리소스 효율적
- **단점**: 복잡한 설정, 의존성 관리 필요
- **추천 대상**: 특별한 요구사항이 있는 경우

---

## Docker Compose 배포 (권장)

### 1. 사전 준비

```bash
# Docker 설치 확인
docker --version
docker-compose --version

# 설치되지 않은 경우:
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 프로젝트 설정

```bash
# 프로젝트 클론
cd /opt
sudo git clone https://github.com/Inpyo0914/data-parsing.git
cd data-parsing

# 환경 변수 설정
sudo cp .env.example .env
sudo nano .env
```

**.env 파일 필수 설정:**
```bash
# CRITICAL: 보안을 위해 반드시 변경!
FLASK_SECRET_KEY=$(openssl rand -hex 32)

# 프로덕션 설정
ENVIRONMENT=production
FLASK_DEBUG=False

# Elasticsearch (Docker 컨테이너 이름 사용)
ES_HOST=elasticsearch
ES_PORT=9200

# 스케줄러
COLLECTION_SCHEDULE=0 9,15,21 * * *
```

### 3. 배포 실행

```bash
# 프로덕션 모드로 실행
sudo docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
sudo docker-compose logs -f

# 특정 서비스 로그만 확인
sudo docker-compose logs -f web
```

### 4. 상태 확인

```bash
# 컨테이너 상태 확인
sudo docker-compose ps

# Elasticsearch 상태
curl http://localhost:9200

# 웹 애플리케이션 상태
curl http://localhost:5000

# 브라우저에서 확인
# http://your-server-ip:5000
```

### 5. 초기 데이터 수집

```bash
# 크롤러 컨테이너 실행
sudo docker-compose exec web python scripts/run_crawler.py

# 또는 스케줄러가 자동으로 수집 (설정된 시간에)
```

---

## 수동 배포

### 1. 시스템 사용자 생성

```bash
# 전용 사용자 생성
sudo useradd -r -s /bin/bash -d /opt/financial-data financial-data
sudo mkdir -p /opt/financial-data
sudo chown financial-data:financial-data /opt/financial-data
```

### 2. 애플리케이션 설치

```bash
# financial-data 사용자로 전환
sudo su - financial-data

# 프로젝트 클론
cd /opt/financial-data
git clone https://github.com/Inpyo0914/data-parsing.git app
cd app

# 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
nano .env  # 설정 수정

# 로그 디렉토리
mkdir -p logs
```

### 3. systemd 서비스 설정

#### Flask 웹 애플리케이션 서비스

```bash
# /etc/systemd/system/financial-data-web.service 파일 생성
sudo nano /etc/systemd/system/financial-data-web.service
```

```ini
[Unit]
Description=Financial Data Web Service
After=network.target elasticsearch.service
Requires=elasticsearch.service

[Service]
Type=simple
User=financial-data
Group=financial-data
WorkingDirectory=/opt/financial-data/app
Environment="PATH=/opt/financial-data/app/venv/bin"
Environment="PYTHONPATH=/opt/financial-data/app"
ExecStart=/opt/financial-data/app/venv/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    "src.web.app:create_app()"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 스케줄러 서비스

```bash
# /etc/systemd/system/financial-data-scheduler.service 파일 생성
sudo nano /etc/systemd/system/financial-data-scheduler.service
```

```ini
[Unit]
Description=Financial Data Crawler Scheduler
After=network.target elasticsearch.service
Requires=elasticsearch.service

[Service]
Type=simple
User=financial-data
Group=financial-data
WorkingDirectory=/opt/financial-data/app
Environment="PATH=/opt/financial-data/app/venv/bin"
Environment="PYTHONPATH=/opt/financial-data/app"
ExecStart=/opt/financial-data/app/venv/bin/python -m src.collector.scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. 서비스 시작

```bash
# 서비스 파일 reload
sudo systemctl daemon-reload

# 서비스 활성화 및 시작
sudo systemctl enable financial-data-web
sudo systemctl enable financial-data-scheduler
sudo systemctl start financial-data-web
sudo systemctl start financial-data-scheduler

# 상태 확인
sudo systemctl status financial-data-web
sudo systemctl status financial-data-scheduler

# 로그 확인
sudo journalctl -u financial-data-web -f
```

### 5. Nginx 리버스 프록시 설정 (선택사항)

```bash
# Nginx 설치
sudo apt install -y nginx

# 설정 파일 생성
sudo nano /etc/nginx/sites-available/financial-data
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 로그
    access_log /var/log/nginx/financial-data-access.log;
    error_log /var/log/nginx/financial-data-error.log;

    # Static files
    location /static {
        alias /opt/financial-data/app/src/web/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 크기 제한
    client_max_body_size 10M;
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/financial-data /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run
```

---

## 프로덕션 체크리스트

### 보안

- [ ] `FLASK_SECRET_KEY` 변경 완료
- [ ] `FLASK_DEBUG=False` 설정
- [ ] 방화벽 설정 (필요한 포트만 오픈)
- [ ] Elasticsearch 외부 접근 차단
- [ ] SSL/TLS 인증서 설정 (HTTPS)
- [ ] 정기적인 보안 업데이트

### 성능

- [ ] Gunicorn worker 수 조정 (CPU 코어 수 기준)
- [ ] Elasticsearch 힙 메모리 설정 (총 메모리의 50%)
- [ ] Nginx gzip 압축 활성화
- [ ] Static 파일 캐싱 설정

### 모니터링

- [ ] 로그 로테이션 설정
- [ ] 디스크 사용량 모니터링
- [ ] Elasticsearch 클러스터 상태 모니터링
- [ ] 애플리케이션 로그 모니터링

### 백업

- [ ] Elasticsearch 스냅샷 설정
- [ ] 설정 파일 백업
- [ ] 백업 복원 테스트

---

## 모니터링

### 로그 로테이션

```bash
# /etc/logrotate.d/financial-data 파일 생성
sudo nano /etc/logrotate.d/financial-data
```

```
/opt/financial-data/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 financial-data financial-data
    sharedscripts
    postrotate
        systemctl reload financial-data-web > /dev/null 2>&1 || true
    endscript
}
```

### Elasticsearch 모니터링

```bash
# 클러스터 상태
curl -X GET "localhost:9200/_cluster/health?pretty"

# 인덱스 통계
curl -X GET "localhost:9200/_cat/indices?v"

# 노드 상태
curl -X GET "localhost:9200/_cat/nodes?v"
```

### 디스크 사용량 모니터링

```bash
# 크론탭 추가
crontab -e

# 매일 디스크 사용량 체크
0 9 * * * df -h | grep '/opt' | awk '{if ($5 > 80) print "Disk usage high: " $5}' | mail -s "Disk Alert" admin@example.com
```

---

## 백업

### Elasticsearch 스냅샷

```bash
# 스냅샷 저장소 생성
curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/var/backups/elasticsearch"
  }
}
'

# 수동 스냅샷 생성
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_$(date +%Y%m%d)?wait_for_completion=true"

# 자동 스냅샷 (cron)
# 매일 새벽 2시에 백업
0 2 * * * curl -X PUT "localhost:9200/_snapshot/backup/snapshot_$(date +\%Y\%m\%d)?wait_for_completion=true"
```

### 설정 파일 백업

```bash
# 백업 스크립트
#!/bin/bash
BACKUP_DIR="/var/backups/financial-data"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# 설정 파일 백업
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /opt/financial-data/app/.env \
    /opt/financial-data/app/config/

# 오래된 백업 삭제 (30일 이상)
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +30 -delete
```

---

## 업데이트

### Docker Compose 환경

```bash
cd /opt/data-parsing

# 최신 코드 가져오기
sudo git pull origin main

# 컨테이너 재빌드 및 재시작
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
sudo docker-compose logs -f
```

### 수동 배포 환경

```bash
# financial-data 사용자로 전환
sudo su - financial-data
cd /opt/financial-data/app

# 최신 코드 가져오기
git pull origin main

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 서비스 재시작
exit  # financial-data 사용자에서 나가기
sudo systemctl restart financial-data-web
sudo systemctl restart financial-data-scheduler

# 상태 확인
sudo systemctl status financial-data-web
sudo systemctl status financial-data-scheduler
```

### 무중단 배포 (Blue-Green)

```bash
# 새 버전 디렉토리 생성
sudo cp -r /opt/financial-data/app /opt/financial-data/app-new

# 새 버전에서 업데이트
cd /opt/financial-data/app-new
sudo git pull
# ... 의존성 설치 등

# 새 버전 테스트
# ... 테스트 수행

# 심볼릭 링크 변경
sudo ln -sfn /opt/financial-data/app-new /opt/financial-data/current

# 서비스 재시작
sudo systemctl restart financial-data-web
```

---

## 문제 해결

### 서비스가 시작되지 않음

```bash
# 로그 확인
sudo journalctl -u financial-data-web -n 100

# 설정 파일 확인
sudo systemctl cat financial-data-web

# 수동으로 실행하여 에러 확인
cd /opt/financial-data/app
source venv/bin/activate
python -m src.web.app
```

### Elasticsearch 연결 실패

```bash
# Elasticsearch 상태 확인
sudo systemctl status elasticsearch

# 연결 테스트
curl -X GET "localhost:9200"

# 로그 확인
sudo journalctl -u elasticsearch -n 100
```

### 메모리 부족

```bash
# 메모리 사용량 확인
free -h

# Elasticsearch 힙 메모리 조정
sudo nano /etc/elasticsearch/jvm.options
# -Xms2g -> -Xms1g로 변경
# -Xmx2g -> -Xmx1g로 변경

sudo systemctl restart elasticsearch
```

---

**마지막 업데이트**: 2025-12-02
