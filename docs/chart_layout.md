# 차트 레이아웃 설계

## 1. 레이아웃 — 미니탭 Process Capability Report 와 동일

미니탭 기본 출력(551×368 px)의 배치를 그대로 따르고, 해상도만 2배(1102×736 px)로 출력한다.
보고서에 붙여넣고 축소하면 미니탭 그래프와 같은 모습이 된다.

```
┌───────────────────────────────────────────────────────────┐
│                    제목 (굵게, y=18px)                      │
│  LSL        Target        USL   (플롯 위 라벨, y=55px)       │
│ ┌──────────┐ ┌────────────────┐ ┌───────┐ Within/Overall   │
│ │Process   │ │                │ │ 범례   │ (414~490, 63~96) │
│ │Data      │ │  히스토그램 +    │ └───────┘                  │
│ │(12~134,  │ │  Within/Overall │ ┌─────────────────────┐    │
│ │ 63~168)  │ │  (148~405,      │ │Potential (Within)   │    │
│ └──────────┘ │   63~280)       │ │(414~540, 100~161)   │    │
│              │                 │ ├─────────────────────┤    │
│              └────────────────┘ │Overall Capability   │    │
│               x축 눈금 (y=292)   │(414~540, 164~240)   │    │
│                                  └─────────────────────┘    │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│ │Observed  │ │Exp.Within│ │Exp.Overall│  (y 305~360, 폭 108) │
│ └──────────┘ └──────────┘ └──────────┘                       │
└───────────────────────────────────────────────────────────┘
```

모든 좌표는 **기준 이미지(551×368) 픽셀**로 코드에 적고 `_fx()/_fy()` 로 figure 좌표(0~1)로 변환한다.

### Figure 크기 / 저장
```python
FIG_W_IN, FIG_H_IN, FIG_DPI = 5.51, 3.68, 200   # → 1102 × 736 px
fig.savefig(buf, format="png", dpi=FIG_DPI)       # bbox_inches="tight" 사용 안 함 → 크기 고정
```

### 배경색 / 글꼴
```python
fig.patch.set_facecolor("#F1ECE2")   # 미니탭 베이지 (기준 이미지에서 샘플링)
font: Arial (없으면 Liberation Sans → DejaVu Sans), 본문 6.2pt, 제목 9.5pt
```

### Target
엑셀 CPK 시트에 `Target` 행이 있으면 그 값을 쓰고, 없으면 `(USL + LSL) / 2`.
Cpm 계산과 Target 선 모두 이 값을 사용한다.

---

## 3. 구성 요소 상세

### 3.1 히스토그램
```python
ax.hist(data, bins=n_bins, density=True,
        color="#787878",           # 회색 (미니탭 스타일)
        edgecolor="black",        # 검정 테두리
        linewidth=0.8,
        alpha=1.0, zorder=3)
```
- `bins`: sqrt(n) 기반, 최소 10
- `density=True`: 정규분포 곡선과 스케일 맞춤

### 3.2 정규분포 곡선
```python
# Within (빨간 실선)
ax.plot(x_curve, norm.pdf(x_curve, mean, sw), "r-", linewidth=1.8)

# Overall (검정 점선)
ax.plot(x_curve, norm.pdf(x_curve, mean, so), "k--", linewidth=1.8)
```

### 3.3 규격선
```python
ax.axvline(lsl,    color="red",   linestyle="--")  # LSL
ax.axvline(usl,    color="red",   linestyle="--")  # USL
ax.axvline(target, color="green", linestyle="--")  # Target
```
- 상단에 "LSL", "Target", "USL" 라벨 표시

### 3.4 테이블 (`_table`)
테두리 있는 표를 Figure 좌표계에 직접 그림 (기준 픽셀 좌표로 지정):
- `_box()`: 흰 바탕 + 검정 테두리
- `_txt()`: 제목(가운데), 라벨(왼쪽), 값(왼쪽 또는 오른쪽 정렬)
- 미니탭처럼 제목과 내용 사이 구분선 없음

---

## 4. X축 범위 결정

```python
spec_range = usl - lsl
sigma_max = max(stdev_within, stdev_overall)

x_lo = min(lsl - spec_range * 0.08, mean - 4.5 * sigma_max)
x_hi = max(usl + spec_range * 0.08, mean + 4.5 * sigma_max)
```
- 규격 범위 바깥 8% 여유
- 또는 평균 ± 4.5 시그마 중 더 넓은 범위

---

## 5. 웹 UI 레이아웃

### Streamlit 페이지 구성
```
┌──────────────┬──────────────────────────────────────────┐
│   사이드바     │                                          │
│              │  CPK Analyzer                             │
│ 파일 업로드    │                                          │
│ 시트 선택     │  [전체 항목: 9개] [PASS: 9개] [FAIL: 0개]  │
│ 그래프 배치   │                                          │
│ [분석 시작]   │  요약 테이블                               │
│              │  ─────────────────────────                │
│              │  차트를 클릭하면 클립보드에 복사됩니다.        │
│              │                                          │
│              │  ┌─────────┐  ┌─────────┐                │
│              │  │ 차트 1   │  │ 차트 2   │                │
│              │  └─────────┘  └─────────┘                │
│              │  ┌─────────┐  ┌─────────┐                │
│              │  │ 차트 3   │  │ 차트 4   │                │
│              │  └─────────┘  └─────────┘                │
└──────────────┴──────────────────────────────────────────┘
```

### 그래프 배치 옵션
- **1열**: 큰 그래프, 세로 스크롤
- **2열** (기본): 한 화면에 더 많은 그래프

### 클릭 복사 기능
- 차트 이미지 클릭 → 클립보드에 PNG 복사
- 초록색 테두리로 복사 완료 피드백
- Ctrl+V로 보고서에 바로 붙여넣기
