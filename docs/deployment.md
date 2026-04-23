# 배포 가이드

## 1. 개발 환경 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

---

## 2. Windows EXE 빌드

### 2.1 빌드 원리
PyInstaller가 Python + 모든 라이브러리를 하나의 폴더로 묶음.
사용자 PC에 Python 설치 불필요.

### 2.2 GitHub Actions 자동 빌드

`main` 브랜치에 push하면 자동으로 Windows exe 빌드됨.

**워크플로우 파일**: `.github/workflows/build-exe.yml`

```yaml
name: Build Windows EXE
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build EXE
        shell: cmd
        run: >-
          pyinstaller --noconfirm --onedir --console --name CPK_Analyzer
          --add-data "app.py;."
          --copy-metadata streamlit
          --copy-metadata altair
          --copy-metadata pandas
          --copy-metadata numpy
          --collect-all streamlit
          --collect-submodules scipy
          --collect-data matplotlib
          launcher.py
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: CPK_Analyzer_Windows
          path: dist/CPK_Analyzer/
```

### 2.3 빌드 옵션 설명

| 옵션 | 이유 |
|------|------|
| `--onedir` | 파일들을 하나의 폴더에 모음 (onefile보다 안정적) |
| `--console` | 콘솔 창 표시 (에러 확인 가능) |
| `--add-data "app.py;."` | Streamlit이 실행할 메인 앱 파일 포함 |
| `--copy-metadata streamlit` | Streamlit 버전 메타데이터 (없으면 PackageNotFoundError) |
| `--copy-metadata altair/pandas/numpy` | 의존 패키지 메타데이터 |
| `--collect-all streamlit` | Streamlit의 모든 파일 (HTML, CSS, JS 등) |
| `--collect-submodules scipy` | scipy C 확장 모듈 (gamma, stats 등) |
| `--collect-data matplotlib` | matplotlib 폰트 파일 |

### 2.4 다운로드 방법
1. https://github.com/powernetqc-star/cpk-analyzer/actions 접속
2. 최신 빌드 (초록 체크) 클릭
3. 하단 Artifacts → `CPK_Analyzer_Windows` 다운로드
4. ZIP 압축 해제 → `CPK_Analyzer.exe` 실행

---

## 3. Launcher 구조 (launcher.py)

PyInstaller exe에서 Streamlit을 안정적으로 실행하기 위한 구조:

```
CPK_Analyzer.exe 실행 (부모 프로세스)
    │
    ├── "CPK Analyzer 시작 중..." 콘솔 메시지 표시
    ├── 5초 후 브라우저 자동 열기 (스레드)
    │
    └── CPK_CHILD=1 환경변수 설정 후 자기 자신 재실행 (자식 프로세스)
         │
         └── Streamlit 서버 시작
              --global.developmentMode false
              --server.port 8501
              --server.headless true
              --server.fileWatcherType none
              --browser.gatherUsageStats false
```

### 해결한 문제들

| 문제 | 원인 | 해결 |
|------|------|------|
| 창 30개 이상 열림 | subprocess가 exe를 무한 재실행 | `CPK_CHILD` 환경변수 가드 |
| PackageNotFoundError | 패키지 메타데이터 누락 | `--copy-metadata`, `--collect-all` |
| developmentMode 충돌 | PyInstaller 환경을 개발모드로 인식 | `--global.developmentMode false` |
| 페이지 빈 화면 | `components.v1` iframe 서빙 실패 | `st.markdown()` 네이티브 방식으로 변경 |
| 에러 시 창 즉시 닫힘 | 콘솔 출력 없이 종료 | `input()` 대기 + traceback 출력 |

---

## 4. 배포 시 주의사항

### Windows 보안 차단
- 미서명 exe → Windows Defender/SmartScreen 차단 가능
- 해결: ZIP 파일 우클릭 → 속성 → "차단 해제" 체크 → 압축 해제

### 중국 법인 배포
- GitHub, Google 접근 불가 환경
- 해결: exe 파일을 이메일/USB로 직접 전달
- 브라우저(Chrome/Edge)는 사용 가능 (Google 서비스만 차단)
- localhost 기반이므로 인터넷 불필요

### 포트 충돌
- 기본 포트: 8501
- 이미 사용 중이면 Streamlit이 자동으로 다른 포트 사용
