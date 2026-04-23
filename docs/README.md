# CPK Analyzer - 프로젝트 제작 문서

## 1. 프로젝트 개요

### 목적
미니탭(Minitab)으로 수동 생성하던 공정능력(CPK) 분석 그래프를 **자동화**하는 프로그램.
엑셀 파일을 업로드하면 모든 테스트 항목의 공정능력 차트를 한 번에 생성한다.

### 해결하는 문제
- 기존: 미니탭에 데이터를 수동 입력 → 테스트 항목별로 하나씩 그래프 생성 (수십 개)
- 이후: 엑셀 업로드 한 번 → 전체 그래프 자동 생성 → 클릭 복사 → 보고서에 붙여넣기

### 기술 스택
| 구분 | 기술 | 역할 |
|------|------|------|
| 프레임워크 | Streamlit | 웹 UI |
| 데이터 처리 | pandas, openpyxl | 엑셀 파싱 |
| 수학/통계 | numpy, scipy | 공정능력 지수 계산 |
| 차트 | matplotlib | 미니탭 스타일 그래프 |
| 배포 | PyInstaller + GitHub Actions | Windows exe 빌드 |

---

## 2. 프로젝트 구조

```
cpk-analyzer/
├── app.py                          # 메인 애플리케이션
├── launcher.py                     # PyInstaller exe 진입점
├── requirements.txt                # Python 의존성
├── .gitignore
├── .github/
│   └── workflows/
│       └── build-exe.yml           # Windows exe 자동 빌드
└── docs/
    ├── README.md                   # 이 문서
    ├── calculation.md              # 공정능력 계산 상세
    ├── excel_format.md             # 엑셀 데이터 형식
    ├── chart_layout.md             # 차트 레이아웃 설계
    └── deployment.md               # 배포 가이드
```

---

## 3. 실행 방법

### 개발 환경 (Mac/Windows/Linux)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Windows exe
1. GitHub Actions에서 빌드된 `CPK_Analyzer_Windows.zip` 다운로드
2. 압축 해제
3. `CPK_Analyzer.exe` 더블클릭
4. 브라우저가 자동으로 열림

---

## 4. 코드 구조 (app.py)

### 4.1 모듈 구성
```
app.py
├── 1. 데이터 파싱
│   ├── get_sheet_names()      # 엑셀 시트 목록
│   └── parse_sheet()          # 시트 → 테스트 항목 추출
├── 2. 공정능력 계산
│   └── calculate_capability() # 모든 지수 계산
├── 3. 차트 생성
│   ├── _draw_table()          # 테두리 표 그리기
│   ├── create_capability_chart() # 미니탭 스타일 차트
│   └── fig_to_png()           # Figure → PNG 변환
├── 4. 클릭 복사
│   ├── COPY_JS                # 클립보드 복사 JavaScript
│   └── render_copyable_image() # 클릭 가능한 이미지 렌더링
└── 5. Streamlit 앱
    └── main()                 # UI 구성
```

### 4.2 데이터 흐름
```
엑셀 파일 업로드
    ↓
get_sheet_names() → 시트 선택
    ↓
parse_sheet() → 테스트 항목 리스트 [{name, usl, lsl, data}, ...]
    ↓
calculate_capability() → 공정능력 지수 dict
    ↓
create_capability_chart() → matplotlib Figure
    ↓
fig_to_png() → PNG bytes
    ↓
render_copyable_image() → 화면 표시 (클릭 → 클립보드 복사)
```

---

## 5. 핵심 알고리즘

### 상세 계산 방법 → [calculation.md](calculation.md)
### 엑셀 형식 규격 → [excel_format.md](excel_format.md)
### 차트 레이아웃 설계 → [chart_layout.md](chart_layout.md)
### 배포 가이드 → [deployment.md](deployment.md)
