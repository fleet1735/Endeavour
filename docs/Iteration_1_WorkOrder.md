Deep Research 의뢰용 작업지시서 – Iteration 1
1. 프로젝트 개요

프로젝트 명: Endeavour

목표: 유연한 멀티-전략 백테스팅 엔진 개발

개발 원칙: Iterative(반복) + Incremental(점진) 결합 → 기능 단위로 나누고 짧은 주기로 완성도 상승

현재 단계: Phase-1 (클린 구조, 데이터 핸들러 구축)

지금 할 일: Iteration 1 – 데이터 핸들러 개발 및 캐시 생성

2. 개발 환경

폴더 구조 (Phase-1 기준)

Endeavour/
  src/           # 엔진 코드
  strategies/    # 전략 JSON
  data/          # 캐시 데이터
  reports/       # 리포트 산출물
  universe.csv   # 테스트 유니버스
  02_docs/       # IPD, README, CHANGE_LOG, WorkOrder
  06_Archives/   # Legacy 코드/자료 보관


실행 원칙: 반드시 프로젝트 루트에서 모듈 실행

python -m src.utils.data_handler


→ sys.path 꼼수 사용 금지

3. 입력 데이터

소스:

기본: yfinance (글로벌/한국 포함, 해외 확장성 고려)

보완: pykrx (한국 주식 품질 안정화용 예외)

유니버스 파일: 02_docs/universe/target_tickers.csv

포맷: UTF-8-SIG, CSV

컬럼: 구분, 순위, 종목명, Ticker

예시:

KOSPI,1,삼성전자,005930.KS
KOSDAQ,1,셀트리온헬스케어,091990.KQ

4. 요구 기능

데이터 로딩

입력: 티커 리스트(target_tickers.csv)

기간: 최근 5년 (오늘 기준 자동 계산)

주기: 일봉(Daily)

소스 선택 파라미터 지원 (source="yfinance" 기본, "pykrx" 옵션)

캐싱

저장소: 04_data/cache/

파일명 규칙: {ticker}_{start}_{end}.csv

포맷: CSV (Parquet 확장 가능)

유효성 체크

캐시 hit/miss 여부 로깅

결측치(NaN) 존재 여부 경고 출력

컬럼 구조 검증: Date, Open, High, Low, Close, Volume

로그 출력 예시

[INFO] Cache hit: 005930.KS (2019-09-26 ~ 2024-09-26)

[INFO] Downloaded: 000660.KS → saved to cache

[WARN] Missing values detected in 035720.KQ

5. 산출물

소스 코드

src/utils/data_handler.py : 데이터 핸들러 모듈

데이터 파일

04_data/cache/*.csv : 종목별 데이터 캐시

로그/리포트

캐시 적중/미스 메시지

다운로드 시작/완료 메시지

결측치 경고

6. Definition of Done (DoD)

 src/utils/data_handler.py 모듈이 정상 동작할 것

 3종목 이상 CSV 캐시 생성 (예: 삼성전자, SK하이닉스, 카카오)

 동일 실행 반복 시 캐시 hit 로그 출력

 결측치 존재 여부 로그에 경고 표시

 실행은 python -m src.utils.data_handler 방식으로 정상 동작할 것

7. Git 커밋 전략

기능 단위 커밋 원칙 준수

예상 메시지:

git add src/utils/data_handler.py 04_data/cache/
git commit -m "feat: implement data_handler for yfinance daily cache (Iteration 1)"

8. 향후 Iteration 계획 (참고)

Iteration 2: JSON 전략 파서 구현 (전략 스키마 해석 → 신호 로그 생성)

Iteration 3: 병렬 실행 러너 연결 (multi-ticker loop)

Iteration 4: 성과 리포트 (성과 지표 7종 + 연도별 테이블)

Iteration 5: 병렬화 적용 (40종목 완주)