# Migration Pack

## Phase 2.3 — CI Finalization

- CF-ONT-101: `validator/dsl_checker.py` 신규 CLI 인자(`--events`, `--setup`, `--out`, `--strict`) 추가. 기존 단일 위치 인자 호출과 **완전 호환**.
- CF-ONT-201: `validator/registry_cohesion_checker.py` 안정화(IndentationError 종결), registry ↔ schemas 결속 검증 고정.
- `.github/workflows/ontology_ci.yml`: **push(main)** 시 101/201 **무조건 실행**, `runs/ci/validator_report.json` 아티팩트 업로드.
