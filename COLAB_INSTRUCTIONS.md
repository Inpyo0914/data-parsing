# Google Colab에서 Flask 뉴스 웹사이트 실행하기

## ⭐ 방법 1: Colab 내장 기능 사용 (가장 간단! 추천)

Google Colab 노트북에서 다음 셀들을 순서대로 실행하세요:

### 셀 1: Flask 설치
```python
!pip install flask
```

### 셀 2: Flask 앱 코드 작성
```python
from flask import Flask, render_template_string

app = Flask(__name__)

# 뉴스 데이터
news_items = [
    {
        "title": "Fed's Daly: This week's Fed decision was not an easy choice - LinkedIn",
        "time": "05:55 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#1a73e8"
    },
    {
        "title": "Trump: Kevin Warsh at top of Fed chair candidate list - CNBC",
        "time": "05:55 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#1a73e8"
    },
    {
        "title": "Trump: We should have the lowest rate in the world - WSJ",
        "time": "05:50 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#1a73e8"
    },
    {
        "title": "Trump: I am leaning toward Warsh or Hassett to lead the Fed - WSJ",
        "time": "05:46 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#1a73e8"
    },
    {
        "title": "Trump: Interest rates should be 1% or lower a year from now - WSJ",
        "time": "05:45 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#1a73e8"
    },
    {
        "title": "Trump: The next Fed Chair should consult with him on interest rates - WSJ",
        "time": "05:46 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#1a73e8"
    },
    {
        "title": "Trump: I am leaning toward Warsh or Hassett to lead the Fed - WSJ",
        "time": "05:46 Dec 13",
        "tags": ["US Bonds", "US Indexes", "USD"],
        "color": "#dc3545"
    }
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>경제 뉴스 피드</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        h1 {
            color: #58a6ff;
            margin-bottom: 30px;
            font-size: 28px;
            text-align: center;
        }

        .news-list {
            list-style: none;
        }

        .news-item {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px 20px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .news-item:hover {
            background-color: #1c2128;
            border-color: #58a6ff;
            transform: translateX(4px);
        }

        .news-item.highlight {
            border-left: 4px solid #dc3545;
        }

        .news-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 20px;
        }

        .news-content {
            flex: 1;
        }

        .news-title {
            font-size: 15px;
            color: #e6edf3;
            margin-bottom: 8px;
            line-height: 1.5;
        }

        .news-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .news-time {
            font-size: 12px;
            color: #7d8590;
        }

        .news-tags {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .tag {
            background-color: #1f6feb;
            color: #ffffff;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }

        .link-icon {
            color: #7d8590;
            font-size: 18px;
            cursor: pointer;
            transition: color 0.2s;
        }

        .link-icon:hover {
            color: #58a6ff;
        }

        .header-info {
            text-align: center;
            margin-bottom: 20px;
            color: #7d8590;
            font-size: 14px;
        }

        @media (max-width: 768px) {
            .news-item {
                flex-direction: column;
                align-items: flex-start;
            }

            .news-meta {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 경제 뉴스 피드</h1>
        <div class="header-info">
            최근 Fed 및 Trump 관련 뉴스 업데이트
        </div>

        <ul class="news-list">
            {% for item in news_items %}
            <li class="news-item {% if item.color == '#dc3545' %}highlight{% endif %}">
                <div class="news-icon" style="background-color: {{ item.color }}20; color: {{ item.color }};">
                    📰
                </div>

                <div class="news-content">
                    <div class="news-title">{{ item.title }}</div>
                    <div class="news-meta">
                        <span class="news-time">{{ item.time }}</span>
                        <div class="news-tags">
                            {% for tag in item.tags %}
                            <span class="tag">{{ tag }}</span>
                            {% endfor %}
                        </div>
                    </div>
                </div>

                <div class="link-icon">🔗</div>
            </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, news_items=news_items)
```

### 셀 3: 서버 실행 및 접속 URL 생성
```python
import threading
from google.colab.output import eval_js

# Flask 서버를 백그라운드에서 실행
def run_app():
    app.run(port=5000, debug=False, use_reloader=False)

thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

# Colab에서 제공하는 공개 URL 생성
import time
time.sleep(2)  # 서버 시작 대기
public_url = eval_js("google.colab.kernel.proxyPort(5000)")
print(f"✅ 웹사이트 접속 URL: {public_url}")
print(f"위 링크를 클릭하면 웹사이트를 볼 수 있습니다!")
```

**장점:**
- ✅ 별도 가입 불필요
- ✅ 인증 토큰 설정 불필요
- ✅ 즉시 사용 가능
- ✅ Colab 세션 내에서 안정적으로 작동

---

## 방법 2: ngrok 사용 (외부 공유 가능)

다른 사람과 URL을 공유하고 싶다면 ngrok을 사용하세요:

### 셀 1: 설치
```python
!pip install flask pyngrok
```

### 셀 2: Flask 앱 코드 (위의 셀 2와 동일)

### 셀 3: ngrok으로 서버 실행
```python
from pyngrok import ngrok
import threading

# ngrok 인증 토큰 설정 (필수!)
ngrok.set_auth_token("YOUR_AUTH_TOKEN")  # 여기에 토큰 입력

# ngrok 터널 생성
public_url = ngrok.connect(5000)
print(f"✅ 웹사이트 접속 URL: {public_url}")

# Flask 서버 백그라운드 실행
def run_app():
    app.run(port=5000, debug=False, use_reloader=False)

thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

print("\n✅ 서버 실행 중!")
```

**ngrok 토큰 발급 방법:**
1. https://dashboard.ngrok.com/signup 에서 무료 가입
2. https://dashboard.ngrok.com/get-started/your-authtoken 에서 토큰 복사
3. 위 코드의 `YOUR_AUTH_TOKEN` 부분에 붙여넣기

**장점:**
- ✅ 다른 사람과 URL 공유 가능
- ✅ 외부 네트워크에서도 접근 가능

**단점:**
- ❌ 가입 및 인증 토큰 설정 필요
- ❌ 무료 버전은 세션 제한 있음

---

## 방법 3: localtunnel 사용 (ngrok 대안)

```python
!pip install flask
!npm install -g localtunnel

# Flask 앱 코드 실행 후...

# 별도 셀에서
import threading
import subprocess

def run_app():
    app.run(port=5000, debug=False)

thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

import time
time.sleep(3)

# localtunnel 실행
!lt --port 5000
```

---

## 뉴스 데이터 업데이트하기

뉴스 항목을 추가하거나 수정하려면 `news_items` 리스트를 수정하세요:

```python
news_items.append({
    "title": "새로운 뉴스 제목",
    "time": "06:00 Dec 14",
    "tags": ["Tag1", "Tag2"],
    "color": "#1a73e8"  # 일반 뉴스: #1a73e8, 중요 뉴스: #dc3545
})
```

---

## 주의사항

1. **세션 유지**: Colab 세션이 종료되면 웹사이트도 중지됩니다
2. **접근 범위**: 방법 1(Colab 내장)은 본인만 접속 가능, 방법 2(ngrok)는 외부 공유 가능
3. **무료 제한**: ngrok 무료 버전은 월 사용량 제한이 있습니다

---

## 문제 해결

### ❌ ngrok 인증 오류 발생시
```
PyngrokNgrokError: authentication failed
```

**해결 방법:**
1. **방법 1 사용 (추천)**: 위의 "방법 1: Colab 내장 기능" 사용 - 인증 불필요
2. **ngrok 토큰 설정**:
   ```python
   from pyngrok import ngrok
   ngrok.set_auth_token("YOUR_AUTH_TOKEN")
   ```
   토큰은 https://dashboard.ngrok.com/get-started/your-authtoken 에서 발급

### ❌ 포트 이미 사용 중 오류
```python
# 포트 번호를 변경하세요
public_url = eval_js("google.colab.kernel.proxyPort(5001)")
app.run(port=5001)
```

### ❌ URL이 생성되지 않음
- 셀을 순서대로 실행했는지 확인
- 서버 시작 대기 시간(`time.sleep(2)`)을 늘려보기
- Colab 런타임 재시작 후 다시 시도

### ❌ 웹페이지가 로드되지 않음
- 생성된 URL을 **새 탭**에서 열기
- 브라우저 캐시 삭제 후 재시도
- Colab 런타임이 실행 중인지 확인
