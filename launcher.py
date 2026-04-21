"""
CPK Analyzer 런처 — PyInstaller exe 진입점
더블클릭하면 Streamlit 서버 시작 + 브라우저 자동 열림
"""
import sys
import os
import multiprocessing

# PyInstaller가 exe를 재실행할 때 무한루프 방지
if os.environ.get("CPK_CHILD") == "1":
    # 자식 프로세스 → Streamlit 직접 실행
    if getattr(sys, "_MEIPASS", None):
        app_path = os.path.join(sys._MEIPASS, "app.py")
    else:
        app_path = os.path.join(os.path.dirname(__file__), "app.py")

    sys.argv = [
        "streamlit", "run", app_path,
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
    from streamlit.web import cli as stcli
    stcli.main()

elif __name__ == "__main__":
    multiprocessing.freeze_support()

    import subprocess
    import threading
    import time
    import webbrowser

    PORT = 8501

    def open_browser():
        time.sleep(4)
        webbrowser.open(f"http://localhost:{PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    # 환경변수 설정 후 자기 자신을 한 번만 재실행
    env = os.environ.copy()
    env["CPK_CHILD"] = "1"

    exe = sys.executable
    subprocess.run([exe], env=env)
