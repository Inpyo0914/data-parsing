# 트러블슈팅 가이드

Financial Data Parsing Service 문제 해결 가이드

---

## 목차

1. [일반적인 문제](#일반적인-문제)
2. [Elasticsearch 관련](#elasticsearch-관련)
3. [크롤러 관련](#크롤러-관련)
4. [웹 애플리케이션 관련](#웹-애플리케이션-관련)
5. [성능 문제](#성능-문제)
6. [데이터 문제](#데이터-문제)

---

## 일반적인 문제

### 서비스가 시작되지 않음

**증상:**
```bash
$ systemctl start financial-data-web
Job for financial-data-web.service failed
```

**해결 방법:**

1. **로그 확인:**
```bash
sudo journalctl -u financial-data-web -n 50
```

2. **포트 충돌 확인:**
```bash
# 5000번 포트 사용 중인 프로세스 확인
sudo lsof -i :5000

# 프로세스 종료
sudo kill -9 <PID>
```

3. **권한 확인:**
```bash
# 로그 디렉토리 권한
ls -la /opt/financial-data/app/logs

# 소유자 변경
sudo chown -R financial-data:financial-data /opt/financial-data/app
```

4. **의존성 확인:**
```bash
# 가상환경에서 모듈 임포트 테스트
cd /opt/financial-data/app
source venv/bin/activate
python -c "from src.web.app import create_app; print('OK')"
```

### 환경 변수가 로드되지 않음

**증상:**
```
KeyError: 'FLASK_SECRET_KEY'
```

**해결 방법:**

1. **.env 파일 위치 확인:**
```bash
ls -la /opt/financial-data/app/.env
```

2. **.env 파일 내용 확인:**
```bash
cat .env | grep FLASK_SECRET_KEY
```

3. **파일 권한 확인:**
```bash
chmod 600 .env
chown financial-data:financial-data .env
```

---

## Elasticsearch 관련

### Elasticsearch 연결 실패

**증상:**
```
elasticsearch.exceptions.ConnectionError: Connection refused
```

**해결 방법:**

1. **Elasticsearch 상태 확인:**
```bash
sudo systemctl status elasticsearch

# 실행 중이 아니면 시작
sudo systemctl start elasticsearch
```

2. **연결 테스트:**
```bash
curl -X GET "localhost:9200"

# 정상 응답 예시:
# {
#   "name" : "node-1",
#   "cluster_name" : "elasticsearch",
#   ...
# }
```

3. **네트워크 설정 확인:**
```bash
# Elasticsearch 설정 확인
sudo nano /etc/elasticsearch/elasticsearch.yml

# 확인할 항목:
# network.host: 0.0.0.0
# http.port: 9200
```

4. **방화벽 확인:**
```bash
# 9200 포트 오픈 확인
sudo ufw status

# 포트 열기 (필요시)
sudo ufw allow 9200/tcp
```

### Elasticsearch 메모리 부족

**증상:**
```
java.lang.OutOfMemoryError: Java heap space
```

**해결 방법:**

1. **힙 메모리 설정 확인:**
```bash
sudo nano /etc/elasticsearch/jvm.options

# 힙 크기 조정 (총 메모리의 50% 권장)
-Xms2g  # 초기 힙 크기
-Xmx2g  # 최대 힙 크기
```

2. **Elasticsearch 재시작:**
```bash
sudo systemctl restart elasticsearch
```

3. **메모리 사용량 모니터링:**
```bash
# 노드 통계
curl -X GET "localhost:9200/_nodes/stats?pretty"

# JVM 힙 사용량
curl -X GET "localhost:9200/_cat/nodes?v&h=heap.percent,ram.percent"
```

### 인덱스 생성 실패

**증상:**
```
elasticsearch.exceptions.RequestError: index_already_exists_exception
```

**해결 방법:**

1. **기존 인덱스 확인:**
```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

2. **인덱스 삭제 후 재생성:**
```bash
# 인덱스 삭제
curl -X DELETE "localhost:9200/financial_data"

# 재생성
python -c "from src.storage.indexer import NewsIndexer; NewsIndexer().setup_indices()"
```

---

## 크롤러 관련

### 크롤링 실패

**증상:**
```
FetchException: Failed to fetch URL
```

**해결 방법:**

1. **네트워크 연결 확인:**
```bash
# FinancialJuice 접속 테스트
curl -I https://www.financialjuice.com

# DNS 확인
nslookup www.financialjuice.com
```

2. **User-Agent 설정 확인:**
```bash
# .env 파일 확인
grep CRAWLER_USER_AGENT .env

# 변경 후 서비스 재시작
```

3. **Rate Limiting 조정:**
```bash
# .env에서 지연 시간 늘리기
CRAWLER_DELAY=5  # 2초 -> 5초로 변경

# 서비스 재시작
sudo systemctl restart financial-data-scheduler
```

4. **타임아웃 증가:**
```bash
# .env 설정
CRAWLER_TIMEOUT=60  # 30초 -> 60초로 변경
```

### HTML 파싱 오류

**증상:**
```
AttributeError: 'NoneType' object has no attribute 'text'
```

**해결 방법:**

1. **웹사이트 구조 변경 확인:**
```bash
# 현재 HTML 구조 확인
curl https://www.financialjuice.com/equities > test.html
cat test.html
```

2. **파서 로직 확인:**
```python
# src/collector/parser.py 확인
# 선택자(selector)가 변경되었는지 확인
```

3. **테스트 실행:**
```bash
# 파서 단위 테스트
pytest tests/unit/test_parser.py -v
```

### 중복 데이터 수집

**증상:**
동일한 뉴스가 여러 번 저장됨

**해결 방법:**

1. **중복 체크 로직 확인:**
```python
# src/storage/indexer.py에서 skip_duplicates=True 확인
stats = indexer.index_news_batch(news_data, skip_duplicates=True)
```

2. **기존 중복 데이터 삭제:**
```bash
# Elasticsearch에서 중복 제거 쿼리
# (수동으로 확인 후 삭제)
```

---

## 웹 애플리케이션 관련

### 500 Internal Server Error

**증상:**
웹 페이지 접속 시 500 에러

**해결 방법:**

1. **애플리케이션 로그 확인:**
```bash
tail -f logs/app.log
tail -f logs/error.log  # Gunicorn 사용 시
```

2. **Elasticsearch 연결 확인:**
```bash
python -c "
from src.storage.es_client import ElasticsearchClient
client = ElasticsearchClient()
print('Connected:', client.connect())
"
```

3. **디버그 모드로 실행:**
```bash
FLASK_DEBUG=True python -m flask --app src.web.app run
```

### 검색이 작동하지 않음

**증상:**
검색 결과가 항상 0건

**해결 방법:**

1. **데이터 존재 확인:**
```bash
curl -X GET "localhost:9200/financial_data/_count"
```

2. **검색 쿼리 테스트:**
```bash
curl -X GET "localhost:9200/financial_data/_search?q=test"
```

3. **인덱스 매핑 확인:**
```bash
curl -X GET "localhost:9200/financial_data/_mapping?pretty"
```

### Static 파일이 로드되지 않음

**증상:**
CSS/JS 파일이 404 Not Found

**해결 방법:**

1. **파일 존재 확인:**
```bash
ls -la src/web/static/css/
ls -la src/web/static/js/
```

2. **Flask static 설정 확인:**
```python
# src/web/app.py
app = Flask(__name__,
            static_folder='static',
            static_url_path='/static')
```

3. **Nginx 사용 시 설정 확인:**
```nginx
location /static {
    alias /opt/financial-data/app/src/web/static;
}
```

---

## 성능 문제

### 웹 페이지 로딩이 느림

**증상:**
페이지 로드에 10초 이상 소요

**해결 방법:**

1. **Elasticsearch 쿼리 최적화:**
```python
# 페이지당 항목 수 줄이기
per_page = 10  # 20 -> 10으로 변경
```

2. **인덱스 크기 확인:**
```bash
curl -X GET "localhost:9200/_cat/indices?v&s=store.size:desc"
```

3. **오래된 데이터 삭제:**
```bash
# 90일 이상 데이터 삭제
curl -X POST "localhost:9200/financial_data/_delete_by_query" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "crawled_at": {
        "lt": "now-90d"
      }
    }
  }
}
'
```

4. **Gunicorn worker 수 조정:**
```ini
# systemd 서비스 파일
ExecStart=/path/to/gunicorn --workers 8 ...  # 4 -> 8로 증가
```

### 크롤링이 느림

**증상:**
한 번 크롤링에 1시간 이상 소요

**해결 방법:**

1. **동시 요청 수 확인:**
```python
# src/collector/crawler.py
# asyncio.gather로 병렬 처리 확인
```

2. **Rate Limiting 완화:**
```bash
# .env
CRAWLER_DELAY=1  # 2초 -> 1초로 변경 (주의: 서버 부담 증가)
```

3. **타임아웃 감소:**
```bash
CRAWLER_TIMEOUT=15  # 30초 -> 15초로 변경
```

---

## 데이터 문제

### 데이터가 수집되지 않음

**증상:**
스케줄러가 실행되지만 새 데이터가 없음

**해결 방법:**

1. **스케줄러 로그 확인:**
```bash
sudo journalctl -u financial-data-scheduler -f
```

2. **수동 크롤링 테스트:**
```bash
python scripts/run_crawler.py
```

3. **웹사이트 접근 확인:**
```bash
curl -I https://www.financialjuice.com/equities
```

### 데이터 손실

**증상:**
이전에 있던 데이터가 사라짐

**해결 방법:**

1. **Elasticsearch 백업 복원:**
```bash
# 스냅샷 목록 확인
curl -X GET "localhost:9200/_snapshot/backup/_all?pretty"

# 복원
curl -X POST "localhost:9200/_snapshot/backup/snapshot_20251201/_restore"
```

2. **인덱스 확인:**
```bash
curl -X GET "localhost:9200/_cat/indices?v"
```

3. **디스크 공간 확인:**
```bash
df -h
```

---

## 진단 스크립트

### 종합 상태 체크

```bash
#!/bin/bash
echo "=== Financial Data Service Health Check ==="

# Elasticsearch
echo -n "Elasticsearch: "
curl -s localhost:9200 > /dev/null && echo "OK" || echo "FAIL"

# Web Service
echo -n "Web Service: "
curl -s localhost:5000 > /dev/null && echo "OK" || echo "FAIL"

# Disk Space
echo "Disk Usage:"
df -h | grep -E "Filesystem|/opt"

# Memory
echo "Memory Usage:"
free -h

# Services
echo "Service Status:"
systemctl is-active elasticsearch
systemctl is-active financial-data-web
systemctl is-active financial-data-scheduler

# Data Count
echo -n "Total Articles: "
curl -s localhost:9200/financial_data/_count | grep -o '"count":[0-9]*' | cut -d: -f2
```

---

## 추가 지원

문제가 해결되지 않으면:

1. **로그 수집:**
```bash
# 모든 관련 로그 수집
sudo journalctl -u elasticsearch > es.log
sudo journalctl -u financial-data-web > web.log
sudo journalctl -u financial-data-scheduler > scheduler.log
tail -n 1000 logs/app.log > app.log
```

2. **GitHub Issue 등록:**
- https://github.com/Inpyo0914/data-parsing/issues
- 로그 파일 첨부 (민감 정보 제거 후)
- 환경 정보 포함 (OS, Python 버전, Elasticsearch 버전)

---

**마지막 업데이트**: 2025-12-02
