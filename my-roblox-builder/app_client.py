import os
import sys
import time
import requests

# ==========================================
# CẤU HÌNH BIẾN MẶC ĐỊNH
# (Các giá trị này sẽ được GitHub Actions thay thế tự động khi build)
# ==========================================
APP_PASSWORD = "DEFAULT_PASSWORD"
DOWNLOAD_LINK = "https://example.com/file.zip"
LOOP_COUNT = 1

def process_task():
    """
    Hàm thực thi công việc chính của Client dựa trên số lần lặp truyền vào.
    """
    # Ép kiểu an toàn sang số nguyên
    try:
        max_loop = int(LOOP_COUNT)
    except (ValueError, TypeError):
        max_loop = 1

    print(f"[+] Starting client task with LOOP_COUNT = {max_loop}")

    # Thực hiện chính xác max_loop lần
    for i in range(max_loop):
        print(f"[*] Processing iteration {i + 1}/{max_loop}...")

        # Xử lý link download nếu có
        if DOWNLOAD_LINK and DOWNLOAD_LINK.startswith("http"):
            try:
                # Thêm logic xử lý/tải file tại đây nếu cần
                pass
            except Exception as e:
                print(f"[-] Error during processing: {e}")

        # Tạm dừng 1 giây giữa các lần lặp
        time.sleep(1)

    print("[+] Task completed successfully!")

def main():
    # Kiểm tra mật khẩu (nếu mật khẩu rỗng sẽ dừng)
    if not APP_PASSWORD:
        sys.exit(1)

    # Chạy tác vụ chính
    process_task()

if __name__ == "__main__":
    main()
