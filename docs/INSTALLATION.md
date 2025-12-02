# 설치 가이드

Financial Data Parsing & Display Service 설치 가이드

---

## 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [Elasticsearch 설치](#elasticsearch-설치)
3. [Python 환경 설정](#python-환경-설정)
4. [애플리케이션 설치](#애플리케이션-설치)
5. [설정](#설정)
6. [초기화](#초기화)
7. [검증](#검증)

---

## 시스템 요구사항

### 최소 요구사항

- **OS**: Linux (Ubuntu 20.04+, CentOS 7+) 또는 macOS 10.15+
- **CPU**: 2 cores
- **RAM**: 4GB (Elasticsearch 포함 시 8GB 권장)
- **Disk**: 10GB 여유 공간
- **Python**: 3.8 이상
- **Elasticsearch**: 7.17.x

### 권장 사양

- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 50GB SSD
- **Python**: 3.10+

---

## Elasticsearch 설치

### Ubuntu/Debian

```bash
# 1. Java 설치 (Elasticsearch 7.x는 Java 11 필요)
sudo apt update
sudo apt install -y openjdk-11-jdk

# 2. Elasticsearch GPG 키 추가
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -

# 3. Elasticsearch 저장소 추가
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list

# 4. Elasticsearch 설치
sudo apt update
sudo apt install -y elasticsearch=7.17.16

# 5. Elasticsearch 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# 6. 상태 확인
sudo systemctl status elasticsearch

# 7. 연결 테스트
curl -X GET "localhost:9200"
```

### CentOS/RHEL

```bash
# 1. Java 설치
sudo yum install -y java-11-openjdk

# 2. Elasticsearch 저장소 추가
sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch

cat <<EOF | sudo tee /etc/yum.repos.d/elasticsearch.repo
[elasticsearch-7.x]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF

# 3. Elasticsearch 설치
sudo yum install -y elasticsearch-7.17.16

# 4. 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

# 5. 연결 테스트
curl -X GET "localhost:9200"
```

### macOS (Homebrew)

```bash
# 1. Homebrew로 Elasticsearch 설치
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full@7.17

# 2. 서비스 시작
brew services start elastic/tap/elasticsearch-full@7.17

# 3. 연결 테스트
curl -X GET "localhost:9200"
```

### Docker (가장 간단)

```bash
# Elasticsearch 7.17 실행
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:7.17.16

# 상태 확인
curl -X GET "localhost:9200"
```

### Elasticsearch 설정 조정 (선택사항)

```bash
# /etc/elasticsearch/elasticsearch.yml 편집
sudo nano /etc/elasticsearch/elasticsearch.yml

# 추가/변경할 설정:
network.host: 0.0.0.0
http.port: 9200
cluster.name: financial-data-cluster
node.name: financial-data-node-1

# 서비스 재시작
sudo systemctl restart elasticsearch
```

---

## Python 환경 설정

### Python 3.8+ 설치

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

#### CentOS/RHEL

```bash
sudo yum install -y python3 python3-pip
```

#### macOS

```bash
# Homebrew 사용
brew install python@3.10
```

### Python 버전 확인

```bash
python3 --version
# Python 3.8.0 이상이어야 함
```

---

## 애플리케이션 설치

### 1. 저장소 클론

```bash
git clone https://github.com/Inpyo0914/data-parsing.git
cd data-parsing
```

### 2. 가상환경 생성

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
# 프로덕션 의존성
pip install -r requirements.txt

# 개발 의존성도 설치하려면 (테스트, 린팅 등)
pip install -r requirements-dev.txt
```

### 4. 설치 확인

```bash
# Python 모듈 임포트 테스트
python -c "from src.collector import crawler; from src.storage import es_client; from src.web import app; print('✓ All modules imported successfully')"
```

---

## 설정

### 1. 환경 변수 파일 생성

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
nano .env
```

### 2. 필수 설정 항목

**.env 파일에서 반드시 변경해야 할 항목:**

```bash
# ⚠️ CRITICAL: Flask Secret Key 변경 필수!
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Elasticsearch 설정 (기본값 확인/수정)
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_PREFIX=financial_data

# Flask 설정
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False  # 프로덕션에서는 반드시 False

# 크롤러 설정
CRAWLER_DELAY=2  # 요청 간 지연 (초)
CRAWLER_TIMEOUT=30
CRAWLER_MAX_RETRIES=3

# 스케줄러 설정 (Cron 형식)
COLLECTION_SCHEDULE=0 9,15,21 * * *  # 매일 9시, 15시, 21시
```

### 3. 로그 디렉토리 생성

```bash
mkdir -p logs
chmod 755 logs
```

---

## 초기화

### 1. Elasticsearch 인덱스 생성

```bash
# Python으로 인덱스 초기화
python -c "
from src.storage.indexer import NewsIndexer
from src.utils.config import Config

config = Config()
indexer = NewsIndexer(config=config)
indexer.setup_indices()
print('✓ Elasticsearch indices created successfully')
"
```

또는 스크립트 사용:

```bash
python scripts/setup_es.py
```

### 2. 초기 데이터 수집 (선택사항)

```bash
# 첫 데이터 수집 실행
python scripts/run_crawler.py
```

---

## 검증

### 1. Elasticsearch 연결 확인

```bash
# ES 연결 테스트
python -c "
from src.storage.es_client import ElasticsearchClient
from src.utils.config import Config

config = Config()
client = ElasticsearchClient(config=config)
client.connect()
if client.is_connected():
    print('✓ Elasticsearch connection successful')
    info = client.client.info()
    print(f'  Version: {info[\"version\"][\"number\"]}')
else:
    print('✗ Elasticsearch connection failed')
"
```

### 2. 웹 애플리케이션 실행 테스트

```bash
# Flask 개발 서버 시작
python -m flask --app src.web.app run --host=0.0.0.0 --port=5000

# 별도 터미널에서 테스트
curl http://localhost:5000
```

### 3. 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 통합 테스트만 실행
pytest tests/integration/ -v
```

### 4. 크롤러 테스트

```bash
# 크롤러 동작 확인 (dry-run)
python -c "
import asyncio
from src.collector.crawler import FinancialJuiceCrawler
from src.utils.config import Config

async def test():
    config = Config()
    async with FinancialJuiceCrawler(config=config) as crawler:
        # 하나의 카테고리만 테스트
        result = await crawler.crawl_category('equities')
        print(f'✓ Crawled {len(result)} articles from equities category')
        if result:
            print(f'  Sample: {result[0].get(\"title\", \"N/A\")}')

asyncio.run(test())
"
```

---

## 문제 해결

### Elasticsearch가 시작되지 않음

```bash
# 로그 확인
sudo journalctl -u elasticsearch -f

# 일반적인 문제:
# 1. 메모리 부족 -> /etc/elasticsearch/jvm.options에서 힙 크기 조정
# 2. 포트 충돌 -> 9200 포트 사용 확인: lsof -i :9200
# 3. 권한 문제 -> 데이터 디렉토리 권한 확인
```

### Python 의존성 설치 실패

```bash
# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 시스템 패키지 설치 (Ubuntu/Debian)
sudo apt install -y python3-dev build-essential libxml2-dev libxslt1-dev zlib1g-dev

# 의존성 재설치
pip install -r requirements.txt --no-cache-dir
```

### 가상환경 활성화 문제

```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 다음 단계

설치가 완료되었으면:

1. **배포 가이드** 참조: [DEPLOYMENT.md](DEPLOYMENT.md)
2. **사용자 가이드** 참조: [USER_GUIDE.md](USER_GUIDE.md)
3. **API 문서** 참조: [API.md](API.md)

---

**마지막 업데이트**: 2025-12-02
