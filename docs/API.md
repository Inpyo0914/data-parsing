# API 문서

Financial Data Parsing Service REST API Documentation

---

## 목차

1. [개요](#개요)
2. [인증](#인증)
3. [기본 URL](#기본-url)
4. [응답 형식](#응답-형식)
5. [에러 코드](#에러-코드)
6. [엔드포인트](#엔드포인트)

---

## 개요

Financial Data Parsing Service는 RESTful API를 제공하여 프로그래매틱하게 금융 뉴스 데이터에 접근할 수 있습니다.

### API 특징

- **JSON 응답**: 모든 API는 JSON 형식으로 응답
- **인증 불필요**: 현재 버전은 인증이 필요 없음 (내부 사용)
- **페이지네이션**: 대량 데이터는 페이지네이션 지원
- **필터링**: 카테고리, 날짜 등으로 필터링 가능

---

## 인증

현재 버전은 인증이 필요하지 않습니다. (소규모 내부 사용 목적)

> **Note**: 외부에 노출할 경우 인증 메커니즘 추가를 권장합니다.

---

## 기본 URL

```
http://localhost:5000/api
```

프로덕션 환경에서는 실제 도메인으로 변경:
```
https://your-domain.com/api
```

---

## 응답 형식

### 성공 응답

```json
{
  "success": true,
  "data": {
    // 실제 데이터
  },
  "meta": {
    // 메타데이터 (페이지네이션 등)
  }
}
```

### 에러 응답

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 설명"
  }
}
```

---

## 에러 코드

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | BAD_REQUEST | 잘못된 요청 파라미터 |
| 404 | NOT_FOUND | 요청한 리소스를 찾을 수 없음 |
| 500 | INTERNAL_ERROR | 서버 내부 오류 |

---

## 엔드포인트

### 1. 뉴스 목록 조회

최신 뉴스 목록을 조회합니다.

**Endpoint:**
```
GET /api/news
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | 페이지 번호 |
| per_page | integer | No | 20 | 페이지당 항목 수 (최대 100) |
| category | string | No | all | 카테고리 필터 (equities, bonds, forex, commodities) |
| sort | string | No | date_desc | 정렬 방식 (date_desc, date_asc) |

**Example Request:**

```bash
curl -X GET "http://localhost:5000/api/news?page=1&per_page=10&category=equities"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "news": [
      {
        "id": "https://www.financialjuice.com/equities/article-123",
        "title": "Stock Market Hits Record High",
        "summary": "Major indices reached all-time highs...",
        "category": "equities",
        "url": "https://www.financialjuice.com/equities/article-123",
        "published_date": "2025-12-02T10:30:00Z",
        "crawled_at": "2025-12-02T11:00:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "per_page": 10,
    "total_pages": 15
  }
}
```

---

### 2. 뉴스 검색

키워드로 뉴스를 검색합니다.

**Endpoint:**
```
GET /api/search
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| q | string | Yes | - | 검색 키워드 |
| page | integer | No | 1 | 페이지 번호 |
| per_page | integer | No | 20 | 페이지당 항목 수 |
| category | string | No | all | 카테고리 필터 |
| from_date | string | No | - | 시작 날짜 (YYYY-MM-DD) |
| to_date | string | No | - | 종료 날짜 (YYYY-MM-DD) |

**Example Request:**

```bash
curl -X GET "http://localhost:5000/api/search?q=market&category=equities&from_date=2025-12-01"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "query": "market",
    "results": [
      {
        "id": "https://www.financialjuice.com/equities/article-123",
        "title": "Market Analysis: Tech Stocks Rally",
        "summary": "Technology sector shows strong performance...",
        "category": "equities",
        "url": "https://www.financialjuice.com/equities/article-123",
        "published_date": "2025-12-02T09:00:00Z",
        "relevance_score": 8.5
      }
    ],
    "total": 45,
    "page": 1,
    "per_page": 20
  }
}
```

---

### 3. 뉴스 상세 조회

특정 뉴스의 상세 정보를 조회합니다.

**Endpoint:**
```
GET /api/news/:news_id
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| news_id | string | Yes | 뉴스 ID (URL 인코딩 필요) |

**Example Request:**

```bash
# URL을 URL-encode하여 사용
NEWS_ID=$(python -c "import urllib.parse; print(urllib.parse.quote('https://www.financialjuice.com/equities/article-123'))")
curl -X GET "http://localhost:5000/api/news/${NEWS_ID}"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "id": "https://www.financialjuice.com/equities/article-123",
    "title": "Stock Market Hits Record High",
    "summary": "Major indices reached all-time highs...",
    "content": "Full article content here...",
    "category": "equities",
    "author": "John Doe",
    "url": "https://www.financialjuice.com/equities/article-123",
    "published_date": "2025-12-02T10:30:00Z",
    "crawled_at": "2025-12-02T11:00:00Z",
    "tags": ["stocks", "market", "nasdaq"]
  }
}
```

**Error Response (404):**

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "News article not found"
  }
}
```

---

### 4. 통계 조회

뉴스 데이터 통계를 조회합니다.

**Endpoint:**
```
GET /api/stats
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| period | string | No | 7d | 통계 기간 (1d, 7d, 30d, all) |

**Example Request:**

```bash
curl -X GET "http://localhost:5000/api/stats?period=7d"
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "period": "7d",
    "total_articles": 450,
    "by_category": {
      "equities": 150,
      "bonds": 100,
      "forex": 120,
      "commodities": 80
    },
    "by_date": [
      {
        "date": "2025-12-02",
        "count": 75
      },
      {
        "date": "2025-12-01",
        "count": 68
      }
    ],
    "latest_crawl": "2025-12-02T15:00:00Z"
  }
}
```

---

## 사용 예시

### Python

```python
import requests

# 기본 URL
BASE_URL = "http://localhost:5000/api"

# 뉴스 목록 조회
response = requests.get(f"{BASE_URL}/news", params={
    "page": 1,
    "per_page": 10,
    "category": "equities"
})

if response.status_code == 200:
    data = response.json()
    if data["success"]:
        for news in data["data"]["news"]:
            print(f"- {news['title']}")
else:
    print(f"Error: {response.status_code}")

# 검색
response = requests.get(f"{BASE_URL}/search", params={
    "q": "market rally",
    "category": "equities"
})

data = response.json()
print(f"Found {data['data']['total']} results")
```

### JavaScript

```javascript
// 뉴스 목록 조회
async function fetchNews(category = 'all', page = 1) {
  const response = await fetch(
    `http://localhost:5000/api/news?category=${category}&page=${page}`
  );

  const data = await response.json();

  if (data.success) {
    return data.data.news;
  } else {
    throw new Error(data.error.message);
  }
}

// 사용 예
fetchNews('equities', 1)
  .then(news => {
    news.forEach(article => {
      console.log(article.title);
    });
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### cURL

```bash
# 뉴스 목록 조회
curl -X GET "http://localhost:5000/api/news?page=1&per_page=20&category=equities"

# 검색
curl -X GET "http://localhost:5000/api/search?q=technology&category=all"

# 통계
curl -X GET "http://localhost:5000/api/stats?period=7d"

# JSON 포맷팅 (jq 사용)
curl -X GET "http://localhost:5000/api/news?per_page=5" | jq '.data.news[] | {title, category, published_date}'
```

---

## Rate Limiting

현재 버전은 Rate Limiting이 없습니다.

> **Note**: 프로덕션 환경에서는 Rate Limiting 추가를 권장합니다.
> 예: 사용자당 분당 60회 요청 제한

---

## 페이지네이션

대량 데이터 조회 시 페이지네이션을 사용하세요.

**페이지네이션 파라미터:**
- `page`: 페이지 번호 (1부터 시작)
- `per_page`: 페이지당 항목 수 (최대 100)

**응답 메타데이터:**
```json
{
  "total": 500,
  "page": 2,
  "per_page": 20,
  "total_pages": 25
}
```

**다음 페이지 계산:**
```python
current_page = response['data']['page']
total_pages = response['data']['total_pages']

if current_page < total_pages:
    next_page = current_page + 1
    # 다음 페이지 요청
```

---

## 변경 로그

### v1.0.0 (2025-12-02)
- 초기 API 릴리스
- 뉴스 조회, 검색, 통계 엔드포인트 제공

---

**마지막 업데이트**: 2025-12-02
