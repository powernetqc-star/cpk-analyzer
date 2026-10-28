# 엑셀 데이터 형식

## 1. 지원 형식
- `.xlsx`, `.xls`
- 시트 선택 가능 (예: "11. 출력 특성 Cpk")

---

## 2. 시트 구조

프로그램이 자동 감지하는 구조:

```
     | A(header_col) | B              | C              | ... | K(result_col)
-----+---------------+----------------+----------------+-----+-------------
  1  | 측정항목       | Line Reg 1     | Line Reg 2     | ... | Result
  2  | Spec max      | 14.66          | 14.66          | ... |
  3  | Spec min      | 13.34          | 13.34          | ... |
  4  | (기타 정보)    |                |                |     |
  ...| ...           |                |                |     |
 12  | 시리얼번호1    | 13.846         | 13.924         | ... | PASS
 13  | 시리얼번호2    | 13.851         | 13.920         | ... | PASS
 ...
211  | 시리얼번호200  | 13.842         | 13.918         | ... | PASS
```

---

## 3. 자동 감지 로직

### 3.1 측정항목 행 (header_row)
- 처음 15행 × 5열 범위에서 "측정항목" 텍스트를 검색
- 이 행이 테스트 항목명의 헤더

### 3.2 Spec max / min 행
- header_row 아래 12행 이내에서 검색
- "spec max", "max", "spec min", "min" (대소문자 무시)

### 3.3 Result 열 (result_col)
- header_row에서 "result" 텍스트가 있는 열
- 이 열 이전까지가 테스트 항목 범위

### 3.4 데이터 시작 행 (data_start_row)
- header_row 아래에서 시리얼번호 패턴 검색
- 조건: 길이 > 10, 숫자와 영문자 모두 포함
- 예: "A10024MVT001"

### 3.5 테스트 항목 추출
- header_col+1 부터 result_col-1 까지의 각 열이 하나의 테스트 항목
- 각 항목에서 추출: 이름, USL, LSL, 데이터 배열
- 건너뛰는 조건:
  - 이름이 비어있거나 "nan"
  - USL/LSL을 float로 변환 불가
  - 유효 데이터가 2개 미만

---

## 4. 시리얼번호 형식 예시

다음과 같은 형태의 시리얼번호를 자동 인식:
```
A10024MVT001
A10024MVT002
B20035APNTest003
```

**조건**: 10자 이상 + 숫자 포함 + 영문자 포함

---

## 5. 데이터 값 처리
- 각 셀을 `float()`로 변환 시도
- 변환 실패하는 셀은 무시 (빈 셀, 텍스트 등)
- `pd.notna()` 체크로 NaN 제외

---

## 6. 건너뛴 항목 표시
Spec 변환 실패 또는 데이터 부족으로 건너뛴 항목은 UI에 표시:
```
건너뛴 항목 (2개)
  ⚠ Discharge Test (Spec 변환 실패: max=N/A, min=N/A)
  ⚠ OVP Test (데이터 부족: 1개)
```

---

## 7. 읽기 엔진 — calamine

시트 값을 읽을 때는 `pandas.read_excel(engine="calamine")` 을 사용한다.

- openpyxl은 값만 필요해도 서식(`styles.xml`)과 외부 링크를 전부 파싱한다.
  MVT 체크리스트처럼 셀 스타일이 수만 개 누적된 파일은 시트 하나 읽는 데 약 10초가 걸린다.
- calamine(Rust)은 같은 시트를 약 0.1초에 읽고, 값은 openpyxl과 동일함을 확인했다.
- `.xls` 도 calamine이 그대로 읽는다.
- python-calamine 이 없으면 openpyxl 로 자동 폴백한다.
- 엑셀에 차트를 **쓰는** 기능(`insert_charts_to_excel`)은 계속 openpyxl을 사용한다.

## 8. openpyxl 호환성

일부 엑셀 파일에서 `CustomPropertyList.from_tree`가 TypeError를 발생시킴.
monkey-patch로 해결:

```python
try:
    from openpyxl.packaging.custom import CustomPropertyList
    _orig_from_tree = CustomPropertyList.from_tree.__func__

    @classmethod
    def _safe_from_tree(cls, tree):
        try:
            return _orig_from_tree(cls, tree)
        except TypeError:
            return cls()

    CustomPropertyList.from_tree = _safe_from_tree
except Exception:
    pass
```
