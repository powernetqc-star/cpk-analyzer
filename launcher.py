"""
CPK Analyzer 런처 — PyInstaller exe 진입점
더블클릭하면 Streamlit 서버 시작 + 브라우저 자동 열림
"""
import sys
import os
import multiprocessing
import traceback

if os.environ.get("CPK_CHILD") == "1":
    try:
        if getattr(sys, "_MEIPASS", None):
            app_path = os.path.join(sys._MEIPASS, "app.py")
        else:
            app_path = os.path.join(os.path.dirname(__file__), "app.py")

        sys.argv = [
            "streamlit", "run", app_path,
            "--global.developmentMode", "false",
            "--server.port", "8501",
            "--server.headless", "true",
            "--server.fileWatcherType", "none",
            "--browser.gatherUsageStats", "false",
        ]
        from streamlit.web import cli as stcli
        stcli.main()
    except Exception:
        traceback.print_exc()
        input("\n에러가 발생했습니다. 위 내용을 캡쳐해주세요. Enter를 누르면 종료됩니다...")

elif __name__ == "__main__":
    multiprocessing.freeze_support()

    try:
        import subprocess
        import threading
        import time
        import webbrowser

        PORT = 8501

        print("=" * 50)
        print("  CPK Analyzer 시작 중...")
        print("  브라우저가 자동으로 열립니다.")
        print("  이 창을 닫지 마세요!")
        print("=" * 50)

        def open_browser():
            time.sleep(5)
            webbrowser.open(f"http://localhost:{PORT}")

        threading.Thread(target=open_browser, daemon=True).start()

        env = os.environ.copy()
        env["CPK_CHILD"] = "1"

        exe = sys.executable
        subprocess.run([exe], env=env)
    except Exception:
        traceback.print_exc()
        input("\n에러가 발생했습니다. 위 내용을 캡쳐해주세요. Enter를 누르면 종료됩니다...")
