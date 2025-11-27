# Development Plan - Financial Data Parsing Service

**프로젝트**: FinancialJuice 크롤링 & 전시 서비스
**언어**: Python 3.8+
**작성일**: 2025-11-27
**상태**: 초기 계획 단계

---

## 목차

1. [개발 환경 구성](#1-개발-환경-구성)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [Phase별 개발 계획](#3-phase별-개발-계획)
4. [모듈별 상세 설계](#4-모듈별-상세-설계)
5. [데이터 모델](#5-데이터-모델)
6. [의존성 관리](#6-의존성-관리)
7. [테스트 전략](#7-테스트-전략)
8. [배포 및 운영](#8-배포-및-운영)

---

## 1. 개발 환경 구성

### 1.1 필수 요구사항

```bash
# Python 버전
Python 3.8 이상 (권장: 3.10+)

# Elasticsearch
Elasticsearch 7.17.x (최신 7.x 버전)

# 시스템 패키지
- pip
- virtualenv 또는 venv
```

### 1.2 초기 설정 순서

```bash
# 1. 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 기본 디렉토리 구조 생성
mkdir -p src/{collector,storage,web/{templates,static},utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p config
mkdir -p logs

# 3. Git 설정
echo "venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "logs/" >> .gitignore

# 4. 환경 변수 템플릿 생성
cp .env.example .env
```

---

## 2. 프로젝트 구조

### 2.1 전체 디렉토리 구조

```
data-parsing/
├── src/
│   ├── __init__.py
│   ├── collector/              # 웹 크롤링 모듈
│   │   ├── __init__.py
│   │   ├── crawler.py         # 크롤러 메인 로직
│   │   ├── parser.py          # HTML 파싱 로직
│   │   ├── scheduler.py       # 스케줄링
│   │   └── rate_limiter.py    # Rate limiting
│   ├── storage/                # Elasticsearch 연동
│   │   ├── __init__.py
│   │   ├── es_client.py       # ES 클라이언트
│   │   ├── indexer.py         # 인덱싱 로직
│   │   └── mappings.py        # 인덱스 매핑 정의
│   ├── web/                    # Flask 웹 앱
│   │   ├── __init__.py
│   │   ├── app.py             # Flask 앱 설정
│   │   ├── routes.py          # 라우트 정의
│   │   ├── views.py           # 뷰 로직
│   │   ├── templates/         # Jinja2 템플릿
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── search.html
│   │   │   └── detail.html
│   │   └── static/            # CSS, JS
│   │       ├── css/
│   │       └── js/
│   └── utils/                  # 공통 유틸리티
│       ├── __init__.py
│       ├── config.py          # 설정 관리
│       ├── logger.py          # 로깅 설정
│       └── helpers.py         # 헬퍼 함수
├── tests/
│   ├── __init__.py
│   ├── unit/                   # 단위 테스트
│   │   ├── test_crawler.py
│   │   ├── test_parser.py
│   │   └── test_es_client.py
│   ├── integration/            # 통합 테스트
│   │   └── test_full_pipeline.py
│   └── fixtures/               # 테스트 데이터
│       ├── sample.html
│       └── sample_data.json
├── config/
│   └── config.yaml             # 설정 파일
├── logs/                       # 로그 파일 (gitignore)
├── scripts/                    # 유틸리티 스크립트
│   ├── setup_es.py            # ES 인덱스 초기화
│   └── run_crawler.py         # 크롤러 실행 스크립트
├── requirements.txt            # 프로덕션 의존성
├── requirements-dev.txt        # 개발 의존성
├── .env.example               # 환경 변수 템플릿
├── .gitignore
├── pytest.ini                 # pytest 설정
├── setup.py                   # 패키지 설정
├── CLAUDE.md
├── README.md
└── DEVELOPMENT_PLAN.md        # 이 파일
```

---

## 3. Phase별 개발 계획

### Phase 1: 개발 환경 설정 (예상 시간: 1-2일)

**목표**: 기본 프로젝트 구조 및 개발 환경 구축

**작업 목록**:
- [x] 프로젝트 문서화 (README.md, CLAUDE.md)
- [ ] 디렉토리 구조 생성
- [ ] 가상환경 설정
- [ ] requirements.txt 작성
- [ ] .env.example 작성
- [ ] 기본 설정 파일 (config.yaml) 작성
- [ ] 로깅 유틸리티 구현
- [ ] Git 설정 완료

**완료 조건**:
- 모든 필요한 디렉토리 생성됨
- 의존성 설치 가능
- 기본 설정 로드 가능

---

### Phase 2: 웹 크롤러 구현 (예상 시간: 3-4일)

**목표**: FinancialJuice 웹사이트 크롤링 기능 구현

#### 2.1 HTML 파싱 로직 (src/collector/parser.py)

**작업**:
```python
# 구현할 주요 함수들
- parse_article_list(html: str) -> List[Dict]
- parse_article_detail(html: str) -> Dict
- extract_metadata(soup: BeautifulSoup) -> Dict
- clean_text(text: str) -> str
```

**작업 상세**:
- [ ] FinancialJuice 웹사이트 구조 분석
- [ ] BeautifulSoup을 이용한 HTML 파싱 로직
- [ ] 카테고리별 셀렉터 정의
- [ ] 뉴스 제목, 내용, 날짜, 카테고리 추출
- [ ] 에러 핸들링 (malformed HTML)

#### 2.2 크롤러 메인 로직 (src/collector/crawler.py)

**작업**:
```python
# 구현할 클래스 및 함수
class FinancialJuiceCrawler:
    - async def fetch_page(url: str) -> str
    - async def crawl_category(category: str) -> List[Dict]
    - async def crawl_all() -> Dict[str, List[Dict]]
```

**작업 상세**:
- [ ] aiohttp를 이용한 비동기 HTTP 요청
- [ ] User-Agent 설정
- [ ] 타임아웃 처리
- [ ] 재시도 로직 (exponential backoff)
- [ ] 에러 로깅

#### 2.3 Rate Limiter (src/collector/rate_limiter.py)

**작업**:
```python
class RateLimiter:
    - async def acquire() -> None
    - def set_delay(seconds: float) -> None
```

**작업 상세**:
- [ ] 요청 간 지연 시간 설정
- [ ] 비동기 컨텍스트 매니저 구현
- [ ] 동시 요청 수 제한

#### 2.4 스케줄러 (src/collector/scheduler.py)

**작업**:
```python
class CrawlScheduler:
    - def schedule(cron_expression: str) -> None
    - async def run_job() -> None
    - def start() -> None
    - def stop() -> None
```

**작업 상세**:
- [ ] APScheduler 연동
- [ ] Cron 표현식 기반 스케줄링
- [ ] 작업 실행 로깅
- [ ] 예외 처리 및 알림

**완료 조건**:
- 각 카테고리에서 뉴스 목록 크롤링 성공
- 파싱된 데이터 구조 검증
- Rate limiting 동작 확인
- 스케줄러 정상 동작

---

### Phase 3: Elasticsearch 연동 (예상 시간: 2-3일)

**목표**: 크롤링한 데이터를 Elasticsearch에 저장

#### 3.1 ES 클라이언트 (src/storage/es_client.py)

**작업**:
```python
class ElasticsearchClient:
    - def __init__(host, port)
    - def connect() -> bool
    - def create_index(index_name: str, mapping: Dict) -> bool
    - async def index_document(index: str, doc: Dict) -> bool
    - async def bulk_index(index: str, docs: List[Dict]) -> Dict
    - def search(index: str, query: Dict) -> Dict
    - def delete_index(index_name: str) -> bool
```

**작업 상세**:
- [ ] elasticsearch-py 라이브러리 연동
- [ ] 연결 풀 설정
- [ ] 헬스 체크 기능
- [ ] 에러 핸들링

#### 3.2 인덱스 매핑 (src/storage/mappings.py)

**작업**:
```python
FINANCIAL_NEWS_MAPPING = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "content": {"type": "text"},
            "category": {"type": "keyword"},
            "published_date": {"type": "date"},
            "source_url": {"type": "keyword"},
            "crawled_at": {"type": "date"},
            ...
        }
    }
}
```

**작업 상세**:
- [ ] 필드 타입 정의
- [ ] 분석기(analyzer) 설정
- [ ] 인덱스 별칭 설정
- [ ] 매핑 검증

#### 3.3 인덱서 (src/storage/indexer.py)

**작업**:
```python
class NewsIndexer:
    - async def index_news(news_list: List[Dict]) -> int
    - def check_duplicate(source_url: str) -> bool
    - async def update_document(doc_id: str, updates: Dict) -> bool
```

**작업 상세**:
- [ ] 중복 체크 로직
- [ ] Bulk indexing 구현
- [ ] 색인 성공/실패 통계
- [ ] 에러 복구

**완료 조건**:
- ES 연결 성공
- 인덱스 생성 성공
- 문서 색인 성공
- 검색 쿼리 동작 확인

---

### Phase 4: Flask 웹 인터페이스 (예상 시간: 3-4일)

**목표**: 사용자가 데이터를 조회할 수 있는 웹 인터페이스 구현

#### 4.1 Flask 앱 설정 (src/web/app.py)

**작업**:
```python
def create_app() -> Flask:
    app = Flask(__name__)
    # 설정 로드
    # 블루프린트 등록
    # 에러 핸들러 등록
    return app
```

**작업 상세**:
- [ ] Flask 앱 팩토리 패턴
- [ ] 환경별 설정 (dev, prod)
- [ ] 에러 핸들러 (404, 500)
- [ ] 정적 파일 서빙

#### 4.2 라우트 정의 (src/web/routes.py)

**작업**:
```python
# 구현할 라우트
GET  /                  # 홈페이지 (최신 뉴스)
GET  /search            # 검색 페이지
GET  /category/<name>   # 카테고리별 뉴스
GET  /news/<id>         # 뉴스 상세
GET  /api/news          # API: 뉴스 목록 (JSON)
GET  /api/search        # API: 검색 (JSON)
```

**작업 상세**:
- [ ] RESTful 라우트 설계
- [ ] 페이지네이션 구현
- [ ] 필터링 파라미터 처리
- [ ] JSON API 엔드포인트

#### 4.3 뷰 로직 (src/web/views.py)

**작업**:
```python
class NewsView:
    - def list_news(page: int, category: str) -> Dict
    - def search_news(query: str, filters: Dict) -> Dict
    - def get_news_detail(news_id: str) -> Dict
```

**작업 상세**:
- [ ] ES 쿼리 생성
- [ ] 결과 포맷팅
- [ ] 캐싱 (선택사항)

#### 4.4 템플릿 (src/web/templates/)

**작업**:
- [ ] base.html (베이스 레이아웃)
- [ ] index.html (홈페이지)
- [ ] search.html (검색 페이지)
- [ ] detail.html (뉴스 상세)
- [ ] components/ (재사용 컴포넌트)

**작업 상세**:
- [ ] Jinja2 템플릿 상속
- [ ] 반응형 디자인 (Bootstrap 사용)
- [ ] 카테고리 필터 UI
- [ ] 날짜 범위 선택기
- [ ] 검색 폼

**완료 조건**:
- 모든 페이지 렌더링 성공
- 검색 기능 동작
- 카테고리 필터 동작
- 반응형 디자인 적용

---

### Phase 5: 통합 및 테스트 (예상 시간: 2-3일)

**목표**: 전체 파이프라인 통합 및 테스트

#### 5.1 단위 테스트

**작업**:
- [ ] tests/unit/test_crawler.py
- [ ] tests/unit/test_parser.py
- [ ] tests/unit/test_es_client.py
- [ ] tests/unit/test_rate_limiter.py

**커버리지 목표**: 80% 이상

#### 5.2 통합 테스트

**작업**:
- [ ] 크롤링 → 파싱 → 저장 전체 플로우
- [ ] 웹 앱 → ES 조회 플로우
- [ ] 스케줄러 동작 테스트

#### 5.3 성능 테스트

**작업**:
- [ ] 크롤링 속도 측정
- [ ] ES 인덱싱 속도 측정
- [ ] 웹 앱 응답 시간 측정

**완료 조건**:
- 모든 테스트 통과
- 커버리지 80% 이상
- 성능 벤치마크 완료

---

### Phase 6: 배포 준비 (예상 시간: 1-2일)

**목표**: 프로덕션 환경 배포 준비

**작업**:
- [ ] 배포 스크립트 작성
- [ ] systemd 서비스 파일 작성
- [ ] nginx 설정 (선택사항)
- [ ] 로그 로테이션 설정
- [ ] 모니터링 설정 (선택사항)

---

## 4. 모듈별 상세 설계

### 4.1 Crawler 모듈

**책임**: FinancialJuice 웹사이트에서 데이터 수집

**주요 클래스**:

```python
# src/collector/crawler.py
class FinancialJuiceCrawler:
    """
    FinancialJuice 웹사이트 크롤러
    """
    def __init__(
        self,
        base_url: str,
        user_agent: str,
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.base_url = base_url
        self.session = None
        self.rate_limiter = RateLimiter()

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': self.user_agent},
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.session.close()

    async def fetch_page(self, url: str) -> str:
        """
        단일 페이지 가져오기

        Args:
            url: 크롤링할 URL

        Returns:
            HTML 문자열

        Raises:
            CrawlerException: 크롤링 실패 시
        """
        async with self.rate_limiter:
            for attempt in range(self.max_retries):
                try:
                    async with self.session.get(url) as response:
                        response.raise_for_status()
                        return await response.text()
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise CrawlerException(f"Failed to fetch {url}: {e}")
                    await asyncio.sleep(2 ** attempt)  # exponential backoff

    async def crawl_category(self, category: str) -> List[Dict]:
        """
        특정 카테고리의 뉴스 크롤링

        Args:
            category: 카테고리 이름 (equities, bonds, forex, commodities)

        Returns:
            뉴스 딕셔너리 리스트
        """
        url = f"{self.base_url}/{category}"
        html = await self.fetch_page(url)
        parser = HTMLParser()
        return parser.parse_article_list(html, category)

    async def crawl_all(self) -> Dict[str, List[Dict]]:
        """
        모든 카테고리 크롤링

        Returns:
            카테고리별 뉴스 딕셔너리
        """
        categories = ['equities', 'bonds', 'forex', 'commodities']
        tasks = [self.crawl_category(cat) for cat in categories]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            cat: result if not isinstance(result, Exception) else []
            for cat, result in zip(categories, results)
        }
```

**주요 기능**:
- 비동기 HTTP 요청
- Rate limiting
- 재시도 로직
- 에러 핸들링

---

### 4.2 Parser 모듈

**책임**: HTML을 파싱하여 구조화된 데이터 추출

```python
# src/collector/parser.py
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

class HTMLParser:
    """HTML 파싱 및 데이터 추출"""

    def parse_article_list(
        self,
        html: str,
        category: str
    ) -> List[Dict]:
        """
        뉴스 목록 페이지 파싱

        Args:
            html: HTML 문자열
            category: 카테고리 이름

        Returns:
            뉴스 정보 딕셔너리 리스트
        """
        soup = BeautifulSoup(html, 'lxml')
        articles = []

        # 실제 구조에 맞게 셀렉터 수정 필요
        for article in soup.select('.article-item'):
            try:
                data = {
                    'title': self._extract_title(article),
                    'summary': self._extract_summary(article),
                    'url': self._extract_url(article),
                    'published_date': self._extract_date(article),
                    'category': category,
                    'crawled_at': datetime.utcnow().isoformat()
                }
                articles.append(data)
            except Exception as e:
                logger.error(f"Failed to parse article: {e}")
                continue

        return articles

    def parse_article_detail(self, html: str) -> Dict:
        """뉴스 상세 페이지 파싱"""
        soup = BeautifulSoup(html, 'lxml')

        return {
            'title': self._extract_title(soup),
            'content': self._extract_content(soup),
            'author': self._extract_author(soup),
            'published_date': self._extract_date(soup),
            'tags': self._extract_tags(soup)
        }

    def _extract_title(self, element) -> str:
        """제목 추출"""
        title_elem = element.select_one('h2.title, .article-title')
        return title_elem.get_text(strip=True) if title_elem else ""

    def _extract_summary(self, element) -> str:
        """요약 추출"""
        summary_elem = element.select_one('.summary, .excerpt')
        return summary_elem.get_text(strip=True) if summary_elem else ""

    def _extract_content(self, soup) -> str:
        """본문 추출"""
        content_elem = soup.select_one('.article-content, .post-content')
        if not content_elem:
            return ""
        # 불필요한 태그 제거
        for tag in content_elem.find_all(['script', 'style', 'iframe']):
            tag.decompose()
        return content_elem.get_text(separator='\n', strip=True)

    def _extract_url(self, element) -> str:
        """URL 추출"""
        link_elem = element.select_one('a[href]')
        return link_elem['href'] if link_elem else ""

    def _extract_date(self, element) -> Optional[str]:
        """날짜 추출 및 파싱"""
        date_elem = element.select_one('time, .date, .published')
        if not date_elem:
            return None
        date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
        # 날짜 파싱 로직 (실제 형식에 맞게 조정)
        try:
            return self._parse_date_string(date_str)
        except:
            return None

    def _extract_author(self, soup) -> str:
        """작성자 추출"""
        author_elem = soup.select_one('.author, .by-line')
        return author_elem.get_text(strip=True) if author_elem else ""

    def _extract_tags(self, soup) -> List[str]:
        """태그 추출"""
        tag_elems = soup.select('.tag, .label')
        return [tag.get_text(strip=True) for tag in tag_elems]

    def _parse_date_string(self, date_str: str) -> str:
        """날짜 문자열을 ISO 형식으로 변환"""
        # 실제 날짜 형식에 맞게 구현
        # 예: "Dec 27, 2025" -> "2025-12-27T00:00:00"
        pass
```

---

### 4.3 Storage 모듈

**책임**: Elasticsearch 연동 및 데이터 저장

```python
# src/storage/es_client.py
from elasticsearch import Elasticsearch, helpers
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ElasticsearchClient:
    """Elasticsearch 클라이언트 래퍼"""

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 9200,
        index_prefix: str = 'financial_data'
    ):
        self.host = host
        self.port = port
        self.index_prefix = index_prefix
        self.client = None

    def connect(self) -> bool:
        """ES 연결"""
        try:
            self.client = Elasticsearch([f"{self.host}:{self.port}"])
            if self.client.ping():
                logger.info(f"Connected to Elasticsearch at {self.host}:{self.port}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False

    def create_index(
        self,
        index_name: str,
        mapping: Dict
    ) -> bool:
        """인덱스 생성"""
        try:
            if self.client.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
                return True

            self.client.indices.create(index=index_name, body=mapping)
            logger.info(f"Created index: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            return False

    async def index_document(
        self,
        index: str,
        doc: Dict,
        doc_id: Optional[str] = None
    ) -> bool:
        """단일 문서 색인"""
        try:
            self.client.index(
                index=index,
                id=doc_id,
                body=doc
            )
            return True
        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            return False

    async def bulk_index(
        self,
        index: str,
        docs: List[Dict]
    ) -> Dict:
        """대량 문서 색인"""
        actions = [
            {
                '_index': index,
                '_id': doc.get('url'),  # URL을 ID로 사용 (중복 방지)
                '_source': doc
            }
            for doc in docs
        ]

        try:
            success, failed = helpers.bulk(
                self.client,
                actions,
                raise_on_error=False,
                stats_only=False
            )
            logger.info(f"Indexed {success} documents, {len(failed)} failed")
            return {'success': success, 'failed': failed}
        except Exception as e:
            logger.error(f"Bulk indexing failed: {e}")
            return {'success': 0, 'failed': len(docs)}

    def search(
        self,
        index: str,
        query: Dict,
        size: int = 10,
        from_: int = 0
    ) -> Dict:
        """검색"""
        try:
            return self.client.search(
                index=index,
                body=query,
                size=size,
                from_=from_
            )
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {'hits': {'hits': [], 'total': {'value': 0}}}
```

---

### 4.4 Web 모듈

**책임**: Flask 웹 인터페이스

```python
# src/web/app.py
from flask import Flask, render_template, request, jsonify
from src.storage.es_client import ElasticsearchClient
from src.utils.config import load_config

def create_app():
    """Flask 앱 팩토리"""
    app = Flask(__name__)

    # 설정 로드
    config = load_config()
    app.config.update(config)

    # ES 클라이언트 초기화
    es_client = ElasticsearchClient(
        host=config['ES_HOST'],
        port=config['ES_PORT']
    )
    es_client.connect()

    # 라우트 등록
    from src.web.routes import register_routes
    register_routes(app, es_client)

    return app

# src/web/routes.py
from flask import Blueprint, render_template, request, jsonify

def register_routes(app, es_client):

    @app.route('/')
    def index():
        """홈페이지 - 최신 뉴스"""
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', None)

        query = build_latest_news_query(category)
        results = es_client.search(
            index='financial_data',
            query=query,
            size=20,
            from_=(page-1)*20
        )

        return render_template(
            'index.html',
            news=results['hits']['hits'],
            total=results['hits']['total']['value'],
            page=page
        )

    @app.route('/search')
    def search():
        """검색"""
        q = request.args.get('q', '')
        category = request.args.get('category', None)
        page = request.args.get('page', 1, type=int)

        query = build_search_query(q, category)
        results = es_client.search(
            index='financial_data',
            query=query,
            size=20,
            from_=(page-1)*20
        )

        return render_template(
            'search.html',
            query=q,
            news=results['hits']['hits'],
            total=results['hits']['total']['value'],
            page=page
        )

    @app.route('/news/<news_id>')
    def news_detail(news_id):
        """뉴스 상세"""
        try:
            doc = es_client.client.get(index='financial_data', id=news_id)
            return render_template('detail.html', news=doc['_source'])
        except:
            return render_template('404.html'), 404

    @app.route('/api/news')
    def api_news():
        """API: 뉴스 목록"""
        # JSON 응답
        pass
```

---

## 5. 데이터 모델

### 5.1 Elasticsearch 문서 구조

```python
# src/storage/mappings.py

FINANCIAL_NEWS_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "custom_analyzer": {
                    "type": "standard",
                    "stopwords": "_english_"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "custom_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "summary": {
                "type": "text",
                "analyzer": "custom_analyzer"
            },
            "content": {
                "type": "text",
                "analyzer": "custom_analyzer"
            },
            "category": {
                "type": "keyword"
            },
            "author": {
                "type": "keyword"
            },
            "source_url": {
                "type": "keyword"
            },
            "published_date": {
                "type": "date",
                "format": "strict_date_optional_time||epoch_millis"
            },
            "crawled_at": {
                "type": "date",
                "format": "strict_date_optional_time||epoch_millis"
            },
            "tags": {
                "type": "keyword"
            }
        }
    }
}
```

### 5.2 문서 예시

```json
{
  "title": "Stock Market Hits Record High",
  "summary": "Major indices reached all-time highs...",
  "content": "Full article content here...",
  "category": "equities",
  "author": "John Doe",
  "source_url": "https://www.financialjuice.com/equities/article-123",
  "published_date": "2025-11-27T10:30:00Z",
  "crawled_at": "2025-11-27T11:00:00Z",
  "tags": ["stocks", "market", "nasdaq"]
}
```

---

## 6. 의존성 관리

### 6.1 requirements.txt

```txt
# Web Framework
Flask==2.3.0
Jinja2==3.1.2

# Async & HTTP
aiohttp==3.9.0
asyncio==3.4.3

# HTML Parsing
beautifulsoup4==4.12.0
lxml==4.9.3

# Elasticsearch
elasticsearch==7.17.9

# Scheduling
APScheduler==3.10.4

# Configuration
python-dotenv==1.0.0
PyYAML==6.0.1

# Utilities
python-dateutil==2.8.2
```

### 6.2 requirements-dev.txt

```txt
# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
pytest-mock==3.11.1

# Code Quality
black==23.7.0
flake8==6.1.0
mypy==1.5.0
pylint==2.17.5

# Development
ipython==8.14.0
ipdb==0.13.13
```

---

## 7. 테스트 전략

### 7.1 단위 테스트

```python
# tests/unit/test_parser.py
import pytest
from src.collector.parser import HTMLParser

def test_parse_article_list():
    """뉴스 목록 파싱 테스트"""
    with open('tests/fixtures/sample.html', 'r') as f:
        html = f.read()

    parser = HTMLParser()
    articles = parser.parse_article_list(html, 'equities')

    assert len(articles) > 0
    assert 'title' in articles[0]
    assert 'url' in articles[0]

def test_extract_title():
    """제목 추출 테스트"""
    # ...
```

### 7.2 통합 테스트

```python
# tests/integration/test_full_pipeline.py
import pytest
from src.collector.crawler import FinancialJuiceCrawler
from src.storage.es_client import ElasticsearchClient

@pytest.mark.asyncio
async def test_crawl_and_index():
    """크롤링 -> 저장 전체 플로우 테스트"""
    # 크롤링
    async with FinancialJuiceCrawler() as crawler:
        news = await crawler.crawl_category('equities')

    # ES 저장
    es_client = ElasticsearchClient()
    es_client.connect()
    result = await es_client.bulk_index('test_index', news)

    assert result['success'] > 0
```

### 7.3 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께
pytest --cov=src --cov-report=html

# 특정 테스트만
pytest tests/unit/test_parser.py

# 비동기 테스트
pytest -v tests/integration/
```

---

## 8. 배포 및 운영

### 8.1 환경 변수 (.env)

```bash
# FinancialJuice
FINANCIAL_JUICE_BASE_URL=https://www.financialjuice.com
CRAWLER_USER_AGENT=Mozilla/5.0 (compatible; DataParser/1.0)
CRAWLER_DELAY=2
CRAWLER_TIMEOUT=30
CRAWLER_MAX_RETRIES=3

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_PREFIX=financial_data

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here

# Scheduler
COLLECTION_SCHEDULE=0 9,15,21 * * *

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 8.2 실행 스크립트

```bash
# scripts/run_crawler.py
#!/usr/bin/env python
"""크롤러 실행 스크립트"""
import asyncio
from src.collector.crawler import FinancialJuiceCrawler
from src.storage.indexer import NewsIndexer
from src.utils.logger import setup_logger

logger = setup_logger()

async def main():
    logger.info("Starting crawler...")

    async with FinancialJuiceCrawler() as crawler:
        news_data = await crawler.crawl_all()

    logger.info(f"Crawled {sum(len(v) for v in news_data.values())} articles")

    indexer = NewsIndexer()
    for category, news_list in news_data.items():
        result = await indexer.index_news(news_list)
        logger.info(f"Indexed {result} articles in {category}")

if __name__ == '__main__':
    asyncio.run(main())
```

```bash
# 실행
python scripts/run_crawler.py
```

### 8.3 systemd 서비스 (선택사항)

```ini
# /etc/systemd/system/financial-data-web.service
[Unit]
Description=Financial Data Web Service
After=network.target elasticsearch.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/data-parsing
Environment="PATH=/path/to/data-parsing/venv/bin"
ExecStart=/path/to/data-parsing/venv/bin/python -m src.web.app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl start financial-data-web
sudo systemctl enable financial-data-web
```

---

## 9. 다음 단계

### 즉시 작업
1. [ ] 프로젝트 디렉토리 구조 생성
2. [ ] requirements.txt 작성 및 의존성 설치
3. [ ] 기본 설정 파일 작성
4. [ ] FinancialJuice 웹사이트 구조 분석

### 단기 목표 (1주)
1. [ ] 크롤러 기본 구현
2. [ ] HTML 파싱 로직 완성
3. [ ] ES 연동 완료

### 중기 목표 (2주)
1. [ ] 웹 인터페이스 완성
2. [ ] 테스트 코드 작성
3. [ ] 스케줄러 구현

---

## 10. 참고사항

### 10.1 코딩 컨벤션
- PEP 8 준수
- Type hints 사용
- Docstring 작성 (Google 스타일)
- 로깅 적극 활용

### 10.2 Git 커밋 메시지
```
feat: 새로운 기능
fix: 버그 수정
docs: 문서 수정
refactor: 리팩토링
test: 테스트 추가/수정
chore: 기타 작업
```

### 10.3 주의사항
- 크롤링 시 robots.txt 확인
- Rate limiting 준수
- 에러 로깅 철저히
- 중복 데이터 체크
- 메모리 누수 방지 (세션 정리)

---

**마지막 업데이트**: 2025-11-27
**작성자**: AI Assistant
**상태**: 초안 완성
