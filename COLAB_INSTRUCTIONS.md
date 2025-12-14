# Google Colab에서 Flask 뉴스 웹사이트 실행하기

## 방법 1: 직접 코드 복사 (권장)

Google Colab 노트북에서 다음 셀들을 순서대로 실행하세요:

### 셀 1: Flask 설치
```python
!pip install flask pyngrok
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

### 셀 3: 서버 실행 (ngrok 사용 - 외부 접근 가능)
```python
from pyngrok import ngrok
import threading

# ngrok 터널 생성
public_url = ngrok.connect(5000)
print(f"✅ 웹사이트 접속 URL: {public_url}")
print(f"브라우저에서 위 URL로 접속하세요!")

# Flask 서버 백그라운드 실행
def run_app():
    app.run(port=5000, debug=False, use_reloader=False)

thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

print("\n✅ 서버 실행 중... (Ctrl+C로 종료)")
```

---

## 방법 2: Colab 기본 실행 (외부 접근 불가)

ngrok 없이 Colab 내에서만 실행하려면:

```python
!pip install flask

# 위의 Flask 앱 코드를 복사한 후

from google.colab.output import eval_js
print(eval_js("google.colab.kernel.proxyPort(5000)"))

# 별도 셀에서
app.run(port=5000, debug=True)
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

1. **ngrok 사용**: 외부에서 접속하려면 ngrok을 사용해야 합니다
2. **세션 유지**: Colab 세션이 종료되면 웹사이트도 중지됩니다
3. **무료 제한**: ngrok 무료 버전은 세션 제한이 있을 수 있습니다

---

## 문제 해결

### 포트 이미 사용 중 오류
```python
# 포트 번호를 변경하세요
public_url = ngrok.connect(5001)  # 5001로 변경
app.run(port=5001)
```

### ngrok 인증 토큰 필요
```python
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_AUTH_TOKEN")  # ngrok.com에서 무료 가입 후 토큰 발급
```

ngrok 토큰은 https://dashboard.ngrok.com/get-started/your-authtoken 에서 발급받을 수 있습니다.
