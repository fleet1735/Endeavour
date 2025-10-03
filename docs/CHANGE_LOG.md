## 2025-10-03 (repo_tree 관리 원칙 확정)
- repo_tree는 최신본 하나만 유지하는 방식으로 확정
- docs/repo_tree_latest.txt 경로에서만 관리
- 루트 및 repo_trees/에 생성된 누적본은 정리 대상
## 2025-10-03 (폴더 구조 정리)
- src/utils 폴더 제거 (중복 구조 정리)
- src/endeavour/utils/*.bak → Archives/Legacy_Code/ 이동
- IPD.md 실행 규칙 src.utils → src.endeavour.utils 로 갱신
## 2025-10-03 (인프라 정비)
- 문서 체계 및 인프라 정비 개시
- IPD.md 최신화 (갱신일 반영, 보안/캐시 관리 원칙 추가)
- src/utils 중복 구조 정리 계획 수립
- Archives/API_Key 보안 이슈 확인 및 정리 예정
- 캐시 파일명 규칙(None_None) 위반 문제 검출, 재생성 루틴 점검 예정
## 2025-10-03
- PowerShell 프로필에 `repo_tree_latest.txt` 자동 생성/갱신 루틴 추가.
- IPD.md: 세션 시작 리마인드 규정 조건부로 개정.
- 프로젝트청사진.md: Unified System Blueprint (2025-10-03 집대성) 삽입.
- Endeavour_Operating_Protocol.md 신규 작성 (AI 온보딩 매뉴얼).
# 📑 CHANGE_LOG

## 2025-10-01
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입

## 2025-09-30
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입
- IPD.md 운영 원칙 개편 (repoRoot 기반 절대경로, Here-Doc 작성 규칙 강화, CHANGE_LOG Append 원칙)
- Migration_pack.md 인수인계 전용 문서로 단순화
- README.md 최신 문서 체계/운영 원칙 반영
- CHANGE_LOG.md Append 관리 원칙 확정
- 소통*.txt 규칙, Archives/ 관리 원칙 반영

## 2025-09-29
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입
- Migration_pack.md 업데이트 → 인수인계 전용, 운영 원칙은 IPD 참조로 일원화
- IPD.md 보강 → Vision & Target Deliverable 최신화, Workdir Guard·Here-Doc 규칙 추가
- 문서 관리 체계 정리 → docs/ 밑 통합, 소통*.txt Git 무시, 일회성 스크립트 Archives/ 이동
- 파일 정리 → 새파일.txt·실행.txt 삭제, fix_data_handler.py → Archives/ 이동
- 소통.txt 신설 (컨텍스트 메모용, Git 무시)

## 2025-09-28
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입
- **fix(Migration_pack): 인코딩 문제 해결**
  - 문제: Migration_pack.md가 PowerShell 5.1 환경에서 UTF-16/ANSI로 저장되어 GitHub/VSC/Obsidian에서 글자가 깨짐
  - 원인: 로컬 터미널 기본 인코딩 문제
  - 조치: PowerShell 7.5.3 업그레이드,  UTF-8 No BOM 강제 설정, Git i18n 인코딩 설정 UTF-8로 조정
  - 결과: GitHub 및 에디터 환경에서 글자 깨짐 문제 해결

## 2025-09-27
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입
- **refactor: Workdir 구조 리팩터링**
  - 실행 구조 정리: 모든 스크립트는 Git 루트에서 실행되도록 강제
  - Migration_pack.md 최신판에서 Workdir 규칙 반영
  - 문서 일원화: Migration_pack.md, IPD.md, CHANGE_LOG.md, 프로젝트청사진.md 동시 업데이트
  - 자동화 원칙: 실행 스크립트 + 커밋/푸시 = 원샷 자동화 적용
  - Git 우선, Drive 후순위. Push는 수동. PowerShell 7.5.3 적용
  - pre-commit 훅: Markdown UTF-8(No BOM)+LF 강제, 25MB 초과 차단, 로그 기록

## 2025-09-26
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입
- DataHandler 복구, Git 상태 점검
- 캐시 무결성 검사 및 로그 점검
- Phase1 마무리, Phase2 준비 단계 진입

## 2025-09-23
- AI Operating Contract(v1.0) 추가: docs/AI_Operating_Contract.md
- 응답 템플릿 추가: docs/AI_Response_Template.md
- IPD 운영 원칙 보강: 실행 우선 규칙/세션 시작 보고 항목/참고 문서 링크 삽입
- 프로젝트 초기화 (IPD.md, CHANGE_LOG.md, README.md 작성)
- GitHub 최초 push
- 3단 문서 체계(IPD + Change Log + Design Notes) 초안 확립