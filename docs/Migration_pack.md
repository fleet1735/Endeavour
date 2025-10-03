⚠️ 문서 관리 규율 안내 (Discipline Notice)
- 본 문서는 Endeavour 프로젝트 문서 관리 규율에 따라 유지됩니다.
- 세션이 바뀌더라도, IPD/CHANGE_LOG/Protocol/청사진/Contract/Template 간 일관성을 반드시 준수해야 합니다.
- 중복 내용은 제거하고, 역할별 구분(헌법·청사진·운영·이력·핸드오프)을 지키십시오.
- 필요 시 Migration_pack.md에 사건/변경 사항 기록 후, ChangeLog에 반영하십시오.

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

## 📌 Git desktop.ini 사태 (2025-10-03) 복구 기록

### 사건 개요
- Windows Explorer + GoogleDrive 동기화로 인해 .git/objects/*, .git/refs/* 내부에 desktop.ini 파일이 다수 생성됨.
- Git은 이를 잘못된 객체/참조로 인식하여 atal: bad object refs/desktop.ini 오류가 지속 발생.
- .git/objects 디렉토리 전체가 오염 → git fsck에서 수백 개 invalid sha1 pointer 검출.
- 최종적으로 Git repo 자체가 무력화됨.

### 대응 경위
1. 초기: desktop.ini 개별 삭제 및 refs 정리 → 실패.
2. 확산: .git/objects 전멸 스크립트 실행 → Git repo 완전 손상.
3. 복구: 
   - 전체 워킹 디렉토리 백업 확보.
   - .git 디렉토리 삭제 후 새로 git init.
   - IPD.md에 위험 작업 사전 백업 의무, Windows+Cloud Drive 리스크 관리 규칙 추가.
   - 모든 파일 새 baseline 커밋 생성, GitHub 원격(origin/main)에 강제 푸시.

### 교훈
- 위험 작업(삭제/정리/전멸) 전에 반드시 **백업 확보**가 선행되어야 함.
- .git은 클라우드 동기화 대상에서 제외하고, 탐색기 접근을 막아야 함.
- 정기적으로 git fsck --full을 통해 조기 탐지 필요.

### 결론
- 2025-10-03 기준, 리포지토리는 깨끗하게 복구됨.
- Git 관리 원칙이 IPD/Migration_pack에 반영되었으므로, 동일 사태는 재발하지 않을 것임.

### 🟢 세션 정비 기록 (2025-10-03 ~ 2025-10-04)
- 문서 체계: Iteration_1_WorkOrder.md → Archives/Legacy_Docs, 중복 문서 삭제, Discipline Notice 삽입
- repo_tree: docs/repo_tree_latest.txt 단일 유지, 타임스탬프 생성 제거, 루트/누적본 제거
- 캐시: *_None_None.csv 제거, {ticker}_{start}_{end}.csv 규칙 통일
- 보안: Archives/API_Key/* Git 추적 제외, .gitignore 등록, D:\SecureKeys로 이동
- 로그 관리: data/logs 회전({name}_YYYY-MM-DD.log), 30일 보존/180일 삭제, Git 제외

### 📦 세션 인수인계 지침 보강 (2025-10-04)
- cache: Git 제외, 필요시 data_handler로 재생성
- reports: Git 보존 (분석/검증 결과물)
- logs: Git 제외, 30일 보존 후 archive, 180일 삭제
- archives: 완료 문서 및 불필요 파일은 Archives 하위로 이동
- 보안: API Key는 D:\SecureKeys 또는 환경변수에서 불러오기, 절대 Git 포함 금지
