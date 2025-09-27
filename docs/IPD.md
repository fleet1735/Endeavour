# 📘 IPD (Initial Project Document) – Endeavour
_최종 갱신: 2025-09-28 (Asia/Seoul)_

## 1. 비전
유연한 멀티-전략 백테스팅 엔진을 **상용 수준 품질**로 구축하여 전략 연구·실험의 허브가 되게 한다.

## 2. 핵심 철학
- **재현성**: 동일 입력 → 동일 결과. 캐시·리포트·로그로 추적 가능.
- **유연성**: 전략을 JSON/코드로 선언, 엔진은 해석·검증·실행.
- **안정성**: 데이터 품질 검증과 폴백 체계, 자동화 우선.

## 3. 표준 폴더 구조
src/endeavour/utils/ # 엔진 유틸(데이터 핸들러 등)
data/cache/ # 재생성 가능 캐시
data/logs/ # 실행 로그
reports/data_quality/ # 검증 리포트(csv)
docs/ # 문서(청사진/IPD/CHANGE_LOG 등)
Archives/ # 레거시/참고자료

## 4. 데이터 전략
- 1차: **yfinance**, 2차 폴백: **pykrx**
- 스키마: `Date, Open, High, Low, Close, Volume`
- 캐시/로그/리포트 경로: `data/cache/`, `data/logs/`, `reports/data_quality/`
- **기준일: T-1 영업일** (주말·공휴일 자동 제외, `holidays.KR` 사용)
- 품질 검증: 결측일/NaN/이상치 체크 → 결과 CSV 리포트 저장

## 5. 실행 규칙
- 실행: `python -m src.utils.data_handler`
- 금지: `sys.path` 조작, 임의의 전역 상태 변조
- 입출력 인코딩: UTF-8

## 6. 브랜치·릴리스 운영
- 기본: `main`(안정), `dev`(통합), `feature/*`(단위)
- 안정판 태깅: 예) `v1.0.0-stable` (데이터 핸들러 기준점 확보 후)
- 커밋 메시지 규칙: `feat|fix|refactor|docs|chore: ...`

## 7. 품질/관측 가능성
- 로그: `data/logs/data_handler.log`
- 리포트: `reports/data_quality/validation_YYYYMMDD.csv`
- 캐시 히트/미스, 소스(yfinance/pykrx) 사용 여부, 검증 결과 레벨(OK/WARN/ERROR) 기록

## 8. 자동화(Here-Document) 원칙
- 스크립트는 **한 방에** 실행·검증·Git 반영까지 포함
- 대용량/복잡 작업은 단계 분리(안전 커밋 단위 유지)
- 인코딩 이슈 예방: PowerShell은 UTF-8, 필요 시 `chcp 65001`

## 9. 보안/비밀정보
- 키/토큰은 레포에 저장 금지. `.gitignore`로 차단, 로컬 `.env` 사용.

## 10. 로드맵
- Phase 1: 데이터 인프라 안정화(완료)
- Phase 2: 백테스트 엔진 고도화
- Phase 3: 전략 라이브러리 확장
- Phase 4: 운영·배포 체계 완성