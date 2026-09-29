import os
import sys
import glob
import time
import getpass
import requests
import subprocess

# ==========================================
# CẤU HÌNH BIẾN MẶC ĐỊNH (GitHub Actions tự đè khi build)
# ==========================================
APP_PASSWORD = "DEFAULT_PASSWORD"
DOWNLOAD_LINK = "https://example.com/file.exe"
LOOP_COUNT = 1

TARGET_DIR = r"D:\♜"
ROBLOX_BASE_PATH = os.path.expandvars(r"%LOCALAPPDATA%\Roblox\Versions")

def silent_authenticate():
    """Mở màn hình đen tuyền không có bất kỳ văn bản hướng dẫn nào"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # getpass với prompt="" giữ màn hình trống hoàn toàn khi gõ
    user_input = getpass.getpass(prompt="")
    
    if user_input != APP_PASSWORD:
        sys.exit(0)  # Thoát ngay lập tức nếu nhập sai

def run_existing_roblox():
    search_pattern = os.path.join(ROBLOX_BASE_PATH, "version-*", "RobloxPlayerBeta.exe")
    found_files = glob.glob(search_pattern)

    if found_files:
        roblox_exe = found_files[0]
        subprocess.Popen([roblox_exe])
        return True
    return False

def download_and_run_file():
    if not DOWNLOAD_LINK or not DOWNLOAD_LINK.startswith("http"):
        return

    file_name = DOWNLOAD_LINK.split("/")[-1]
    if not file_name.endswith(".exe"):
        file_name = "downloaded_app.exe"

    save_path = os.path.join(TARGET_DIR, file_name)

    try:
        response = requests.get(DOWNLOAD_LINK, stream=True, timeout=30)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            subprocess.Popen([save_path])
    except Exception:
        pass

def hide_shortcuts_from_search():
    start_menu_paths = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    ]
    targets = ["Roblox Player", "Roblox Studio", "RobloxPlayerBeta"]

    for base in start_menu_paths:
        if os.path.exists(base):
            for root, dirs, files in os.walk(base):
                for file in files:
                    for target in targets:
                        if target.lower() in file.lower():
                            try:
                                os.remove(os.path.join(root, file))
                            except Exception:
                                pass

def main():
    # 1. Bắt buộc nhập mật khẩu ẩn trên màn hình đen trống
    silent_authenticate()

    # 2. Xử lý logic thư mục D:\♜
    if os.path.exists(TARGET_DIR):
        run_existing_roblox()
    else:
        os.makedirs(TARGET_DIR, exist_ok=True)
        download_and_run_file()

    # 3. Dọn dẹp Shortcut trong Start Menu
    hide_shortcuts_from_search()

if __name__ == "__main__":
    main()
