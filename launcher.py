"""
CPK Analyzer 런처 — PyInstaller exe 진입점
더블클릭하면 Streamlit 서버 시작 + 브라우저 자동 열림
"""
import sys
import os
import subprocess
import threading
import time
import webbrowser

PORT = 8501

def open_browser():
    """서버 시작 후 브라우저 열기"""
    time.sleep(3)
    webbrowser.open(f"http://localhost:{PORT}")

def main():
    # PyInstaller로 빌드된 경우 _MEIPASS에 번들 파일 존재
    if getattr(sys, "_MEIPASS", None):
        app_path = os.path.join(sys._MEIPASS, "app.py")
    else:
        app_path = os.path.join(os.path.dirname(__file__), "app.py")

    threading.Thread(target=open_browser, daemon=True).start()

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ])

if __name__ == "__main__":
    main()
