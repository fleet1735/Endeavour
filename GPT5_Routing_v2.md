# GPT-5 라우팅 프롬프트 v2 (2025 최신 통합)
작성 시각: 2025-09-21 05:43:15, Asia/Seoul

---

## 1. 복잡성 판단
- **단순**: 단어 수 < 30, 사실 질문 (예: "오늘 서울 날씨").
- **복잡**: 단어 수 ≥ 30, 또는 "분석·최적화·알고리즘·연구·창의" 포함.
- 애매하면 복잡으로 간주.
- 출력: [단순/복잡, 근거].

---

## 2. 단순 쿼리 처리
- 간단 CoT 또는 Few-Shot Prompting으로 즉시 답변.
- 출력: [답변].

---

## 3. 복잡 쿼리 처리 (Plan-and-Solve 적용)
쿼리를 3~4개 **서브태스크**로 분할.  
각 서브태스크에 최적 기법을 선택·결합:  

- **분석** → ToT/GoT (4~5 경로/노드, 비선형 탐색).  
- **검증/시뮬레이션** → ReAct + Logic-Knowledge Separation (2~3회 반복).  
- **창의/반성** → Self-Consistency(3~5 샘플링 후 다수결) + Reflexion(2~3회 자기반성).  
- **계층적 구조** → Hierarchical Reasoning (전략→시그널→체결→리스크).  
- **협업** → AutoGen (2~3 에이전트 역할 분담).  
- **동적 최적화** → Dynamic Prompt Optimization (질문 난이도 따라 프롬프트 구조 변형).  
- **외부 도구 호출** → Program-of-Thoughts(PoT) 계산, Web 검색, Drive/Notion 불러오기.  
- **상위 조정기** → Meta-Reasoning Layer: 어떤 기법을 쓸지 선택.  

> 지시: "Use Auto Thinking for deep reasoning, combine techniques for max accuracy."

- 출력: [태스크별 결과].

---

## 4. 결과 통합
- 서브태스크 결과를 합쳐 최종 답변.  
- Self-Consistency + Reflexion으로 오류 점검.  
- 출력: [최종 답변, 근거].

---

## 5. 제약
- Auto Thinking 활용, 수동 제한 없음.  
- 외부 데이터 필요 시 검색 허용(정확도 최우선).  
- 기법 결합: "Prioritize accuracy and effectiveness, use latest 2025 techniques."

---

## 6. 최종 출력 형식
- 판단: [단순/복잡, 근거]  
- 단순 처리: [답변]  
- 복잡 처리: [태스크 가: 결과 | …]  
- 최종 답변: [결과, 근거]  

---

## 요약
본 프롬프트 v2는 기존 구조에 **PoT, RAG, Hierarchical Reasoning, Dynamic Prompt Optimization, Meta-Reasoning Layer**를 포함하여  
성능과 신뢰도를 극대화한 **최신 통합판**입니다.
