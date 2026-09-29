from flask import Flask, render_template_string, request, send_file
import os
import requests
import time
import uuid
import zipfile

app = Flask(__name__)

# ĐIỀN ĐÚNG USERNAME VÀ REPO GITHUB CỦA BẠN VÀO ĐÂY (VD: "khoa/roblox-builder")
GITHUB_REPO = "TÊN_USERNAME_CỦA_BẠN/TÊN_REPO_CỦA_BẠN"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # Sẽ lấy từ Environment Variable trên Render

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Custom App Generator</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .box { background: #1e293b; padding: 30px; border-radius: 12px; width: 100%; max-width: 420px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }
        h2 { margin-top: 0; color: #38bdf8; text-align: center; }
        label { font-size: 14px; color: #94a3b8; display: block; margin-top: 15px; margin-bottom: 5px; }
        input { width: 100%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; font-size: 14px; }
        input:focus { border-color: #38bdf8; outline: none; }
        button { width: 100%; margin-top: 25px; padding: 14px; background: #2563eb; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 15px; transition: background 0.2s; }
        button:hover { background: #1d4ed8; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Tạo App Client</h2>
        <form action="/generate" method="POST">
            <label>Mật Khẩu App</label>
            <input type="password" name="password" placeholder="Nhập mật khẩu mở app..." required>

            <label>Link Download File</label>
            <input type="url" name="download_link" placeholder="https://example.com/file.zip" required>

            <label>Số Lần Loop</label>
            <input type="number" name="loop" placeholder="Ví dụ: 5" min="1" value="1" required>

            <button type="submit">tai roblox an danh made by khoa</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    password = request.form.get('password')
    download_link = request.form.get('download_link')
    loop_count = request.form.get('loop')
    build_id = str(uuid.uuid4())[:8]

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Gửi lệnh yêu cầu GitHub Actions bắt đầu build EXE
    dispatch_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/build.yml/dispatches"
    payload = {
        "ref": "main",
        "inputs": {
            "password": password,
            "download_link": download_link,
            "loop": str(loop_count),
            "build_id": build_id
        }
    }
    
    res = requests.post(dispatch_url, json=payload, headers=headers)
    if res.status_code != 204:
        return f"Lỗi khởi chạy build trên GitHub: {res.text}", 500

    # 2. Web ngồi chờ GitHub build xong (khoảng 1 - 1.5 phút)
    artifact_name = f"exe-{build_id}"
    artifact_url = None
    
    for _ in range(30):
        time.sleep(5)
        artifacts_res = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/actions/artifacts", headers=headers)
        if artifacts_res.status_code == 200:
            artifacts = artifacts_res.json().get("artifacts", [])
            for art in artifacts:
                if art["name"] == artifact_name:
                    artifact_url = art["archive_download_url"]
                    break
        if artifact_url:
            break

    if not artifact_url:
        return "Quá thời gian chờ tạo file EXE!", 500

    # 3. Tải file ZIP từ GitHub về Web Server, giải nén và trả file .EXE cho người dùng
    zip_res = requests.get(artifact_url, headers=headers)
    work_dir = os.path.join("/tmp", f"build_{build_id}")
    os.makedirs(work_dir, exist_ok=True)
    zip_path = os.path.join(work_dir, "build.zip")

    with open(zip_path, "wb") as f:
        f.write(zip_res.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(work_dir)

    exe_path = os.path.join(work_dir, "RobloxAnDanh_MadeByKhoa.exe")
    return send_file(exe_path, as_attachment=True, download_name="RobloxAnDanh_MadeByKhoa.exe")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
