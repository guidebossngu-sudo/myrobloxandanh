from flask import Flask, render_template_string, request, send_file
import os
import requests
import time
import uuid
import zipfile

app = Flask(__name__)

# Thông tin Repository và Token GitHub
GITHUB_REPO = "guidebossngu-sudo/myrobloxandanh"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # Lấy từ Environment Variables trên Render/Koyeb

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
    if not GITHUB_TOKEN:
        return "Lỗi Server: Chưa cấu hình biến GH_TOKEN trên Render!", 500

    password = request.form.get('password')
    download_link = request.form.get('download_link')
    loop_count = request.form.get('loop')
    build_id = str(uuid.uuid4())[:8]

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN.strip()}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "ref": "main",
        "inputs": {
            "password": password,
            "download_link": download_link,
            "loop": str(loop_count),
            "build_id": build_id
        }
    }

    # Thử gửi request qua 2 đường dẫn (thư mục gốc hoặc trong my-roblox-builder)
    workflow_paths = [
        "build.yml",
        "my-roblox-builder%2F.github%2Fworkflows%2Fbuild.yml"
    ]

    res = None
    success = False

    for wf_path in workflow_paths:
        dispatch_url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{wf_path}/dispatches"
        res = requests.post(dispatch_url, json=payload, headers=headers)
        if res.status_code == 204:
            success = True
            break

    if not success and res is not None:
        return f"Lỗi GitHub API (Mã {res.status_code}): {res.text}", 500

    # 2. Ngồi chờ GitHub Actions build xong (tối đa 2.5 phút)
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
        return "Quá thời gian chờ tạo file EXE trên GitHub!", 500

    # 3. Tải file ZIP từ GitHub về Server, giải nén và gửi file .exe cho client
    zip_res = requests.get(artifact_url, headers=headers)
    work_dir = os.path.join("/tmp", f"build_{build_id}")
    os.makedirs(work_dir, exist_ok=True)
    zip_path = os.path.join(work_dir, "build.zip")

    with open(zip_path, "wb") as f:
        f.write(zip_res.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(work_dir)

    exe_path = os.path.join(work_dir, "RobloxAnDanh_MadeByKhoa.exe")
    if not os.path.exists(exe_path):
        return "Lỗi: Không tìm thấy file EXE trong gói Artifact sau khi giải nén!", 500

    return send_file(exe_path, as_attachment=True, download_name="RobloxAnDanh_MadeByKhoa.exe")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
