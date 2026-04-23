# 공정능력 계산 상세

## 1. 기본 통계량

### Sample Mean (표본 평균)
```
mean = (1/n) * Σ x_i
```

### Sample N
데이터 포인트 개수 (예: 200개)

### Subgroup Size
**1** (개별 관측값). 생산 순서대로 하나씩 측정한 데이터.

### Target (목표값)
```
Target = (USL + LSL) / 2
```
USL과 LSL의 중간값으로 자동 계산.

---

## 2. 표준편차 추정

### Overall StDev (전체 표준편차)
표본 표준편차 (ddof=1):
```python
stdev_overall = np.std(data, ddof=1)
# = sqrt( Σ(x_i - mean)² / (n-1) )
```

### Within StDev (군내 표준편차) — 핵심

**s/c4 방법** 사용. 이것이 미니탭과 정확히 일치하는 유일한 방법.

```python
from scipy.special import gamma

c4 = sqrt(2/(n-1)) * gamma(n/2) / gamma((n-1)/2)
stdev_within = stdev_overall / c4
```

#### c4 보정계수란?
- 표본 표준편차 s는 모표준편차 σ의 **편향 추정량**
- c4는 이 편향을 보정하는 계수
- n이 클수록 c4 → 1에 가까워짐

#### 다른 방법과의 비교 (n=200, 실제 데이터)
| 방법 | Within StDev | 미니탭 일치 여부 |
|------|-------------|----------------|
| **s/c4** | **0.004990** | **정확히 일치** |
| MR_bar/d2 | 0.005170 | 불일치 |
| RMSSD | 0.005170 | 불일치 |
| Median MR/d4 | 0.004866 | 불일치 |

**결론: 반드시 s/c4 방법을 사용해야 미니탭과 동일한 결과를 얻는다.**

---

## 3. 공정능력 지수

### Potential (Within) Capability — 잠재 능력

단기 변동(Within StDev)을 기반으로 한 지수:

```
Cp  = (USL - LSL) / (6 * StDev_Within)        # 잠재 공정능력
CPL = (Mean - LSL) / (3 * StDev_Within)        # 하한 방향
CPU = (USL - Mean) / (3 * StDev_Within)        # 상한 방향
Cpk = min(CPL, CPU)                            # 실제 공정능력
```

### Overall Capability — 전체 능력

장기 변동(Overall StDev)을 기반으로 한 지수:

```
Pp  = (USL - LSL) / (6 * StDev_Overall)
PPL = (Mean - LSL) / (3 * StDev_Overall)
PPU = (USL - Mean) / (3 * StDev_Overall)
Ppk = min(PPL, PPU)
```

### Cpm — 목표값 대비 능력

```
tau = sqrt(StDev_Overall² + (Mean - Target)²)
Cpm = (USL - LSL) / (6 * tau)
```

### 판정 기준
- **Cpk >= 1.33**: PASS
- **Cpk < 1.33**: FAIL

---

## 4. PPM (Parts Per Million) 성능

### Observed Performance (관측 성능)
실제 규격 벗어난 비율:
```
PPM < LSL = (LSL 미만 개수 / N) * 1,000,000
PPM > USL = (USL 초과 개수 / N) * 1,000,000
PPM Total = PPM < LSL + PPM > USL
```

### Expected Within Performance (예측 단기 성능)
정규분포 가정, Within StDev 기준:
```python
PPM < LSL = norm.cdf((LSL - Mean) / StDev_Within) * 1e6
PPM > USL = (1 - norm.cdf((USL - Mean) / StDev_Within)) * 1e6
```

### Expected Overall Performance (예측 장기 성능)
정규분포 가정, Overall StDev 기준:
```python
PPM < LSL = norm.cdf((LSL - Mean) / StDev_Overall) * 1e6
PPM > USL = (1 - norm.cdf((USL - Mean) / StDev_Overall)) * 1e6
```

---

## 5. 정규분포 곡선

히스토그램 위에 두 개의 정규분포 곡선을 그린다:

- **Within (빨간 실선)**: N(Mean, StDev_Within) — 단기 변동
- **Overall (검정 점선)**: N(Mean, StDev_Overall) — 장기 변동

```python
from scipy.stats import norm
y_within  = norm.pdf(x, mean, stdev_within)
y_overall = norm.pdf(x, mean, stdev_overall)
```

---

## 6. 계산 검증 결과

실제 엑셀 데이터(Standby Power Test, n=200)로 미니탭 결과와 비교:

| 항목 | 미니탭 | 우리 프로그램 | 차이 |
|------|--------|-------------|------|
| Sample Mean | 0.049005 | 0.049005 | 0 |
| StDev(Within) | 0.004990 | 0.004990 | < 1e-9 |
| StDev(Overall) | 0.004984 | 0.004984 | 0 |
| Cp | 4.49 | 4.49 | 0 |
| Cpk | 3.44 | 3.44 | 0 |
| Pp | 4.49 | 4.49 | 0 |
| Ppk | 3.45 | 3.45 | 0 |
