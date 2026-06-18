import requests
import re
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# impact words:
SENSITIVE_KEYWORDS = [
    "admin", "panel", "test", "dev", "debug",
    "api", "key", "token", "secret", "password",
    "internal", "backup", "staging", "todo", "fixme"
]

# regex:
PATTERNS = {
    "html": r"<!--(.*?)-->",
    "css_js_block": r"/\*(.*?)\*/",
    "js_line": r"//(.*)"
}

# test with header:
def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0 CommentHunter"}
    r = requests.get(url, headers=headers, timeout=10)
    return r.text

# extract:
def extract_comments(text):
    comments = []

    comments += re.findall(PATTERNS["html"], text, re.DOTALL)

    comments += re.findall(PATTERNS["css_js_block"], text, re.DOTALL)

    comments += re.findall(PATTERNS["js_line"], text)


    return [c.strip() for c in comments if c.strip()]


def extract_assets(base_url, html):
    soup = BeautifulSoup(html, "html.parser")

    assets = []

    for script in soup.find_all("script", src=True):
        assets.append(urljoin(base_url, script["src"]))

    for link in soup.find_all("link", rel="stylesheet"):
        if link.get("href"):
            assets.append(urljoin(base_url, link["href"]))

    return assets

    # impect analyze:
def analyze_comments(comments):
    results = []

    for c in comments:
        score = 0

        found_keywords = []

        for k in SENSITIVE_KEYWORDS:
            if k.lower() in c.lower():
                score += 1
                found_keywords.append(k)


        results.append({
            "text": c,
            "score": score,
            "keywords": found_keywords
        })

    #sort
    return sorted(results, key=lambda x: x["score"], reverse=True)


def fetch_asset_comments(url):
    try:
        content = fetch(url)
        return extract_comments(content)
    except:
        return []

    # create HTML:
def generate_html_report(url, data):
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CommentHunter Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }}
            
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                overflow: hidden;
            }}
            
            header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            header .target-url {{
                font-size: 1em;
                opacity: 0.95;
                word-break: break-all;
            }}
            
            .content {{
                padding: 40px 30px;
            }}
            
            .stats {{
                display: flex;
                justify-content: space-around;
                margin-bottom: 40px;
                flex-wrap: wrap;
                gap: 20px;
            }}
            
            .stat-box {{
                text-align: center;
                padding: 20px;
                border-radius: 8px;
                flex: 1;
                min-width: 150px;
            }}
            
            .stat-box.high {{
                background: #fee;
                border-left: 4px solid #e74c3c;
            }}
            
            .stat-box.medium {{
                background: #fffaf0;
                border-left: 4px solid #f39c12;
            }}
            
            .stat-box.low {{
                background: #f5f5f5;
                border-left: 4px solid #95a5a6;
            }}
            
            .stat-box h3 {{
                font-size: 2em;
                margin-bottom: 5px;
            }}
            
            .stat-box p {{
                font-size: 0.9em;
                color: #666;
            }}
            
            .comments-section {{
                border-top: 2px solid #ecf0f1;
                padding-top: 30px;
            }}
            
            .comments-section h2 {{
                color: #2c3e50;
                margin-bottom: 30px;
                font-size: 1.5em;
            }}
            
            .comment-item {{
                margin-bottom: 25px;
                border-radius: 8px;
                overflow: hidden;
                border-left: 5px solid #95a5a6;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease;
            }}
            
            .comment-item:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }}
            
            .comment-item.high {{
                background: #fee;
                border-left-color: #e74c3c;
            }}
            
            .comment-item.medium {{
                background: #fffaf0;
                border-left-color: #f39c12;
            }}
            
            .comment-item.low {{
                background: #f9f9f9;
                border-left-color: #95a5a6;
            }}
            
            .comment-header {{
                padding: 15px 20px;
                background: rgba(0, 0, 0, 0.02);
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }}
            
            .comment-badge {{
                display: inline-block;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            
            .badge-high {{
                background: #e74c3c;
                color: white;
            }}
            
            .badge-medium {{
                background: #f39c12;
                color: white;
            }}
            
            .badge-low {{
                background: #95a5a6;
                color: white;
            }}
            
            .score-display {{
                font-weight: 700;
                font-size: 1.1em;
            }}
            
            .comment-body {{
                padding: 20px;
            }}
            
            .comment-text {{
                background: white;
                padding: 15px;
                border-radius: 6px;
                border: 1px solid #ecf0f1;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 0.95em;
                line-height: 1.5;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            
            .keywords {{
                margin-top: 15px;
                padding-top: 15px;
                border-top: 1px solid rgba(0, 0, 0, 0.1);
            }}
            
            .keywords strong {{
                color: #2c3e50;
                margin-right: 10px;
            }}
            
            .keyword-tag {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                margin: 4px 4px 4px 0;
                font-size: 0.85em;
            }}
            
            footer {{
                background: #f8f9fa;
                padding: 20px 30px;
                text-align: center;
                color: #7f8c8d;
                border-top: 1px solid #ecf0f1;
                font-size: 0.9em;
            }}
            
            @media (prefers-color-scheme: dark) {{
                body {{
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                }}
                
                .container {{
                    background: #0f3460;
                    color: #e0e0e0;
                }}
                
                header {{
                    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
                }}
                
                .content {{
                    color: #e0e0e0;
                }}
                
                .comments-section h2 {{
                    color: #e0e0e0;
                }}
                
                .stat-box {{
                    color: #e0e0e0;
                }}
                
                .stat-box.high {{
                    background: rgba(231, 76, 60, 0.2);
                }}
                
                .stat-box.medium {{
                    background: rgba(243, 156, 18, 0.2);
                }}
                
                .stat-box.low {{
                    background: rgba(149, 165, 166, 0.2);
                }}
                
                .stat-box p {{
                    color: #b0b0b0;
                }}
                
                .comments-section {{
                    border-top-color: #16213e;
                }}
                
                .comment-item.high {{
                    background: rgba(231, 76, 60, 0.15);
                }}
                
                .comment-item.medium {{
                    background: rgba(243, 156, 18, 0.15);
                }}
                
                .comment-item.low {{
                    background: rgba(149, 165, 166, 0.15);
                }}
                
                .comment-item {{
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
                }}
                
                .comment-item:hover {{
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
                }}
                
                .comment-header {{
                    background: rgba(0, 0, 0, 0.3);
                }}
                
                .comment-text {{
                    background: #1a1a2e;
                    border-color: #16213e;
                    color: #e0e0e0;
                }}
                
                .keywords strong {{
                    color: #e0e0e0;
                }}
                
                .keywords {{
                    border-top-color: rgba(255, 255, 255, 0.1);
                }}
                
                footer {{
                    background: #16213e;
                    color: #909090;
                    border-top-color: #0f3460;
                }}
                
                .score-display {{
                    color: #e0e0e0;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔍 CommentHunter Report</h1>
                <div class="target-url">Target: {url}</div>
            </header>
            
            <div class="content">
    """

    # Calculate statistics
    high_count = sum(1 for item in data if item["score"] >= 2)
    medium_count = sum(1 for item in data if item["score"] == 1)
    low_count = sum(1 for item in data if item["score"] == 0)
    
    html += f"""
                <div class="stats">
                    <div class="stat-box high">
                        <h3>{high_count}</h3>
                        <p>High Risk</p>
                    </div>
                    <div class="stat-box medium">
                        <h3>{medium_count}</h3>
                        <p>Medium Risk</p>
                    </div>
                    <div class="stat-box low">
                        <h3>{low_count}</h3>
                        <p>Low Risk</p>
                    </div>
                </div>
                
                <div class="comments-section">
                    <h2>Found Comments ({len(data)} total)</h2>
    """

    for item in data:
        cls = "low"
        badge_cls = "badge-low"
        risk_level = "Low Risk"
        
        if item["score"] >= 2:
            cls = "high"
            badge_cls = "badge-high"
            risk_level = "High Risk"
        elif item["score"] == 1:
            cls = "medium"
            badge_cls = "badge-medium"
            risk_level = "Medium Risk"

        html += f"""
                    <div class="comment-item {cls}">
                        <div class="comment-header">
                            <span class="comment-badge {badge_cls}">{risk_level}</span>
                            <span class="score-display">Risk Score: {item['score']}</span>
                        </div>
                        <div class="comment-body">
                            <div class="comment-text">{item['text']}</div>
        """
        
        if item["keywords"]:
            html += f"""
                            <div class="keywords">
                                <strong>Sensitive Keywords Found:</strong>
        """
            for keyword in item["keywords"]:
                html += f'<span class="keyword-tag">{keyword}</span>'
            html += """
                            </div>
        """
        
        html += """
                        </div>
                    </div>
        """

    html += """
                </div>
            </div>
            
            <footer>
                <p>Generated by CommentHunter - Bug Bounty Comment Extractor</p>
            </footer>
        </div>
    </body>
    </html>
    """

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("[+] HTML report saved as report.html")


def main():
    parser = argparse.ArgumentParser(description="CommentHunter - Bug Bounty Comment Extractor")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--jc", action="store_true", help="Fetch JS/CSS files too")

    args = parser.parse_args()

    print(f"[+] Fetching {args.url}")
    html = fetch(args.url)

    comments = extract_comments(html)

    # jc mode: fetch js&css files
    if args.jc:
        print("[+] jc mode enabled: fetching assets...")
        assets = extract_assets(args.url, html)

        for a in assets:
            print(f"[+] Fetching asset: {a}")
            comments += fetch_asset_comments(a)

    analyzed = analyze_comments(comments)

    # com output
    for item in analyzed:
        tag = "[HIGH]" if item["score"] >= 2 else "[MED]" if item["score"] == 1 else "[LOW]"
        print(f"{tag} {item['text']}")
        if item["keywords"]:
            print(f"     -> keywords: {', '.join(item['keywords'])}")

    # htmlm report
    if args.html:
        generate_html_report(args.url, analyzed)
ls

if __name__ == "__main__":
    main()

# by MRscript-up
"""
using:
/\/\/\/\/\/\/\/\/\
python Comment_Finder.py https://google.com/ --jc
/\/\/\/\/\/\/\/\/\
HTML stdout:
--html
/\/\/\/\/\/\/\/\/\
"""


