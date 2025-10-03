# 📦 Migration Pack (인수인계 문서)
<!-- @LOCKED:DRIVE_LINK START -->
> 🔗 **Google Drive (Endeavour Core Docs)**
> https://drive.google.com/drive/folders/1PoOdQS3BzKvY0zfHfmo1bABzRbuFHf0f?usp=sharing  
> ※ 잠금 영역입니다. 자동화/수정 스크립트는 이 블록을 변경/삭제하면 안 됩니다.
<!-- @LOCKED:DRIVE_LINK END -->

## 🔒 편집 원칙 (Reference)
- 본 불변 규칙은 IPD.md [운영 원칙 섹션]을 따른다.

---

## 업무 인수인계 사항

### 거시적 과업
1) Iteration 2 진입 준비  
   - R: 백테스트 엔진 담당  
   - D: YYYY-MM-DD  
   - DoD: parallel_runner.py로 KOSPI30+KOSDAQ10 병렬 실행 (평균 런타임 ≤ N분, 실패율 ≤ X%)  
   - Checks: 샘플 리포트 3건, CHANGE_LOG 반영  

2) 데이터 품질 개선  
   - R: 데이터 핸들러 담당  
   - DoD: 캐시 무결성 검사 함수, 결측치 경고 로그 규격화, 로그 파일 회전 정책 적용  

3) CI/CD 도입 (선택)  
   - R: DevOps 담당  
   - DoD: Lint + Unit Test 워크플로우, 배지 표시, 실패 시 차단  

### 세부 과업
- 현재 위치: Phase1 완료, Phase2 착수 전  
- 다음 단계 (핵심): parse_strategy 모듈  
  - JSON → 실행 규칙 트랜스파일  
  - 인터페이스 계약:  
    - 입력 스키마 키 목록  
    - 산출 규칙 리스트  
    - 예외 처리 규격  
- 검증:  
  - 3개 샘플 전략(JSON) → 동일 데이터로 결과 재현성 확인 (±0 거래 오차)  
  - 리포트 비교표 생성

<!-- @LOCKED:SESSION_START START -->
### 세션 시작 절차 (2025-10-03 개정)

- 세션 시작 시 반드시 업로드해야 할 파일:
  1. `docs/repo_tree_latest.txt`
  2. `docs/Migration_pack.md`

- AI는 첫 대화 직후 두 파일이 모두 있는지 확인한다.
  - 두 파일이 모두 있으면 리마인드 생략.
  - 하나라도 누락되면 즉시 업로드 요청.

- 목적: 세션 시작 시점에 최신 repo 구조와 맥락을 확보하여 작업 연속성을 보장.
<!-- @LOCKED:SESSION_START END -->

