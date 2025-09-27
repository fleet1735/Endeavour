# Change Log

## 2025-09-23
- **IPD.md 최초 업데이트**: Endeavour 프로젝트의 마스터플랜 반영.
- **README.md 업데이트**: 프로젝트 개요, 구조, 문서 연결 최신화.
- **전략 추출 절차 추가**: GPTs 프롬프트 및 JSON 스키마 초안 정의, IPD에 반영.

## 2025-09-26 (1)
- **Phase-1 단순화 구조 확정**: src, strategies, data, reports, universe.csv 5개 축 유지.
- **Git 운영 원칙 보강**: "한 변경축 = 한 커밋" 소규모 단위 실험 방식 도입.
- **초기 목표 설정**: SMA 크로스 단일 전략 × 3종목 스모크 테스트를 DoD(Definition of Done)로 정의.
- **문서 업데이트**: IPD.md / README.md에 단순화 구조 및 운영 원칙 반영.

## 2025-09-26 (2)
- **Iterative + Incremental 개발 지침 반영**: 기능 단위 점진적 개발과 짧은 반복주기 방식으로 개발 계획 수립.
- **IPD.md 업데이트**: Big Picture (Phase)와 Iteration Plan 구분 반영.
- **README.md 업데이트**: 로드맵을 Phase/Iteration 구분 구조로 재정리.

## 2025-09-27
- **refactor**: `data_handler.py` 안정화(최종본, business-grade)
  - yfinance `'tuple'.lower` 예외 및 pykrx `'Date'` 키 오류 해결
  - 스키마 정규화: `Date, Open, High, Low, Close, Volume`
  - 캐시/로그/리포트 경로 통일: `data/cache/`, `data/logs/`, `reports/data_quality/`
  - 폴백 로직: yfinance 실패 시 pykrx로 대체, 캐시 저장/적중 로깅
  - **종료일 로직**: **T-1 영업일**(주말·공휴일 제외, `holidays.KR` 기반) 적용
  - 품질검증 리포트: 결측 영업일/NaN/이상치 점검 → CSV로 저장
- **chore**: 폴더 구조 통일(숫자 접두 제거)
  - `04_data/*` → `data/*`, `03_reports/*` → `reports/*`, `02_docs/*` → `docs/*`, `06_Archives/*` → `Archives/*`
- **chore**: `.gitignore` 최종 규칙 반영(캐시/로그/리포트/IDE/시스템 파일)
- **docs**: `프로젝트청사진.md`, `IPD.md` 최신 구조·실행원칙 반영
- **release (prep)**: 안정판 태깅 **`v1.0.0-stable`** 준비(문서 정리 후 태그 푸시 예정)
