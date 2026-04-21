"""
CPK Analyzer 런처 — PyInstaller exe 진입점
더블클릭하면 Streamlit 서버 시작 + 브라우저 자동 열림
"""
import sys
import os
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()

    import threading
    import time
    import webbrowser

    PORT = 8501

    # PyInstaller 번들 경로
    if getattr(sys, "_MEIPASS", None):
        app_path = os.path.join(sys._MEIPASS, "app.py")
    else:
        app_path = os.path.join(os.path.dirname(__file__), "app.py")

    # 브라우저 자동 열기
    def open_browser():
        time.sleep(3)
        webbrowser.open(f"http://localhost:{PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    # subprocess 대신 Streamlit 직접 호출 (무한 재실행 방지)
    sys.argv = [
        "streamlit", "run", app_path,
        "--server.port", str(PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]

    from streamlit.web import cli as stcli
    stcli.main()
