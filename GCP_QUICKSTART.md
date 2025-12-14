# 🚀 Google Cloud Platform 배포 - 완전 초보자 가이드

Google Cloud에 Flask 뉴스 웹사이트를 배포하는 방법을 처음부터 끝까지 자세히 설명합니다.

---

## 📌 목차

1. [Google Cloud 계정 만들기](#1-google-cloud-계정-만들기)
2. [Google Cloud SDK 설치하기](#2-google-cloud-sdk-설치하기)
3. [터미널(명령 프롬프트) 사용법](#3-터미널명령-프롬프트-사용법)
4. [Google Cloud 로그인하기](#4-google-cloud-로그인하기)
5. [프로젝트 만들기](#5-프로젝트-만들기)
6. [배포하기 (App Engine 방법)](#6-배포하기-app-engine-방법)
7. [웹사이트 확인하기](#7-웹사이트-확인하기)

---

## 1. Google Cloud 계정 만들기

### 1-1. Google Cloud 접속
1. 웹브라우저를 열고 https://cloud.google.com 접속
2. 우측 상단의 **"무료로 시작하기"** 또는 **"Console"** 클릭
3. Google 계정으로 로그인 (없으면 먼저 Google 계정 생성)

### 1-2. 무료 크레딧 활성화
1. 국가 선택 (대한민국)
2. 이용약관 동의 체크
3. **결제 정보 입력** (필수)
   - 💡 신용카드 또는 체크카드 등록
   - ⚠️ 무료 크레딧 $300이 제공되며, 자동 청구되지 않음
   - ⚠️ 무료 할당량 내에서 사용하면 비용 발생 안 함
4. "무료 평가판 시작" 클릭

✅ **완료!** 이제 Google Cloud Console 대시보드를 볼 수 있습니다.

---

## 2. Google Cloud SDK 설치하기

**Google Cloud SDK**는 터미널(명령 프롬프트)에서 `gcloud` 명령어를 사용할 수 있게 해주는 프로그램입니다.

### 윈도우 (Windows) 사용자

#### 2-1. 설치 프로그램 다운로드
1. https://cloud.google.com/sdk/docs/install 접속
2. **Windows용 설치 프로그램** 다운로드
   - "GoogleCloudSDKInstaller.exe" 파일 다운로드

#### 2-2. 설치 실행
1. 다운로드한 `.exe` 파일 더블클릭
2. "다음" 클릭하며 설치 진행
3. **중요:** "Start Cloud SDK Shell" 체크박스 체크
4. "완료" 클릭

#### 2-3. Cloud SDK Shell 열기
설치 완료 후 자동으로 **"Google Cloud SDK Shell"** 창이 열립니다.
(검은색 또는 파란색 배경의 터미널 창)

**나중에 다시 열려면?**
- 시작 메뉴 → "Google Cloud SDK Shell" 검색 → 클릭

---

### 맥 (macOS) 사용자

#### 2-1. 터미널 열기
1. 런치패드 → "기타" → "터미널" 클릭
   - 또는 `Command + Space` → "터미널" 입력 → Enter

#### 2-2. SDK 설치 명령어 실행
터미널에 아래 명령어를 **복사해서 붙여넣고** Enter:
```bash
curl https://sdk.cloud.google.com | bash
```

설치 중 질문이 나오면:
- "Do you want to continue?" → **Y** 입력 후 Enter
- 설치 경로 묻는 질문 → 그냥 **Enter** (기본 경로 사용)

#### 2-3. 터미널 재시작
터미널 창을 **완전히 닫고** 다시 엽니다.

---

### 리눅스 (Linux) 사용자

터미널에 아래 명령어 실행:
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

---

## 3. 터미널(명령 프롬프트) 사용법

### 터미널이란?
- 명령어를 입력해서 컴퓨터를 조작하는 프로그램
- **Windows**: "명령 프롬프트", "PowerShell", "Google Cloud SDK Shell"
- **Mac/Linux**: "터미널"

### 터미널 여는 방법

#### Windows:
1. **Google Cloud SDK Shell** 사용 (권장)
   - 시작 메뉴 → "Google Cloud SDK Shell" 검색 → 클릭

2. 또는 **PowerShell** 사용
   - 시작 메뉴 → "PowerShell" 검색 → 클릭

#### Mac:
- `Command + Space` → "터미널" 입력 → Enter

#### Linux:
- `Ctrl + Alt + T`

### 기본 명령어

```bash
# 현재 위치 확인
pwd

# 파일 목록 보기
ls          # Mac/Linux
dir         # Windows

# 폴더 이동
cd 폴더이름

# 한 단계 위 폴더로 이동
cd ..
```

---

## 4. Google Cloud 로그인하기

### 4-1. 터미널 열기
- **Windows**: Google Cloud SDK Shell 실행
- **Mac/Linux**: 터미널 실행

### 4-2. Google 계정 로그인

터미널에 다음 명령어 입력:
```bash
gcloud auth login
```

Enter를 누르면:
1. 웹브라우저가 **자동으로 열립니다**
2. Google 계정 선택
3. "Google Cloud SDK에서 Google 계정에 액세스하려고 합니다" → **허용** 클릭
4. "인증되었습니다" 메시지 확인
5. 브라우저 창 닫기

터미널로 돌아오면:
```
You are now logged in as [your-email@gmail.com].
```
이런 메시지가 보이면 성공!

---

## 5. 프로젝트 만들기

### 5-1. 프로젝트 ID 정하기

프로젝트 ID는 전 세계에서 유일해야 하며, 한 번 정하면 변경할 수 없습니다.

**예시:**
- `my-news-app-12345`
- `news-feed-2024`
- `yourname-news-site`

**규칙:**
- 소문자, 숫자, 하이픈(-) 만 사용
- 6-30자
- 문자로 시작해야 함

### 5-2. 터미널에서 프로젝트 생성

터미널에 다음 명령어 입력 (프로젝트 ID는 본인이 정한 것으로 변경):
```bash
gcloud projects create my-news-app-12345 --name="뉴스 피드 웹사이트"
```

**명령어 설명:**
- `gcloud projects create`: 프로젝트 생성 명령
- `my-news-app-12345`: 프로젝트 ID (본인 것으로 변경!)
- `--name="뉴스 피드 웹사이트"`: 프로젝트 이름 (한글 가능)

성공하면:
```
Create in progress for [my-news-app-12345].
```
이런 메시지가 보입니다.

### 5-3. 프로젝트 설정

터미널에 다음 명령어 입력:
```bash
gcloud config set project my-news-app-12345
```
(프로젝트 ID는 본인 것으로 변경!)

### 5-4. 결제 계정 연결

#### 방법 1: 웹 브라우저에서 연결 (권장)
1. https://console.cloud.google.com 접속
2. 좌측 상단 프로젝트 선택 드롭다운 클릭
3. 방금 만든 프로젝트 선택
4. 좌측 메뉴 → "결제" → "계정 연결" 클릭
5. 무료 평가판 계정 선택 → "계정 설정" 클릭

#### 방법 2: 터미널에서 확인
```bash
gcloud billing accounts list
```

출력되는 계정 ID를 복사한 후:
```bash
gcloud billing projects link my-news-app-12345 --billing-account=계정ID
```

---

## 6. 배포하기 (App Engine 방법)

이제 본격적으로 웹사이트를 배포합니다!

### 6-1. 프로젝트 폴더로 이동

#### 현재 이 저장소를 다운로드했다면:

**Windows 예시:**
```bash
cd C:\Users\사용자이름\Downloads\data-parsing
```

**Mac/Linux 예시:**
```bash
cd ~/Downloads/data-parsing
```

**폴더 경로 찾는 방법:**
- **Windows**: 파일 탐색기에서 폴더 열고 주소창 복사
- **Mac**: Finder에서 폴더 우클릭 → "정보 입력" → 위치 복사

#### Git으로 저장소 클론했다면:
```bash
cd data-parsing
```

### 6-2. 파일 확인

현재 폴더에 다음 파일들이 있는지 확인:
```bash
ls          # Mac/Linux
dir         # Windows
```

**필요한 파일:**
- ✅ `flask_news_app.py`
- ✅ `app.yaml`
- ✅ `requirements.txt`

보이지 않으면 폴더 위치가 잘못된 것입니다!

### 6-3. App Engine 초기화

터미널에 다음 명령어 입력:
```bash
gcloud app create --region=asia-northeast3
```

**명령어 설명:**
- `gcloud app create`: App Engine 앱 생성
- `--region=asia-northeast3`: 서울 리전 (한국에서 가장 빠름)

**다른 리전 옵션:**
- `asia-northeast1`: 도쿄
- `us-central1`: 미국 중부
- `europe-west1`: 벨기에

질문이 나오면 **Y** 입력 후 Enter

성공하면:
```
Success! The app is now created.
```

### 6-4. **드디어 배포!**

터미널에 다음 명령어 입력:
```bash
gcloud app deploy
```

진행 과정:
1. "Do you want to continue (Y/n)?" → **Y** 입력 후 Enter
2. 업로드 중... (약 1-2분)
3. 빌드 중... (약 2-3분)
4. 배포 중... (약 1분)

**전체 약 3-5분 소요**

성공하면:
```
Deployed service [default] to [https://your-project-id.uc.r.appspot.com]
```

---

## 7. 웹사이트 확인하기

### 7-1. 브라우저에서 열기

#### 방법 1: 자동으로 열기
터미널에 입력:
```bash
gcloud app browse
```

자동으로 브라우저가 열립니다!

#### 방법 2: 직접 URL 입력
배포 완료 메시지에 나온 URL을 복사해서 브라우저에 붙여넣기:
```
https://your-project-id.uc.r.appspot.com
```

### 7-2. 웹사이트 확인

축하합니다! 🎉

뉴스 피드 웹사이트가 보이면 배포 성공입니다!

---

## 8. 뉴스 내용 수정하고 다시 배포하기

### 8-1. 코드 수정

`flask_news_app.py` 파일을 텍스트 에디터로 열고 `news_items` 부분 수정

### 8-2. 다시 배포

터미널에서 동일한 명령어 실행:
```bash
gcloud app deploy
```

업데이트가 자동으로 배포됩니다!

---

## 💡 자주 묻는 질문 (FAQ)

### Q1: "gcloud 명령어를 찾을 수 없습니다" 오류가 나요!

**원인**: Google Cloud SDK가 제대로 설치되지 않았습니다.

**해결:**
1. Google Cloud SDK Shell 사용 (Windows)
2. 터미널 재시작 (Mac/Linux)
3. SDK 재설치

### Q2: "Billing account is not enabled" 오류가 나요!

**원인**: 결제 계정이 연결되지 않았습니다.

**해결:**
1. https://console.cloud.google.com/billing 접속
2. "계정 연결" 클릭
3. 무료 평가판 선택

### Q3: 배포 후 502 오류가 나요!

**원인**: 앱이 제대로 시작되지 않았습니다.

**해결:**
```bash
# 로그 확인
gcloud app logs tail
```

### Q4: 비용이 얼마나 나오나요?

**답변:**
- 무료 할당량: 하루 28시간 (F1 인스턴스 기준)
- 소규모 개인 사이트는 **완전 무료**
- 무료 크레딧 $300 제공

### Q5: 배포를 취소하고 싶어요!

**방법 1: 특정 버전만 삭제**
```bash
gcloud app versions list
gcloud app versions delete [VERSION_ID]
```

**방법 2: 프로젝트 전체 삭제**
```bash
gcloud projects delete my-news-app-12345
```

---

## 📝 명령어 요약 (복사용)

```bash
# 1. 로그인
gcloud auth login

# 2. 프로젝트 생성
gcloud projects create my-news-app-12345 --name="뉴스 피드 웹사이트"

# 3. 프로젝트 설정
gcloud config set project my-news-app-12345

# 4. 프로젝트 폴더로 이동
cd /path/to/data-parsing

# 5. App Engine 초기화
gcloud app create --region=asia-northeast3

# 6. 배포
gcloud app deploy

# 7. 웹사이트 열기
gcloud app browse
```

---

## 🎯 다음 단계

배포에 성공했다면:

1. ✅ 커스텀 도메인 연결하기
2. ✅ 뉴스 데이터 자동 업데이트 기능 추가
3. ✅ 데이터베이스 연결 (Firestore)
4. ✅ 사용자 로그인 기능 추가
5. ✅ RSS 피드 파싱 기능 추가

---

## 🆘 도움이 필요하면?

- **공식 문서**: https://cloud.google.com/appengine/docs
- **한국어 지원**: https://cloud.google.com/support
- **커뮤니티**: https://www.googlecloudcommunity.com/

---

**축하합니다! 이제 여러분의 웹사이트가 전 세계에 공개되었습니다! 🎉**
