## [Phase 2] Patch — Ontology-First hardening (json import fix, UTC fix, audit hash func) — 2025-10-11 04:09:54 +09:00
- tools/registry_cohesion_checker.py: UnboundLocalError(json) 수정 — 모듈 import 순서 정리
- validator/engines: datetime.utcnow → datetime.now(timezone.utc)
- PowerShell audit hash 함수명 충돌 회피(H → GetSHA256)
- CHANGE_LOG append 구문 안전 패턴 반영