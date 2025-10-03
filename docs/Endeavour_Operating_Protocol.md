# Endeavour 운영체계 (Operating Protocol)

이 문서는 Endeavour 프로젝트에서 확립한 운영 프로세스를 정리한 매뉴얼이다.  
향후 새로운 프로젝트에서도 이 매뉴얼을 기준으로 세션/개발을 진행할 수 있다.  

---

## 1. 헌법 문서
- **IPD.md**: 철학, 표준 폴더 구조, 운영 원칙, 불변 규칙.  
- **프로젝트청사진.md**: 아키텍처 설계도, Phase별 목표, 최신 설계 변경사항.  
- **AI_Operating_Contract.md**: AI 협업 규칙 (실행 우선, 오류 보고, Here-Doc 원칙).  
- **AI_Response_Template.md**: 응답/보고 형식 표준.  

👉 역할: **규칙과 설계**를 명문화 → 세션이 바뀌어도 변하지 않는 헌법.  

---

## 2. 컨텍스트 유지 장치
- **Migration_pack.md**: 세션 간 “핸드오프 문서”.  
  - 오늘 변경/이슈/다음 세션에 전달할 맥락 기록.  
  - 세션 시작 시 반드시 업로드.  
- **repo_tree_latest.txt**: repo 전체 구조 최신본.  
  - PowerShell 프로필에서 자동 생성.  
  - 세션 시작 시 반드시 업로드.  

👉 역할: **세션 간 끊김 없는 맥락 연결**.  

---

## 3. Git 운용 규칙
- **Git 루트 가드**: `git rev-parse --show-toplevel`로 항상 Endeavour 루트 확인.  
- **Heredoc 자동화 스크립트**:  
  - AI가 파일 생성/수정/삭제 → add/commit/push까지 한번에.  
  - 사용자는 PowerShell에 붙여넣기만.  
- **pre-commit 훅**: Markdown UTF-8 정규화, 25MB 이상 차단, 로그 기록.  

👉 역할: **수작업 없는 코드 반영**.  

---

## 4. 세션 시작 절차 (Bootstrap Protocol)
1. 사용자가 PowerShell 실행 → `repo_tree_latest.txt` 자동 생성 (`docs/` 폴더).  
2. 첫 대화 시 `repo_tree_latest.txt` + `Migration_pack.md` 업로드.  
3. AI는 두 파일 확인:  
   - 둘 다 있으면 리마인드 생략.  
   - 하나라도 없으면 즉시 업로드 요청.  

👉 역할: **AI가 항상 최신 코드와 맥락을 알고 시작**.  

---

## 5. 개발 단계 진행
- **Phase 1**: 데이터 파이프라인 (캐시/결측치/소스 교차검증).  
- **Phase 2**: JSON 전략 파서 설계.  
- **Phase 3**: 병렬 백테스트 엔진 (VectorBT → Backtrader).  
- **Phase 4**: 분석/보고 모듈 (QuantStats/Plotly).  
- **Phase 5**: 리스크 관리/Sizer 도입.  

👉 역할: **큰 그림(청사진)과 단계별 진척을 연결**.  

---

## 6. 협업/확장
- **사람-AI 교체 대응**: Migration_pack.md + repo_tree_latest.txt → 새 AI/협업자도 바로 이어받기 가능.  
- **문서 연동 원칙**: IPD, Migration_pack, CHANGE_LOG, 프로젝트청사진은 동시 업데이트.  
- **Archives/**: 일회성 코드/스크립트 보관, 과거 실험 기록 유지.  

👉 역할: **조직적 협업 / 장기 유지보수 대비**.  

---

## 7. 활용 방법
- 새로운 프로젝트를 시작할 때 이 문서를 AI에게 보여주면,  
  AI는 이 매뉴얼을 기준으로 전무님께 안내를 하고, 세션 관리/개발 프로세스를 자동으로 지원한다.
