from flask import Flask, render_template_string
from datetime import datetime

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

# HTML 템플릿
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

if __name__ == '__main__':
    # Colab에서 실행시 외부 접근 허용
    app.run(host='0.0.0.0', port=5000, debug=True)
