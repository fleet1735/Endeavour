## 2025-10-03 (추가 기록)
- **fix(Git): desktop.ini 오염 복구**
  - .git/refs, .git/objects 오염으로 fatal 발생 → .git 전멸 및 repo 재초기화
  - IPD.md에 위험 작업 사전 백업 의무, Windows+Cloud Drive desktop.ini 리스크 관리 규정 추가
  - Migration_pack.md에 사건 경위 및 교훈 기록

- **refactor(repo_tree): 관리 방식 개편**
  - repo_tree 루트 누적 → epo_trees/ 폴더 고정 출력
  - PowerShell 프로필에 epo_tree.ps1 자동 실행 재등록 (repo_trees 전용 저장)

- **docs(운영 규정): 불변 원칙 강화**
  - Heredoc 제공 원칙: 승인 후 즉시 실행, 분할/질문/물타기 금지
  - 주제 집중, 선택지 남발 금지 → AI Operating Contract, Response Template, Endeavour Operating Protocol에 반영
