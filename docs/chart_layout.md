# 차트 레이아웃 설계

## 1. 레이아웃 선택

두 가지 안을 비교한 후 **Option B**를 채택:

| 구분 | Option A | Option B (채택) |
|------|----------|----------------|
| Process Data | 우측 상단 | **좌측 별도 패널** |
| 히스토그램 | 좌측 | **중앙** |
| Capability 테이블 | 우측 | **우측** |
| PPM 테이블 | 하단 3열 | **하단 3열** |

**채택 이유**: 미니탭의 Process Data가 크게 보이는 스타일과 가장 유사.

---

## 2. Figure 좌표계

matplotlib Figure 좌표 (0~1 범위):

```
┌─────────────────────────────────────────────────────────────┐
│                        제목 (y=0.965)                        │
├──────────┬─────────────────────────┬────────────────────────┤
│          │                         │ Potential (Within)     │
│ Process  │                         │ Capability             │
│ Data     │     히스토그램 + 곡선     │ (x=0.68, y=0.84)      │
│          │                         │                        │
│ (x=0.02) │   (x=0.215~0.635)      │ Overall Capability     │
│ (y=0.87) │   (y=0.20~0.87)        │ (x=0.68, y=0.645)     │
│          │                         │                        │
├──────────┴───────────┬─────────────┴────────────────────────┤
│  Observed Perf.      │ Exp. Within Perf. │ Exp. Overall Perf.│
│  (x=0.04, y=0.15)   │ (x=0.35, y=0.15) │ (x=0.66, y=0.15) │
└──────────────────────┴───────────────────┴───────────────────┘
```

### Figure 크기
```python
fig = plt.figure(figsize=(14, 7.5))
```

### 배경색
```python
fig.patch.set_facecolor("#F0ECD8")  # 미니탭과 동일한 베이지색
```

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

### 3.4 테이블 (`_draw_table`)
테두리 있는 표를 Figure 좌표계에 직접 그림:
- `Rectangle`: 테두리 박스
- `fig.text()`: 제목, 라벨, 값
- `Line2D`: 제목과 내용 구분선

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
