from flask import Flask, jsonify, request, redirect
import os
import json

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════════
# 광고 설정 - 환경변수 또는 하드코딩
# Vercel Dashboard > Settings > Environment Variables 에서 설정
# ═══════════════════════════════════════════════════════════════════════

def get_ad_config():
    """환경변수에서 광고 설정을 가져옵니다."""
    
    # 환경변수에서 JSON 설정 가져오기 (있으면)
    config_json = os.environ.get('AD_CONFIG_JSON')
    if config_json:
        try:
            return json.loads(config_json)
        except:
            pass
    
    # 개별 환경변수에서 가져오기
    config = {
        "top_banner": {
            "enabled": os.environ.get("TOP_BANNER_ENABLED", "true").lower() == "true",
            "items": [],
            "clicks": 0
        },
        "bottom_banner": {
            "enabled": os.environ.get("BOTTOM_BANNER_ENABLED", "true").lower() == "true",
            "items": [],
            "clicks": 0
        }
    }
    
    # 상단 배너 아이템들 (최대 5개)
    for i in range(1, 6):
        img = os.environ.get(f"TOP_BANNER_IMG_{i}")
        link = os.environ.get(f"TOP_BANNER_LINK_{i}", "")
        if img:
            config["top_banner"]["items"].append({
                "image_url": img,
                "click_url": link
            })
    
    # 하단 배너 아이템들 (최대 5개)
    for i in range(1, 6):
        img = os.environ.get(f"BOTTOM_BANNER_IMG_{i}")
        link = os.environ.get(f"BOTTOM_BANNER_LINK_{i}", "")
        if img:
            config["bottom_banner"]["items"].append({
                "image_url": img,
                "click_url": link
            })
    
    # 기본 플레이스홀더 (아무것도 설정 안된 경우)
    if not config["top_banner"]["items"]:
        config["top_banner"]["items"] = [{
            "image_url": "https://via.placeholder.com/900x100/1a1a2e/00d4ff?text=Top+Banner+-+Set+Environment+Variables",
            "click_url": "https://vercel.com"
        }]
    
    if not config["bottom_banner"]["items"]:
        config["bottom_banner"]["items"] = [{
            "image_url": "https://via.placeholder.com/900x100/1a1a2e/00d4ff?text=Bottom+Banner+-+Set+Environment+Variables",
            "click_url": "https://vercel.com"
        }]
    
    return config


# ═══════════════════════════════════════════════════════════════════════
# API 라우트
# ═══════════════════════════════════════════════════════════════════════

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Screen Capture Defender Ad Server",
        "endpoints": {
            "ad_config": "/api/ad-config.json",
            "admin": "/admin"
        }
    })


@app.route('/api/ad-config.json')
@app.route('/api/ad-config')
def ad_config():
    config = get_ad_config()
    response = jsonify(config)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 's-maxage=60, stale-while-revalidate'
    return response


@app.route('/click/<position>/<int:index>')
def ad_click(position, index):
    config = get_ad_config()
    key = f"{position}_banner"
    
    if key in config and 0 <= index < len(config[key]['items']):
        target_url = config[key]['items'][index].get('click_url', 'https://google.com')
        return redirect(target_url)
    
    return "Link not found", 404


@app.route('/admin')
def admin_page():
    config = get_ad_config()
    
    html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Screen Capture Defender - 광고 관리</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; color: #00d4ff; }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .card h2 { color: #00d4ff; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; }
        
        .status-ok { color: #2ecc71; }
        .status-badge { background: #238636; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; }
        
        .banner-item {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .banner-item img { max-width: 100%; height: auto; border-radius: 5px; margin: 10px 0; }
        .banner-item code { 
            background: #0d1117; 
            padding: 5px 10px; 
            border-radius: 4px; 
            color: #7ee787; 
            word-break: break-all;
            display: block;
            margin: 5px 0;
        }
        
        .info-box {
            background: rgba(0, 212, 255, 0.1);
            border-left: 4px solid #00d4ff;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        .info-box h3 { color: #00d4ff; margin-bottom: 10px; }
        .info-box ol { margin-left: 20px; line-height: 2; }
        .info-box a { color: #00d4ff; }
        
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: #00d4ff; }
        td code { background: #0d1117; padding: 3px 8px; border-radius: 4px; color: #7ee787; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Screen Capture Defender<br>광고 관리 시스템</h1>
        
        <div class="card">
            <h2>📡 서버 상태</h2>
            <p class="status-ok">
                <span class="status-badge">✅ 정상 운영 중</span>
            </p>
            <p style="margin-top: 15px; color: #aaa;">
                호스팅: Vercel (한국 CDN) | API: /api/ad-config.json
            </p>
        </div>
        
        <div class="card">
            <h2>📍 상단 배너 (Top Banner)</h2>
            <p>활성화: ''' + ('✅ Yes' if config['top_banner']['enabled'] else '❌ No') + '''</p>
            <p>등록된 이미지: ''' + str(len(config['top_banner']['items'])) + '''개</p>
            ''' + ''.join([f'''
            <div class="banner-item">
                <p><strong>#{i+1}</strong></p>
                <img src="{item['image_url']}" alt="배너">
                <p>이미지: <code>{item['image_url']}</code></p>
                <p>링크: <code>{item['click_url']}</code></p>
            </div>
            ''' for i, item in enumerate(config['top_banner']['items'])]) + '''
        </div>
        
        <div class="card">
            <h2>📍 하단 배너 (Bottom Banner)</h2>
            <p>활성화: ''' + ('✅ Yes' if config['bottom_banner']['enabled'] else '❌ No') + '''</p>
            <p>등록된 이미지: ''' + str(len(config['bottom_banner']['items'])) + '''개</p>
            ''' + ''.join([f'''
            <div class="banner-item">
                <p><strong>#{i+1}</strong></p>
                <img src="{item['image_url']}" alt="배너">
                <p>이미지: <code>{item['image_url']}</code></p>
                <p>링크: <code>{item['click_url']}</code></p>
            </div>
            ''' for i, item in enumerate(config['bottom_banner']['items'])]) + '''
        </div>
        
        <div class="card">
            <h2>⚙️ 배너 설정 변경 방법</h2>
            
            <div class="info-box">
                <h3>Vercel Dashboard에서 환경변수 수정</h3>
                <ol>
                    <li><a href="https://vercel.com/dashboard" target="_blank">Vercel Dashboard</a> 접속</li>
                    <li>이 프로젝트 선택 → <strong>Settings</strong> 탭</li>
                    <li><strong>Environment Variables</strong> 메뉴</li>
                    <li>아래 변수들을 추가/수정</li>
                    <li><strong>Deployments</strong> 탭 → 최신 배포 → <strong>⋮</strong> → <strong>Redeploy</strong></li>
                </ol>
            </div>
            
            <h3 style="margin-top: 25px; color: #ffd700;">환경변수 목록</h3>
            <table>
                <tr><th>변수명</th><th>설명</th></tr>
                <tr><td><code>TOP_BANNER_ENABLED</code></td><td>상단 배너 활성화 (true/false)</td></tr>
                <tr><td><code>TOP_BANNER_IMG_1</code></td><td>상단 배너 이미지 1 URL</td></tr>
                <tr><td><code>TOP_BANNER_LINK_1</code></td><td>상단 배너 1 클릭 링크</td></tr>
                <tr><td><code>TOP_BANNER_IMG_2</code></td><td>상단 배너 이미지 2 URL (선택)</td></tr>
                <tr><td><code>TOP_BANNER_LINK_2</code></td><td>상단 배너 2 클릭 링크 (선택)</td></tr>
                <tr><td><code>BOTTOM_BANNER_ENABLED</code></td><td>하단 배너 활성화 (true/false)</td></tr>
                <tr><td><code>BOTTOM_BANNER_IMG_1</code></td><td>하단 배너 이미지 1 URL</td></tr>
                <tr><td><code>BOTTOM_BANNER_LINK_1</code></td><td>하단 배너 1 클릭 링크</td></tr>
            </table>
            
            <div class="info-box" style="margin-top: 20px;">
                <h3>🖼️ 이미지 호스팅 추천</h3>
                <p>배너 이미지는 외부 URL이 필요합니다:</p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li><a href="https://imgur.com" target="_blank">Imgur</a> - 무료, 직접 링크</li>
                    <li><a href="https://imgbb.com" target="_blank">ImgBB</a> - 무료 이미지 호스팅</li>
                    <li>GitHub Raw URL</li>
                </ul>
                <p style="margin-top: 10px;"><strong>권장 사이즈:</strong> 900 x 100 픽셀</p>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    return html


# Vercel serverless handler
app = app
