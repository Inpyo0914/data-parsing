# Financial Data Parsing & Display Service

금융 데이터 수집 및 전시 웹 서비스

---

## 프로젝트 개요

FinancialJuice에서 금융 시장 관련 뉴스와 이벤트를 자동으로 수집하여 Elasticsearch에 저장하고, Flask 기반 웹 인터페이스를 통해 사용자에게 제공하는 서비스입니다.

### 주요 특징

- **자동 데이터 수집**: 정해진 시간에 FinancialJuice에서 데이터 자동 수집
- **비동기 처리**: 효율적인 데이터 수집 및 저장을 위한 비동기 방식
- **심플한 구조**: 소수 사용자를 위한 단순하고 유지보수가 쉬운 아키텍처
- **인증 불필요**: 별도의 사용자 인증 없이 바로 접근 가능

---

## 대상 데이터

다음 금융 시장 카테고리의 뉴스 및 이벤트:

1. **증권 (Equities)**
2. **채권 (Bonds)**
3. **외환 (Foreign Exchange)**
4. **원자재 (Commodities)**

---

## 프로젝트 목표

### 핵심 목표

1. **자동화**: 수동 개입 없이 정기적으로 금융 데이터 수집
2. **실시간성**: 최신 금융 뉴스 및 이벤트를 신속하게 제공
3. **검색 가능성**: Elasticsearch를 통한 효율적인 데이터 검색 및 필터링
4. **단순성**: 복잡한 기능보다는 핵심 기능의 안정적 동작에 집중
5. **유지보수성**: 향후 수정 및 확장이 용이한 코드 구조

### 비목표 (Non-Goals)

- 대규모 사용자 지원 (동시 사용자 3명 이하 상정)
- 복잡한 인증/권한 시스템
- 실시간 스트리밍 데이터
- 고가용성(HA) 구성

---

## 기술 스택

### Backend
- **Python 3.8+**: 메인 프로그래밍 언어
- **Flask**: 경량 웹 프레임워크
- **aiohttp / asyncio**: 비동기 HTTP 요청 및 웹 크롤링
- **BeautifulSoup4**: HTML 파싱 및 데이터 추출
- **lxml**: 고성능 XML/HTML 파서 (선택사항)

### Data Storage
- **Elasticsearch 7.x**: 데이터 저장 및 검색 엔진

### Scheduling
- **APScheduler** 또는 **Celery**: 정기적인 데이터 수집 스케줄링

### Frontend
- **HTML/CSS/JavaScript**: 심플한 웹 인터페이스
- **Bootstrap** (선택사항): 기본 스타일링

---

## 시스템 아키텍처

```
┌─────────────────────────┐
│ FinancialJuice 웹사이트 │
└───────────┬─────────────┘
            │
            │ (웹 크롤링)
            ▼
┌─────────────────────────┐
│   Web Crawler           │
│   (aiohttp + BS4)       │
└───────────┬─────────────┘
            │
            │ (파싱 & 저장)
            ▼
┌─────────────────────────┐
│  Elasticsearch 7.x      │
└───────────┬─────────────┘
            │
            │ (조회)
            ▼
┌─────────────────────────┐
│   Flask Web App         │
└───────────┬─────────────┘
            │
            │ (전시)
            ▼
┌─────────────────────────┐
│   사용자 브라우저        │
└─────────────────────────┘
```

---

## 주요 기능

### 1. 데이터 수집 (Data Collection)

- FinancialJuice 웹사이트 크롤링을 통한 뉴스/이벤트 수집
- 비동기 방식으로 여러 카테고리 동시 크롤링
- HTML 파싱 및 구조화된 데이터 추출
- 중복 데이터 필터링
- 오류 발생 시 재시도 로직
- 정해진 시간에 자동 실행 (스케줄링)
- Rate limiting을 통한 서버 부하 최소화

### 2. 데이터 저장 (Data Storage)

- Elasticsearch 7.x에 구조화된 형태로 저장
- 카테고리별 인덱싱
- 타임스탬프 기반 정렬
- 효율적인 검색을 위한 필드 매핑

### 3. 웹 인터페이스 (Web Interface)

- **홈 페이지**: 최신 뉴스/이벤트 목록 표시
- **카테고리 필터링**: 증권, 채권, 외환, 원자재별 필터
- **검색 기능**: 키워드 기반 뉴스 검색
- **날짜 필터**: 기간별 데이터 조회
- **상세 보기**: 개별 뉴스/이벤트 상세 정보

---

## 설계 원칙

### 1. 단순성 (Simplicity)

- 최소한의 의존성
- 명확한 코드 구조
- 불필요한 추상화 지양

### 2. 유지보수성 (Maintainability)

- 명확한 함수/모듈 분리
- 충분한 주석 및 문서화
- 일관된 코딩 스타일

### 3. 확장성 고려 (Future-Proof)

- 새로운 데이터 소스 추가 용이
- 카테고리 확장 가능한 구조
- 설정 파일 기반 구성

---

## 프로젝트 구조 (예상)

```
data-parsing/
├── src/
│   ├── collector/          # 데이터 수집 모듈
│   │   ├── __init__.py
│   │   ├── financial_juice.py
│   │   └── scheduler.py
│   ├── storage/            # Elasticsearch 연동
│   │   ├── __init__.py
│   │   └── es_client.py
│   ├── web/                # Flask 웹 앱
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes.py
│   │   └── templates/
│   └── utils/              # 공통 유틸리티
│       └── config.py
├── tests/                  # 테스트 코드
├── config/                 # 설정 파일
│   └── config.yaml
├── requirements.txt        # Python 의존성
├── .env.example           # 환경 변수 예시
├── CLAUDE.md              # AI 어시스턴트 가이드
└── README.md              # 이 파일
```

---

## 시작하기

### 사전 요구사항

- Python 3.8 이상
- Elasticsearch 7.x
- 안정적인 인터넷 연결

### 설치 (예정)

```bash
# 저장소 클론
git clone https://github.com/Inpyo0914/data-parsing.git
cd data-parsing

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집하여 필요한 설정 입력

# Elasticsearch 연결 확인
# (Elasticsearch가 실행 중이어야 함)

# 웹 서버 실행
python src/web/app.py
```

---

## 설정

### 환경 변수

```bash
# FinancialJuice 크롤링 설정
FINANCIAL_JUICE_BASE_URL=https://www.financialjuice.com
CRAWLER_USER_AGENT=Mozilla/5.0 (compatible; DataParser/1.0)
CRAWLER_DELAY=2  # 요청 간 대기 시간 (초)
CRAWLER_TIMEOUT=30  # 요청 타임아웃 (초)

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200
ES_INDEX_PREFIX=financial_data

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# Scheduler
COLLECTION_SCHEDULE=0 9,15,21 * * *  # 매일 9시, 15시, 21시
```

---

## 사용 예시

### 데이터 수집 실행

```bash
# 수동 실행
python src/collector/financial_juice.py

# 스케줄러 시작
python src/collector/scheduler.py
```

### 웹 서비스 접속

```
http://localhost:5000
```

---

## 개발 로드맵

### Phase 1: 기본 구조 (현재)
- [x] 프로젝트 문서화
- [ ] 프로젝트 구조 생성
- [ ] 개발 환경 설정

### Phase 2: 데이터 수집
- [ ] FinancialJuice 웹 크롤러 구현
- [ ] HTML 파싱 및 데이터 추출 로직
- [ ] 비동기 크롤링 로직 구현
- [ ] Rate limiting 및 에러 핸들링
- [ ] 스케줄러 구현

### Phase 3: 데이터 저장
- [ ] Elasticsearch 클라이언트 구현
- [ ] 인덱스 매핑 정의
- [ ] 데이터 저장 로직 구현

### Phase 4: 웹 인터페이스
- [ ] Flask 앱 기본 구조
- [ ] 뉴스 목록 페이지
- [ ] 검색 기능
- [ ] 필터링 기능

### Phase 5: 테스트 및 배포
- [ ] 단위 테스트 작성
- [ ] 통합 테스트
- [ ] 배포 스크립트 작성

---

## 제약사항

- **동시 사용자**: 최대 3명 (소규모 서비스)
- **인증**: 구현하지 않음
- **데이터 보관**: 정책 미정 (추후 결정)
- **백업**: 기본 Elasticsearch 스냅샷 활용

---

## 트러블슈팅

### Elasticsearch 연결 실패
- Elasticsearch 서비스가 실행 중인지 확인
- 포트 및 호스트 설정 확인

### 데이터 수집 실패
- 네트워크 연결 확인
- FinancialJuice 웹사이트 구조 변경 여부 확인
- User-Agent 설정 확인
- Rate limiting 설정 조정 (요청 간격 늘리기)
- 크롤링 대상 URL 유효성 확인

---

## 기여

이 프로젝트는 소수 사용자를 위한 개인 프로젝트입니다. 기여에 대한 별도 가이드라인은 없으나, 개선 사항이 있다면 이슈를 통해 제안해주세요.

---

## 라이선스

TBD (To Be Determined)

---

## 연락처

- Repository: [Inpyo0914/data-parsing](https://github.com/Inpyo0914/data-parsing)
- Issues: [GitHub Issues](https://github.com/Inpyo0914/data-parsing/issues)

---

**마지막 업데이트**: 2025-11-26
