from flask import Flask, render_template_string, request, jsonify, send_file
import os
import requests
import uuid
import zipfile

app = Flask(__name__)

# Lấy token và repo từ Environment Variables trên Render
GITHUB_REPO = os.getenv("GH_REPO", "guidebossngu-sudo/myrobloxandanh")
GITHUB_TOKEN = os.getenv("GH_TOKEN")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Client Generator</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .box { background: #1e293b; padding: 30px; border-radius: 12px; width: 100%; max-width: 420px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; text-align: center; }
        h2 { margin-top: 0; color: #38bdf8; }
        label { font-size: 14px; color: #94a3b8; display: block; margin-top: 15px; margin-bottom: 5px; text-align: left; }
        input { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; font-size: 14px; }
        input:focus { border-color: #38bdf8; outline: none; }
        button { width: 100%; margin-top: 25px; padding: 14px; background: #2563eb; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #1d4ed8; }
        button:disabled { background: #475569; cursor: not-allowed; }
        #status { margin-top: 20px; font-size: 14px; color: #38bdf8; word-break: break-all; }
        .loader { border: 4px solid #334155; border-top: 4px solid #38bdf8; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 15px auto; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="box">
        <h2>Roblox Client Generator</h2>
        <form id="buildForm">
            <label>Mật Khẩu Xác Thực App</label>
            <input type="password" id="password" placeholder="Nhập mật khẩu..." required>

            <label>Link Download File (.exe)</label>
            <input type="url" id="download_link" placeholder="https://example.com/file.exe" required>

            <label>Số Lần Lặp (Loop)</label>
            <input type="number" id="loop" min="1" value="1" required>

            <button type="submit" id="submitBtn">Tạo File EXE</button>
        </form>

        <div class="loader" id="loader"></div>
        <div id="status"></div>
    </div>

    <script>
        document.getElementById('buildForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('submitBtn');
            const loader = document.getElementById('loader');
            const status = document.getElementById('status');

            btn.disabled = true;
            loader.style.display = 'block';
            status.innerText = "Đang gửi lệnh build sang GitHub Actions...";

            const payload = {
                password: document.getElementById('password').value,
                download_link: document.getElementById('download_link').value,
                loop: document.getElementById('loop').value
            };

            try {
                const res = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (res.ok) {
                    status.innerText = "Đã khởi tạo! Đang chờ GitHub Actions đóng gói file EXE...";
                    checkArtifact(data.build_id);
                } else {
                    status.innerText = "Lỗi: " + (data.error || "Không thể khởi tạo lệnh");
                    btn.disabled = false;
                    loader.style.display = 'none';
                }
            } catch (err) {
                status.innerText = "Lỗi kết nối tới Render Server!";
                btn.disabled = false;
                loader.style.display = 'none';
            }
        });

        async function checkArtifact(buildId) {
            const status = document.getElementById('status');
            const btn = document.getElementById('submitBtn');
            const loader = document.getElementById('loader');
            let count = 0;

            const interval = setInterval(async () => {
                count++;
                status.innerText = `Đang đóng gói file .EXE trên GitHub... (${count * 5}s)`;

                try {
                    const res = await fetch(`/check-status/${buildId}`);
                    const data = await res.json();

                    if (data.status === 'success') {
                        clearInterval(interval);
                        loader.style.display = 'none';
                        status.innerHTML = `<a href="${data.url}" target="_blank" style="color:#4ade80;font-weight:bold;font-size:16px;">TẢI FILE EXE VỀ MÁY</a>`;
                        btn.disabled = false;
                    }
                } catch (e) {}

                if (count >= 36) {
                    clearInterval(interval);
                    loader.style.display = 'none';
                    status.innerText = "Hết thời gian chờ. Hãy kiểm tra tab Actions trên GitHub!";
                    btn.disabled = false;
                }
            }, 5000);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    if not GITHUB_TOKEN:
        return jsonify({"error": "Chưa cấu hình GH_TOKEN trên Render!"}), 500

    data = request.json or {}
    build_id = str(uuid.uuid4())[:8]

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN.strip()}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "ref": "main",
        "inputs": {
            "password": str(data.get('password', '')),
            "download_link": str(data.get('download_link', '')),
            "loop": str(data.get('loop', '1')),
            "build_id": build_id
        }
    }

    dispatch_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/build.yml/dispatches"
    res = requests.post(dispatch_url, json=payload, headers=headers)

    if res.status_code == 204:
        return jsonify({"status": "started", "build_id": build_id})
    else:
        return jsonify({"error": f"GitHub API {res.status_code}: {res.text}"}), 500

@app.route('/check-status/<build_id>')
def check_status(build_id):
    if not GITHUB_TOKEN:
        return jsonify({"status": "pending"})

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN.strip()}",
        "Accept": "application/vnd.github.v3+json"
    }
    artifact_name = f"exe-{build_id}"

    artifacts_res = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts", headers=headers)
    if artifacts_res.status_code == 200:
        for art in artifacts_res.json().get("artifacts", []):
            if art["name"] == artifact_name:
                return jsonify({"status": "success", "url": f"/download/{build_id}"})

    return jsonify({"status": "pending"})

@app.route('/download/<build_id>')
def download_artifact(build_id):
    if not GITHUB_TOKEN:
        return "Lỗi Server: Chưa cấu hình GH_TOKEN", 500

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN.strip()}",
        "Accept": "application/vnd.github.v3+json"
    }
    artifact_name = f"exe-{build_id}"

    artifacts_res = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts", headers=headers)
    if artifacts_res.status_code != 200:
        return "Lỗi truy vấn GitHub API", 500

    artifact_url = None
    for art in artifacts_res.json().get("artifacts", []):
        if art["name"] == artifact_name:
            artifact_url = art["archive_download_url"]
            break

    if not artifact_url:
        return "Không tìm thấy file build!", 404

    zip_res = requests.get(artifact_url, headers=headers)
    if zip_res.status_code != 200:
        return "Không thể tải file từ GitHub API", 500

    work_dir = os.path.join("/tmp", f"build_{build_id}")
    os.makedirs(work_dir, exist_ok=True)
    zip_path = os.path.join(work_dir, "build.zip")

    with open(zip_path, "wb") as f:
        f.write(zip_res.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(work_dir)

    exe_path = os.path.join(work_dir, "RobloxAnDanh_MadeByKhoa.exe")
    if not os.path.exists(exe_path):
        return "Lỗi: Không tìm thấy file EXE sau giải nén", 500

    return send_file(exe_path, as_attachment=True, download_name="RobloxAnDanh_MadeByKhoa.exe")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
