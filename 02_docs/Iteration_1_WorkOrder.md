# Iteration 1 작업지시서 – Endeavour 프로젝트

## 1. 개요
- **프로젝트 명**: Endeavour (유연한 멀티-전략 백테스팅 엔진)
- **현재 단계**: Phase-1 (단순화 구조, Iterative+Incremental 개발 지침 적용)
- **Iteration 1 목표**: 데이터 핸들러 구축 → yfinance에서 KOSPI30 + KOSDAQ10 대상 종목의 5년치 일봉 데이터를 확보하여 캐시 저장

---

## 2. 작업 배경
- 기존 코드(`src/engines`, `utils`, `strategies`)는 모두 `06_Archives/Legacy_Code/`로 이동.
- Phase-1 개발은 **깨끗한 새 구조**(src, strategies, data, reports, universe.csv)에서 시작.
- 이번 Iteration은 데이터 파이프라인을 첫 기능 단위로 완성하는 것에 초점.

---

## 3. 입력 데이터
- **소스**: yfinance (기본), pykrx (한국시장 보완)
- **대상 종목**: `02_docs/universe/target_tickers.csv`
  - 포맷: CSV, UTF-8-SIG
  - 컬럼: `구분, 순위, 종목명, Ticker`
  - 예시:
    ```
    KOSPI,1,삼성전자,005930.KS
    KOSDAQ,1,셀트리온헬스케어,091990.KQ
    ```

---

## 4. 요구 기능
1. **데이터 로딩**
   - 입력: 티커 리스트(`target_tickers.csv`)
   - 기간: 최근 5년 (오늘 기준 자동 계산)
   - 주기: 일봉(Daily)
   - 소스 선택: `source="yfinance"` (기본), `source="pykrx"` (옵션)

2. **캐싱**
   - 로컬 저장소: `04_data/cache/`
   - 포맷: CSV (추후 Parquet 확장 가능)
   - 파일명: `{ticker}_{start}_{end}.csv`

3. **유효성 체크**
   - 캐시 hit/miss 여부 로깅
   - 결측치(NaN) 존재 시 경고 출력
   - 파일 구조 검증 (컬럼: Date, Open, High, Low, Close, Volume)

4. **실행 방식**
   - 반드시 프로젝트 루트에서 모듈 실행:
     ```bash
     python -m src.utils.data_handler
     ```
   - `sys.path` 꼼수 사용 금지

---

## 5. 산출물
1. **폴더/파일**
   - `src/utils/data_handler.py` : 데이터 핸들러 모듈
   - `04_data/cache/*.csv` : 캐시된 종목별 데이터 파일

2. **로그**
   - 캐시 적중/미스 메시지
   - 다운로드 시작/완료 메시지
   - 결측치 존재 여부 경고

3. **테스트 결과**
   - 예시: 삼성전자(005930.KS), SK하이닉스(000660.KS), 카카오(035720.KQ) → 캐시 파일 생성 확인

---

## 6. Definition of Done (DoD)
- [ ] `src/utils/data_handler.py` 모듈이 존재할 것
- [ ] 3종목 이상 캐시 파일이 `04_data/cache/`에 생성될 것
- [ ] 동일 실행 반복 시 캐시 hit 로그 정상 출력
- [ ] 결측치 존재 여부 로그에 표시
- [ ] 실행은 `python -m src.utils.data_handler` 방식으로 정상 동작할 것

---

## 7. Git 커밋 전략
- 기능 단위 커밋 원칙 적용
- 예상 메시지:
  ```bash
  git add src/utils/data_handler.py 04_data/cache/
  git commit -m "feat: implement data_handler for yfinance daily cache (Iteration 1)"
8. 향후 계획 (참고)
Iteration 2: JSON 전략 파서 구현

Iteration 3: 병렬 실행 러너 연결

Iteration 4: 성과 리포트(지표 7종 + 연도별 테이블)

Iteration 5: 병렬화(40종목 완주)