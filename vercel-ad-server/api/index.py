from flask import Flask, jsonify, request, redirect
import os
import json

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════════
# 광고 설정 - 환경변수에서 가져오기
# ═══════════════════════════════════════════════════════════════════════

def get_ad_config():
    """환경변수에서 광고 설정을 가져옵니다."""
    
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
    
    # 기본 플레이스홀더
    if not config["top_banner"]["items"]:
        config["top_banner"]["items"] = [{
            "image_url": "https://via.placeholder.com/900x100/1a1a2e/00d4ff?text=Top+Banner",
            "click_url": "https://vercel.com"
        }]
    
    if not config["bottom_banner"]["items"]:
        config["bottom_banner"]["items"] = [{
            "image_url": "https://via.placeholder.com/900x100/1a1a2e/00d4ff?text=Bottom+Banner",
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
        .container { max-width: 1100px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 10px; color: #00d4ff; font-size: 2.2em; }
        h2 { text-align: center; margin-bottom: 30px; color: #ffd700; font-size: 1.3em; font-weight: normal; }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .card h3 { color: #00d4ff; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; }
        
        .status-ok { color: #2ecc71; }
        .status-badge { background: #238636; padding: 5px 15px; border-radius: 20px; font-size: 0.85em; display: inline-block; }
        
        /* 탭 스타일 */
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn {
            padding: 12px 25px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        .tab-btn:hover { background: rgba(255,255,255,0.2); }
        .tab-btn.active { background: #00d4ff; color: #1a1a2e; font-weight: bold; }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        /* 배너 편집 폼 */
        .banner-editor {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .banner-editor h4 { color: #ffd700; margin-bottom: 15px; }
        
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #aaa; font-size: 0.9em; }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 1px solid #444;
            border-radius: 8px;
            background: #0d1117;
            color: #fff;
            font-size: 1em;
        }
        .form-group input:focus { border-color: #00d4ff; outline: none; }
        
        /* 미리보기 */
        .preview-box {
            background: #1a1a2e;
            border: 2px dashed #444;
            border-radius: 10px;
            padding: 10px;
            margin-top: 15px;
            text-align: center;
            min-height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .preview-box img {
            max-width: 100%;
            max-height: 100px;
            border-radius: 5px;
        }
        .preview-box .placeholder { color: #666; }
        
        /* 버튼 스타일 */
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            margin-right: 10px;
            margin-top: 10px;
        }
        .btn-primary { background: #00d4ff; color: #1a1a2e; }
        .btn-primary:hover { background: #00b8e6; }
        .btn-success { background: #2ecc71; color: #fff; }
        .btn-success:hover { background: #27ae60; }
        .btn-danger { background: #e74c3c; color: #fff; }
        .btn-danger:hover { background: #c0392b; }
        .btn-secondary { background: #555; color: #fff; }
        .btn-secondary:hover { background: #666; }
        
        /* 배너 목록 */
        .banner-list { margin-top: 20px; }
        .banner-item {
            background: rgba(0,0,0,0.3);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .banner-item img { width: 150px; height: 50px; object-fit: cover; border-radius: 5px; }
        .banner-item-info { flex: 1; }
        .banner-item-info code { 
            background: #0d1117; 
            padding: 3px 8px; 
            border-radius: 4px; 
            color: #7ee787; 
            font-size: 0.85em;
            word-break: break-all;
        }
        
        /* 복사 박스 */
        .copy-box {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        .copy-box pre {
            color: #7ee787;
            font-family: monospace;
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 0.9em;
            margin: 0;
        }
        
        /* 알림 */
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-info { background: rgba(0, 212, 255, 0.2); border-left: 4px solid #00d4ff; }
        .alert-success { background: rgba(46, 204, 113, 0.2); border-left: 4px solid #2ecc71; }
        
        /* 이미지 호스팅 링크 */
        .hosting-links { margin-top: 15px; }
        .hosting-links a {
            display: inline-block;
            padding: 8px 15px;
            background: rgba(255,255,255,0.1);
            color: #00d4ff;
            text-decoration: none;
            border-radius: 5px;
            margin-right: 10px;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        .hosting-links a:hover { background: rgba(255,255,255,0.2); }
        
        /* 토글 스위치 */
        .toggle-container { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; }
        .toggle-switch {
            position: relative;
            width: 50px;
            height: 26px;
        }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #555;
            transition: 0.3s;
            border-radius: 26px;
        }
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 20px;
            width: 20px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: 0.3s;
            border-radius: 50%;
        }
        input:checked + .toggle-slider { background-color: #2ecc71; }
        input:checked + .toggle-slider:before { transform: translateX(24px); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Screen Capture Defender</h1>
        <h2>광고 관리 시스템</h2>
        
        <!-- 서버 상태 -->
        <div class="card">
            <h3>📡 서버 상태</h3>
            <p><span class="status-badge">✅ 정상 운영 중</span></p>
            <p style="margin-top: 10px; color: #aaa;">
                호스팅: Vercel (한국 CDN) | API: /api/ad-config.json
            </p>
        </div>
        
        <!-- 탭 -->
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('editor')">📝 배너 편집기</button>
            <button class="tab-btn" onclick="showTab('current')">📋 현재 설정</button>
            <button class="tab-btn" onclick="showTab('guide')">📖 설정 가이드</button>
        </div>
        
        <!-- 배너 편집기 탭 -->
        <div id="tab-editor" class="tab-content active">
            <div class="card">
                <h3>🎨 배너 편집기</h3>
                
                <div class="alert alert-info">
                    <strong>💡 사용 방법:</strong> 아래에서 이미지 URL과 링크를 입력하면 실시간으로 미리보기가 표시됩니다.
                    설정이 완료되면 하단의 "환경변수 복사" 버튼을 눌러 Vercel에 적용하세요.
                </div>
                
                <!-- 상단 배너 편집 -->
                <div class="banner-editor">
                    <h4>📍 상단 배너 (Top Banner)</h4>
                    
                    <div class="toggle-container">
                        <label class="toggle-switch">
                            <input type="checkbox" id="top_enabled" checked onchange="updatePreview()">
                            <span class="toggle-slider"></span>
                        </label>
                        <span>배너 활성화</span>
                    </div>
                    
                    <div id="top-banners">
                        <div class="form-group">
                            <label>이미지 #1 URL (900x100 권장)</label>
                            <input type="text" id="top_img_1" placeholder="https://i.imgur.com/example.png" oninput="updatePreview()">
                        </div>
                        <div class="form-group">
                            <label>클릭 링크 #1</label>
                            <input type="text" id="top_link_1" placeholder="https://example.com" oninput="updatePreview()">
                        </div>
                        <div class="preview-box" id="top_preview_1">
                            <span class="placeholder">이미지 URL을 입력하면 미리보기가 표시됩니다</span>
                        </div>
                    </div>
                    
                    <button class="btn btn-secondary" onclick="addBannerField('top')">+ 배너 추가</button>
                </div>
                
                <!-- 하단 배너 편집 -->
                <div class="banner-editor">
                    <h4>📍 하단 배너 (Bottom Banner)</h4>
                    
                    <div class="toggle-container">
                        <label class="toggle-switch">
                            <input type="checkbox" id="bottom_enabled" checked onchange="updatePreview()">
                            <span class="toggle-slider"></span>
                        </label>
                        <span>배너 활성화</span>
                    </div>
                    
                    <div id="bottom-banners">
                        <div class="form-group">
                            <label>이미지 #1 URL (900x100 권장)</label>
                            <input type="text" id="bottom_img_1" placeholder="https://i.imgur.com/example.png" oninput="updatePreview()">
                        </div>
                        <div class="form-group">
                            <label>클릭 링크 #1</label>
                            <input type="text" id="bottom_link_1" placeholder="https://example.com" oninput="updatePreview()">
                        </div>
                        <div class="preview-box" id="bottom_preview_1">
                            <span class="placeholder">이미지 URL을 입력하면 미리보기가 표시됩니다</span>
                        </div>
                    </div>
                    
                    <button class="btn btn-secondary" onclick="addBannerField('bottom')">+ 배너 추가</button>
                </div>
                
                <!-- 이미지 호스팅 안내 -->
                <div class="alert alert-info">
                    <strong>🖼️ 이미지 호스팅:</strong> 배너 이미지는 외부 URL이 필요합니다.
                    <div class="hosting-links">
                        <a href="https://imgur.com/upload" target="_blank">📷 Imgur</a>
                        <a href="https://imgbb.com/" target="_blank">📷 ImgBB</a>
                        <a href="https://postimages.org/" target="_blank">📷 PostImages</a>
                    </div>
                </div>
                
                <!-- 환경변수 출력 -->
                <h4 style="margin-top: 30px; color: #ffd700;">📋 Vercel 환경변수</h4>
                <p style="color: #aaa; margin-bottom: 10px;">아래 내용을 Vercel Dashboard > Settings > Environment Variables에 추가하세요.</p>
                
                <div class="copy-box">
                    <pre id="env-output">설정을 입력하면 환경변수가 여기에 표시됩니다.</pre>
                </div>
                
                <button class="btn btn-success" onclick="copyEnvVars()">📋 환경변수 복사</button>
                <button class="btn btn-primary" onclick="window.open('https://vercel.com/dashboard', '_blank')">🚀 Vercel Dashboard 열기</button>
            </div>
        </div>
        
        <!-- 현재 설정 탭 -->
        <div id="tab-current" class="tab-content">
            <div class="card">
                <h3>📋 현재 적용된 설정</h3>
                
                <h4 style="color: #ffd700; margin: 20px 0 15px;">📍 상단 배너</h4>
                <p>활성화: ''' + ('✅ Yes' if config['top_banner']['enabled'] else '❌ No') + '''</p>
                <div class="banner-list">
                ''' + ''.join([f'''
                    <div class="banner-item">
                        <img src="{item['image_url']}" alt="배너" onerror="this.src='https://via.placeholder.com/150x50/333/666?text=Error'">
                        <div class="banner-item-info">
                            <p>이미지: <code>{item['image_url'][:60]}...</code></p>
                            <p>링크: <code>{item['click_url']}</code></p>
                        </div>
                    </div>
                ''' for item in config['top_banner']['items']]) + '''
                </div>
                
                <h4 style="color: #ffd700; margin: 30px 0 15px;">📍 하단 배너</h4>
                <p>활성화: ''' + ('✅ Yes' if config['bottom_banner']['enabled'] else '❌ No') + '''</p>
                <div class="banner-list">
                ''' + ''.join([f'''
                    <div class="banner-item">
                        <img src="{item['image_url']}" alt="배너" onerror="this.src='https://via.placeholder.com/150x50/333/666?text=Error'">
                        <div class="banner-item-info">
                            <p>이미지: <code>{item['image_url'][:60]}...</code></p>
                            <p>링크: <code>{item['click_url']}</code></p>
                        </div>
                    </div>
                ''' for item in config['bottom_banner']['items']]) + '''
                </div>
            </div>
        </div>
        
        <!-- 설정 가이드 탭 -->
        <div id="tab-guide" class="tab-content">
            <div class="card">
                <h3>📖 설정 가이드</h3>
                
                <div class="alert alert-info">
                    <h4>1️⃣ 이미지 준비</h4>
                    <p>900 x 100 픽셀 크기의 배너 이미지를 준비합니다.</p>
                </div>
                
                <div class="alert alert-info">
                    <h4>2️⃣ 이미지 업로드</h4>
                    <p>Imgur, ImgBB 등에 이미지를 업로드하고 직접 링크(Direct Link)를 복사합니다.</p>
                    <div class="hosting-links">
                        <a href="https://imgur.com/upload" target="_blank">Imgur 업로드</a>
                        <a href="https://imgbb.com/" target="_blank">ImgBB 업로드</a>
                    </div>
                </div>
                
                <div class="alert alert-info">
                    <h4>3️⃣ 배너 편집기에서 설정</h4>
                    <p>"배너 편집기" 탭에서 이미지 URL과 클릭 링크를 입력합니다.</p>
                </div>
                
                <div class="alert alert-info">
                    <h4>4️⃣ Vercel에 환경변수 적용</h4>
                    <ol style="margin-left: 20px; margin-top: 10px; line-height: 2;">
                        <li>Vercel Dashboard 접속</li>
                        <li>이 프로젝트 선택 → Settings 탭</li>
                        <li>Environment Variables 메뉴</li>
                        <li>변수 추가 (예: TOP_BANNER_IMG_1 = https://...)</li>
                        <li>Deployments 탭 → Redeploy</li>
                    </ol>
                </div>
                
                <div class="alert alert-success">
                    <h4>✅ 완료!</h4>
                    <p>Redeploy 후 1-2분 뒤에 새 배너가 적용됩니다.</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let topBannerCount = 1;
        let bottomBannerCount = 1;
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function updatePreview() {
            // 상단 배너 미리보기
            for (let i = 1; i <= topBannerCount; i++) {
                const imgInput = document.getElementById('top_img_' + i);
                const previewBox = document.getElementById('top_preview_' + i);
                if (imgInput && previewBox) {
                    if (imgInput.value) {
                        previewBox.innerHTML = '<img src="' + imgInput.value + '" onerror="this.parentElement.innerHTML=\\'<span class=placeholder>이미지를 불러올 수 없습니다</span>\\'">';
                    } else {
                        previewBox.innerHTML = '<span class="placeholder">이미지 URL을 입력하면 미리보기가 표시됩니다</span>';
                    }
                }
            }
            
            // 하단 배너 미리보기
            for (let i = 1; i <= bottomBannerCount; i++) {
                const imgInput = document.getElementById('bottom_img_' + i);
                const previewBox = document.getElementById('bottom_preview_' + i);
                if (imgInput && previewBox) {
                    if (imgInput.value) {
                        previewBox.innerHTML = '<img src="' + imgInput.value + '" onerror="this.parentElement.innerHTML=\\'<span class=placeholder>이미지를 불러올 수 없습니다</span>\\'">';
                    } else {
                        previewBox.innerHTML = '<span class="placeholder">이미지 URL을 입력하면 미리보기가 표시됩니다</span>';
                    }
                }
            }
            
            // 환경변수 업데이트
            generateEnvVars();
        }
        
        function addBannerField(position) {
            let count, container;
            if (position === 'top') {
                topBannerCount++;
                count = topBannerCount;
                container = document.getElementById('top-banners');
            } else {
                bottomBannerCount++;
                count = bottomBannerCount;
                container = document.getElementById('bottom-banners');
            }
            
            const html = `
                <hr style="border: 0; border-top: 1px solid #333; margin: 20px 0;">
                <div class="form-group">
                    <label>이미지 #${count} URL</label>
                    <input type="text" id="${position}_img_${count}" placeholder="https://i.imgur.com/example.png" oninput="updatePreview()">
                </div>
                <div class="form-group">
                    <label>클릭 링크 #${count}</label>
                    <input type="text" id="${position}_link_${count}" placeholder="https://example.com" oninput="updatePreview()">
                </div>
                <div class="preview-box" id="${position}_preview_${count}">
                    <span class="placeholder">이미지 URL을 입력하면 미리보기가 표시됩니다</span>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        }
        
        function generateEnvVars() {
            let envVars = [];
            
            // 상단 배너
            const topEnabled = document.getElementById('top_enabled').checked;
            envVars.push('TOP_BANNER_ENABLED=' + topEnabled);
            
            for (let i = 1; i <= topBannerCount; i++) {
                const img = document.getElementById('top_img_' + i)?.value || '';
                const link = document.getElementById('top_link_' + i)?.value || '';
                if (img) {
                    envVars.push('TOP_BANNER_IMG_' + i + '=' + img);
                    envVars.push('TOP_BANNER_LINK_' + i + '=' + link);
                }
            }
            
            // 하단 배너
            const bottomEnabled = document.getElementById('bottom_enabled').checked;
            envVars.push('BOTTOM_BANNER_ENABLED=' + bottomEnabled);
            
            for (let i = 1; i <= bottomBannerCount; i++) {
                const img = document.getElementById('bottom_img_' + i)?.value || '';
                const link = document.getElementById('bottom_link_' + i)?.value || '';
                if (img) {
                    envVars.push('BOTTOM_BANNER_IMG_' + i + '=' + img);
                    envVars.push('BOTTOM_BANNER_LINK_' + i + '=' + link);
                }
            }
            
            document.getElementById('env-output').textContent = envVars.join('\\n');
        }
        
        function copyEnvVars() {
            const envText = document.getElementById('env-output').textContent;
            navigator.clipboard.writeText(envText).then(() => {
                alert('환경변수가 클립보드에 복사되었습니다!\\n\\nVercel Dashboard > Settings > Environment Variables에 붙여넣기 하세요.');
            });
        }
        
        // 초기화
        generateEnvVars();
    </script>
</body>
</html>'''
    
    return html


# Vercel serverless handler
app = app
