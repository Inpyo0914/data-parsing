# 사용자 가이드

Financial Data Parsing Service 사용자 가이드

---

## 목차

1. [시작하기](#시작하기)
2. [웹 인터페이스 사용](#웹-인터페이스-사용)
3. [데이터 수집 관리](#데이터-수집-관리)
4. [API 사용](#api-사용)
5. [고급 기능](#고급-기능)
6. [FAQ](#faq)

---

## 시작하기

### 첫 접속

1. 웹 브라우저를 열고 서비스 URL에 접속합니다:
   ```
   http://localhost:5000
   ```
   또는 프로덕션 서버의 주소

2. 홈페이지가 표시되면 설치가 정상적으로 완료된 것입니다.

### 초기 데이터 수집

처음 접속하면 데이터가 없을 수 있습니다. 데이터를 수집하는 방법:

**방법 1: 자동 스케줄링 (권장)**
- 스케줄러가 설정된 시간에 자동으로 데이터를 수집합니다
- 기본 설정: 매일 9시, 15시, 21시

**방법 2: 수동 실행**
```bash
# 터미널에서 실행
python scripts/run_crawler.py
```

---

## 웹 인터페이스 사용

### 1. 홈페이지

**기능:**
- 최신 금융 뉴스 목록 표시
- 카테고리별 탭 제공
- 날짜 역순으로 정렬

**사용법:**
1. 홈페이지 접속
2. 카테고리 탭 클릭 (전체, 증권, 채권, 외환, 원자재)
3. 뉴스 제목 클릭하여 상세 보기

**화면 구성:**
```
┌─────────────────────────────────────┐
│ Financial Data Service              │ <- 헤더
├─────────────────────────────────────┤
│ [전체] [증권] [채권] [외환] [원자재]  │ <- 카테고리 탭
├─────────────────────────────────────┤
│ 📰 Stock Market Hits Record High    │
│    2025-12-02 10:30                 │
│    Major indices reached...         │
├─────────────────────────────────────┤
│ 📰 Bond Yields Fall to New Low      │
│    2025-12-02 09:15                 │
│    Treasury yields drop...          │
└─────────────────────────────────────┘
```

### 2. 카테고리 필터링

**URL 구조:**
```
/category/<category_name>
```

**지원 카테고리:**
- `equities` - 증권
- `bonds` - 채권
- `forex` - 외환
- `commodities` - 원자재

**사용 예:**
```
http://localhost:5000/category/equities  <- 증권 뉴스만 표시
http://localhost:5000/category/bonds     <- 채권 뉴스만 표시
```

### 3. 검색 기능

**접근 방법:**
- 상단 메뉴의 "검색" 클릭
- URL: `/search`

**검색 옵션:**
- **키워드**: 제목, 요약, 본문에서 검색
- **카테고리**: 특정 카테고리로 제한
- **날짜 범위**: 시작일~종료일 지정 (선택사항)

**검색 예시:**
```
검색어: market rally
카테고리: 증권
날짜: 2025-12-01 ~ 2025-12-02

결과: 10건
```

**고급 검색:**
- 따옴표로 정확한 구문 검색: `"stock market"`
- AND 검색: `market AND technology`
- OR 검색: `bonds OR forex`

### 4. 뉴스 상세 보기

**표시 정보:**
- 뉴스 제목
- 발행 날짜 및 시간
- 카테고리
- 요약 (있는 경우)
- 본문 내용 (있는 경우)
- 태그 (있는 경우)
- 원문 링크

**기능:**
- 원문 보기: "Read Original" 버튼 클릭
- 뒤로 가기: "Back to list" 링크

### 5. 페이지네이션

- 한 페이지에 20개 항목 표시
- 하단에 페이지 번호 표시
- 이전/다음 버튼으로 이동

---

## 데이터 수집 관리

### 스케줄러 설정

**설정 파일:** `.env`

```bash
# Cron 형식으로 설정
COLLECTION_SCHEDULE=0 9,15,21 * * *
```

**Cron 형식 설명:**
```
분 시 일 월 요일
*  *  *  *  *

예시:
0 9,15,21 * * *    <- 매일 9시, 15시, 21시
0 */6 * * *        <- 6시간마다
0 0 * * *          <- 매일 자정
```

**일반적인 스케줄:**
- 하루 3회: `0 9,15,21 * * *`
- 4시간마다: `0 */4 * * *`
- 매시간: `0 * * * *`
- 평일 근무시간: `0 9-17 * * 1-5`

### 수동 데이터 수집

**방법 1: 스크립트 사용**
```bash
cd /path/to/data-parsing
python scripts/run_crawler.py
```

**방법 2: Python 코드**
```python
import asyncio
from src.collector.crawler import FinancialJuiceCrawler
from src.storage.indexer import NewsIndexer
from src.utils.config import Config

async def collect_data():
    config = Config()

    # 크롤링
    async with FinancialJuiceCrawler(config=config) as crawler:
        news_data = await crawler.crawl_all()

    # 저장
    indexer = NewsIndexer(config=config)
    indexer.setup_indices()
    stats = indexer.index_news_batch(news_data)

    print(f"Collected {stats['total_success']} articles")

asyncio.run(collect_data())
```

### 데이터 수집 로그 확인

```bash
# 애플리케이션 로그
tail -f logs/app.log

# 크롤러 로그만 필터링
tail -f logs/app.log | grep "crawler"

# systemd 로그 (서비스로 실행 시)
sudo journalctl -u financial-data-scheduler -f
```

---

## API 사용

### 기본 사용법

**뉴스 목록 조회:**
```bash
curl http://localhost:5000/api/news?per_page=10
```

**카테고리별 조회:**
```bash
curl http://localhost:5000/api/news?category=equities&per_page=5
```

**검색:**
```bash
curl "http://localhost:5000/api/search?q=market&category=equities"
```

**통계:**
```bash
curl http://localhost:5000/api/stats
```

### Python에서 API 사용

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 최신 뉴스 가져오기
def get_latest_news(category="all", limit=10):
    response = requests.get(f"{BASE_URL}/news", params={
        "category": category,
        "per_page": limit
    })

    data = response.json()
    if data["success"]:
        return data["data"]["news"]
    return []

# 사용 예
news = get_latest_news("equities", 5)
for article in news:
    print(f"- {article['title']}")
```

### JavaScript에서 API 사용

```javascript
async function getNews(category = 'all') {
  const response = await fetch(
    `http://localhost:5000/api/news?category=${category}&per_page=10`
  );

  const data = await response.json();

  if (data.success) {
    return data.data.news;
  }

  throw new Error(data.error.message);
}

// 사용 예
getNews('equities')
  .then(news => {
    news.forEach(article => {
      console.log(article.title);
    });
  });
```

상세한 API 문서는 [API.md](API.md)를 참조하세요.

---

## 고급 기능

### Elasticsearch 직접 쿼리

```bash
# 모든 뉴스 개수
curl -X GET "localhost:9200/financial_data/_count"

# 특정 키워드 검색
curl -X GET "localhost:9200/financial_data/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "title": "market"
    }
  },
  "size": 10
}
'

# 카테고리별 집계
curl -X GET "localhost:9200/financial_data/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category"
      }
    }
  }
}
'
```

### 데이터 내보내기

```python
from src.storage.es_client import ElasticsearchClient
import json

# Elasticsearch에서 모든 데이터 조회
client = ElasticsearchClient()
client.connect()

query = {"query": {"match_all": {}}}
results = client.search("financial_data", query, size=1000)

# JSON 파일로 저장
with open('export.json', 'w', encoding='utf-8') as f:
    for hit in results['hits']['hits']:
        json.dump(hit['_source'], f, ensure_ascii=False)
        f.write('\n')

print(f"Exported {len(results['hits']['hits'])} articles")
```

### 데이터 삭제

```bash
# 특정 인덱스 삭제
curl -X DELETE "localhost:9200/financial_data"

# 재생성
python -c "from src.storage.indexer import NewsIndexer; NewsIndexer().setup_indices()"

# 오래된 데이터 삭제 (30일 이상)
curl -X POST "localhost:9200/financial_data/_delete_by_query" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "crawled_at": {
        "lt": "now-30d"
      }
    }
  }
}
'
```

---

## FAQ

### Q1. 데이터가 수집되지 않아요

**A:** 다음을 확인하세요:
1. Elasticsearch가 실행 중인지 확인: `curl http://localhost:9200`
2. 스케줄러가 실행 중인지 확인: `systemctl status financial-data-scheduler`
3. 로그 확인: `tail -f logs/app.log`
4. 네트워크 연결 확인

### Q2. 검색이 동작하지 않아요

**A:**
- Elasticsearch 인덱스가 생성되었는지 확인: `curl localhost:9200/_cat/indices`
- 데이터가 있는지 확인: `curl localhost:9200/financial_data/_count`

### Q3. 웹 페이지가 느려요

**A:**
- Elasticsearch 메모리 설정 확인
- 데이터가 너무 많은 경우 오래된 데이터 삭제 고려
- 페이지당 표시 항목 수 줄이기

### Q4. 특정 카테고리만 수집하고 싶어요

**A:** `config/config.yaml` 또는 `.env`에서 수정:
```bash
# .env 파일에 없으면 코드 수정 필요
# src/collector/crawler.py의 categories 리스트 수정
```

### Q5. 데이터를 다른 시스템으로 연동하고 싶어요

**A:** API를 사용하거나 Elasticsearch에서 직접 읽기:
- REST API 사용 (권장)
- Elasticsearch 클라이언트 라이브러리 사용
- CSV/JSON으로 내보내기

### Q6. 보안이 걱정되요

**A:** 프로덕션 환경에서는:
- HTTPS 사용 (SSL/TLS)
- 방화벽으로 포트 제한
- Elasticsearch 외부 접근 차단
- 정기적인 보안 업데이트
- API에 인증 추가 (필요시)

### Q7. 백업은 어떻게 하나요?

**A:** [DEPLOYMENT.md](DEPLOYMENT.md)의 백업 섹션 참조:
- Elasticsearch 스냅샷 사용
- 정기적인 자동 백업 설정
- 백업 복원 테스트 필수

---

## 지원

문제가 해결되지 않으면:

1. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 참조
2. [GitHub Issues](https://github.com/Inpyo0914/data-parsing/issues) 검색
3. 새로운 이슈 등록

---

**마지막 업데이트**: 2025-12-02
