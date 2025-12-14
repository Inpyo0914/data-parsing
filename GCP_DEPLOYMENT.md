# Google Cloud Platform 배포 가이드

Flask 뉴스 웹사이트를 Google Cloud Platform에 배포하는 방법을 안내합니다.

---

## 📋 목차

1. [배포 방법 비교](#배포-방법-비교)
2. [사전 준비](#사전-준비)
3. [방법 1: Google App Engine (추천)](#방법-1-google-app-engine-추천)
4. [방법 2: Google Cloud Run](#방법-2-google-cloud-run)
5. [비용 안내](#비용-안내)
6. [문제 해결](#문제-해결)

---

## 배포 방법 비교

| 특징 | App Engine | Cloud Run |
|------|-----------|-----------|
| 설정 난이도 | ⭐ 매우 쉬움 | ⭐⭐ 쉬움 |
| 배포 시간 | 3-5분 | 5-7분 |
| 무료 할당량 | 28시간/일 | 월 200만 요청 |
| 자동 스케일링 | ✅ | ✅ |
| 커스텀 도메인 | ✅ | ✅ |
| 컨테이너 제어 | ❌ | ✅ |
| 추천 대상 | 간단한 배포 | 컨테이너 경험자 |

---

## 사전 준비

### 1. Google Cloud 계정 생성
- https://cloud.google.com 접속
- "무료로 시작하기" 클릭
- Google 계정으로 로그인
- 신용카드 등록 (무료 크레딧 $300 제공)

### 2. 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 상단 프로젝트 선택 → "새 프로젝트"
3. 프로젝트 이름 입력 (예: `news-feed-app`)
4. "만들기" 클릭

### 3. Google Cloud SDK 설치

#### macOS/Linux:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

#### Windows:
1. https://cloud.google.com/sdk/docs/install 에서 설치 프로그램 다운로드
2. 설치 후 명령 프롬프트에서:
```cmd
gcloud init
```

### 4. 인증 및 프로젝트 설정
```bash
# Google 계정으로 로그인
gcloud auth login

# 프로젝트 설정
gcloud config set project [PROJECT_ID]

# 현재 설정 확인
gcloud config list
```

---

## 방법 1: Google App Engine (추천)

### ⭐ 장점
- 설정 파일 하나만 있으면 됨
- 배포 명령어 한 줄
- 자동 스케일링 및 로드 밸런싱
- HTTPS 자동 적용

### 📝 배포 단계

#### 1. App Engine API 활성화
```bash
gcloud app create --region=asia-northeast3
```
> 💡 `asia-northeast3`는 서울 리전입니다. 다른 리전도 선택 가능합니다.

#### 2. 필요한 파일 확인
이 레포지토리에는 이미 다음 파일들이 포함되어 있습니다:
- ✅ `flask_news_app.py` - Flask 애플리케이션
- ✅ `requirements.txt` - Python 의존성
- ✅ `app.yaml` - App Engine 설정

#### 3. 배포 실행
```bash
gcloud app deploy
```

명령어 실행 후:
- `Do you want to continue (Y/n)?` → **Y** 입력
- 배포 완료까지 3-5분 소요

#### 4. 웹사이트 열기
```bash
gcloud app browse
```

또는 다음 URL로 직접 접속:
```
https://[PROJECT_ID].uc.r.appspot.com
```

### 🔄 업데이트 배포
코드를 수정한 후:
```bash
gcloud app deploy
```
동일한 명령어로 업데이트를 배포할 수 있습니다.

### 📊 로그 확인
```bash
# 실시간 로그 확인
gcloud app logs tail -s default

# 최근 로그 보기
gcloud app logs read
```

### 🗑️ 삭제
```bash
# 앱 버전 삭제
gcloud app versions delete [VERSION_ID]

# 프로젝트 전체 삭제 (주의!)
gcloud projects delete [PROJECT_ID]
```

---

## 방법 2: Google Cloud Run

### ⭐ 장점
- 컨테이너 기반으로 더 유연함
- 사용한 만큼만 과금 (더 저렴할 수 있음)
- 로컬 Docker로 테스트 가능

### 📝 배포 단계

#### 1. Cloud Run API 활성화
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 2. 필요한 파일 확인
이 레포지토리에는 이미 다음 파일들이 포함되어 있습니다:
- ✅ `flask_news_app.py` - Flask 애플리케이션
- ✅ `requirements.txt` - Python 의존성
- ✅ `Dockerfile` - 컨테이너 설정
- ✅ `.dockerignore` - Docker 빌드 최적화

#### 3. Cloud Build로 이미지 빌드 및 배포
```bash
gcloud run deploy news-feed-app \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --platform managed
```

옵션 설명:
- `--source .`: 현재 디렉토리의 코드 사용
- `--region asia-northeast3`: 서울 리전
- `--allow-unauthenticated`: 공개 접근 허용
- `--platform managed`: 완전 관리형 서비스

#### 4. 배포 완료
배포가 완료되면 다음과 같은 URL이 표시됩니다:
```
Service URL: https://news-feed-app-xxxxx-an.a.run.app
```

### 🔄 업데이트 배포
```bash
gcloud run deploy news-feed-app \
  --source . \
  --region asia-northeast3
```

### 📊 로그 확인
```bash
# 실시간 로그
gcloud run logs tail news-feed-app --region asia-northeast3

# 최근 로그
gcloud run logs read news-feed-app --region asia-northeast3
```

### 🗑️ 삭제
```bash
gcloud run services delete news-feed-app --region asia-northeast3
```

---

## 로컬 테스트 (선택사항)

### App Engine 로컬 테스트
```bash
# 개발 서버 실행
python flask_news_app.py

# 브라우저에서 http://localhost:5000 접속
```

### Cloud Run 로컬 테스트
```bash
# Docker 이미지 빌드
docker build -t news-feed-app .

# 컨테이너 실행
docker run -p 8080:8080 news-feed-app

# 브라우저에서 http://localhost:8080 접속
```

---

## 비용 안내

### App Engine 무료 할당량
- **인스턴스 시간**: 28시간/일 (F1 인스턴스 기준)
- **송신 대역폭**: 1GB/일
- **수신 대역폭**: 무제한

**예상 비용**: 트래픽이 적으면 **완전 무료**

### Cloud Run 무료 할당량 (월별)
- **요청**: 200만 건
- **CPU 시간**: 36만 vCPU-초
- **메모리**: 18만 GiB-초
- **송신 대역폭**: 1GB

**예상 비용**: 소규모 사이트는 **완전 무료**

### 💡 비용 절감 팁
1. **App Engine**: `app.yaml`에서 `min_instances: 0` 설정 (이미 적용됨)
2. **Cloud Run**: 요청이 없으면 자동으로 0으로 스케일 다운
3. **예산 알림 설정**:
   ```bash
   # Cloud Console에서 설정
   # Billing → Budgets & alerts → CREATE BUDGET
   ```

---

## 커스텀 도메인 연결

### App Engine
1. [App Engine 설정](https://console.cloud.google.com/appengine/settings/domains) 접속
2. "커스텀 도메인" → "도메인 추가"
3. 도메인 소유권 확인
4. DNS 레코드 설정

### Cloud Run
```bash
gcloud run domain-mappings create \
  --service news-feed-app \
  --domain your-domain.com \
  --region asia-northeast3
```

---

## 환경 변수 설정

### App Engine (app.yaml에 추가)
```yaml
env_variables:
  API_KEY: "your-api-key"
  ENV: "production"
```

### Cloud Run
```bash
gcloud run deploy news-feed-app \
  --set-env-vars API_KEY=your-api-key,ENV=production \
  --region asia-northeast3
```

---

## 문제 해결

### ❌ "Billing account is not enabled" 오류
**원인**: 결제 계정이 활성화되지 않음

**해결**:
1. https://console.cloud.google.com/billing 접속
2. 결제 계정 설정 또는 연결
3. 무료 크레딧 $300 활성화

### ❌ "API has not been used" 오류
**원인**: 필요한 API가 활성화되지 않음

**해결**:
```bash
# App Engine
gcloud services enable appengine.googleapis.com

# Cloud Run
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
```

### ❌ "Permission denied" 오류
**원인**: 계정 권한 부족

**해결**:
```bash
# 다시 인증
gcloud auth login

# 프로젝트 소유자 권한 필요
# Cloud Console에서 IAM 설정 확인
```

### ❌ 배포 후 502/503 오류
**원인**: 앱이 제대로 시작되지 않음

**해결**:
```bash
# 로그 확인
gcloud app logs tail -s default  # App Engine
gcloud run logs tail news-feed-app --region asia-northeast3  # Cloud Run

# 로컬에서 먼저 테스트
python flask_news_app.py
```

### ❌ 느린 첫 응답 (Cold Start)
**원인**: 인스턴스가 0으로 스케일 다운된 후 첫 요청

**해결 (App Engine)**:
`app.yaml`에서:
```yaml
automatic_scaling:
  min_instances: 1  # 최소 1개 인스턴스 유지 (비용 발생)
```

**해결 (Cloud Run)**:
```bash
gcloud run deploy news-feed-app \
  --min-instances 1 \
  --region asia-northeast3
```
> ⚠️ 주의: `min_instances: 1`은 비용이 발생할 수 있습니다

---

## 모니터링 및 성능

### App Engine Dashboard
```bash
# 브라우저에서 대시보드 열기
open https://console.cloud.google.com/appengine
```

### Cloud Run Metrics
```bash
# 브라우저에서 메트릭 확인
open https://console.cloud.google.com/run
```

### 모니터링 설정
- **Uptime Checks**: 사이트 가동 시간 모니터링
- **Alerting**: 문제 발생 시 이메일 알림
- **Cloud Monitoring**: 상세 성능 메트릭

---

## 추천 배포 전략

### 소규모 개인 프로젝트
→ **App Engine** 추천
- 설정이 간단하고 빠름
- 유지보수가 쉬움

### 마이크로서비스 / 컨테이너 경험자
→ **Cloud Run** 추천
- 더 저렴할 수 있음
- 유연한 커스터마이징

### 프로덕션 환경
→ **Cloud Run + Cloud CDN** 추천
- 글로벌 콘텐츠 배포
- 더 나은 성능

---

## 유용한 명령어 모음

```bash
# 현재 배포된 버전 확인
gcloud app versions list

# 트래픽 분할 (A/B 테스트)
gcloud app services set-traffic default --splits v1=0.9,v2=0.1

# 자동 스케일링 확인
gcloud app instances list

# Cloud Run 서비스 목록
gcloud run services list

# Cloud Run 리비전 목록
gcloud run revisions list

# 프로젝트 전체 비용 확인
gcloud billing accounts list
```

---

## 다음 단계

배포 후 고려할 사항:

1. ✅ **모니터링 설정**: Cloud Monitoring으로 성능 추적
2. ✅ **백업 전략**: 정기적인 백업 설정
3. ✅ **CI/CD 구축**: GitHub Actions로 자동 배포
4. ✅ **보안 강화**: IAP (Identity-Aware Proxy) 설정
5. ✅ **성능 최적화**: CDN, 캐싱 설정

---

## 참고 자료

- [App Engine 문서](https://cloud.google.com/appengine/docs)
- [Cloud Run 문서](https://cloud.google.com/run/docs)
- [GCP 무료 등급](https://cloud.google.com/free)
- [GCP 가격 계산기](https://cloud.google.com/products/calculator)

---

**문제가 발생하면?**
- [GCP 공식 지원](https://cloud.google.com/support)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-app-engine)
- [GCP 커뮤니티](https://www.googlecloudcommunity.com/)
