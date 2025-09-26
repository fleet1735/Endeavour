# IPD (Integrated Project Document)

프로젝트 Endeavour의 목표, 구조, 전략, 규칙 등을 정의하는 통합 문서입니다.

---

## 1. 프로젝트 비전
- **투자기법 포트폴리오 구축**: 종목이 아니라 전략(기법)들을 포트폴리오처럼 관리.
- **1차 목표**: 유연한 백테스팅 시스템 완성.
- **최종 목표**: 자동매매 실행 시스템으로 확장.

## 2. 핵심 철학
- **유연성**: 전략을 JSON 선언형 구조로 정의 → 누구나 쉽게 전략 추가/수정 가능.
- **현실성**: 실제 시장 체결과 유사한 규칙(T+1 시가 체결, 수수료/슬리피지 반영) 적용.
- **확장성**: 한국시장 → 해외시장까지 확장 가능(yfinance, pykrx 병행).

## 3. 프로젝트 연혁
- **1차 시도 (Gemini)**: 전체 코드를 한 번에 제시, 의도와 불일치, 기초공사 실패로 중단.
- **2차 시도 (Gemini)**: milestone 단위 점진적 개발, 그러나 버전관리 부재와 막판 수정 실패로 중단.
- **3차 시도 (ChatGPT)**: Git 기반 버전관리, IPD/CHANGE_LOG/README 체계적 관리, 작은 단위 검증.

## 4. 데이터 전략
- **1단계(MVP)**: yfinance로 KOSPI 30, KOSDAQ 10개 종목의 5년치 일봉 확보.
- **강화 단계**: pykrx 기반 데이터 파이프라인 별도 구축 → 결측치·생존편향 보완.
- **데이터 캐싱**: 로컬 CSV 저장소, 재현성 확보.

## 5. 전략 정의(JSON)
- 구성 요소: `metadata`, `universe_filters`, `indicators`, `entry_rules`, `exit_rules`, `position_size`.
- 연산자: `> < == crosses_above/below` + AND/OR 중첩 논리.
- 기본값: `position_size = 1.0` (100% 자본 투입).

## 6. 전략 추출 절차
- GPTs 프롬프트 기반으로 유튜브 자막/문서/스크립트에서 전략 규칙 추출.
- JSON 스키마에 맞춰 전략 파일 생성.
- human_reviewed 여부를 확인 후 백테스트 투입.
- Git에 커밋 + CHANGE_LOG에 기록.

### GPTs 프롬프트 템플릿
당신은 세계 최고 수준의 퀀트/백테스트 전문가다.
내가 유튜브 자막/문서/스크립트를 제공하면,
이를 분석해서 매매전략을 표준 JSON 스키마에 맞추어 변환해라.

요구사항:

1. JSON은 반드시 유효해야 한다.
2. 전략의 이름, 설명, 원본 출처(링크/자막 발췌), 생성시각을 기록한다.
3. entry_rules와 exit_rules는 연산자(operator), 좌변(left), 우변(right) 구조로 작성한다.
4. 불확실한 값은 notes 필드에 기록하고 confidence 점수를 낮게 준다.
5. position_size는 기본 1.0으로 설정한다.
6. 출력은 JSON 단일 객체로만 한다.

### JSON 스키마 예시
```json
{
  "strategy_id": "yt_20250923_demo_001",
  "name": "SMA_Crossover_With_RSI",
  "description": "50일 SMA가 200일 SMA를 상향 돌파하고 RSI(14)가 50 이상일 때 매수, 반대시 매도",
  "source": {
    "origin_url": "https://youtube.com/xxxxx",
    "origin_type": "youtube",
    "transcript_snippet": "50일 이동평균선이 200일 이동평균선을 돌파하면...",
    "timestamp_in_source": "00:03:45-00:04:20"
  },
  "extracted_at": "2025-09-23T19:00:00+09:00",
  "extractor_version": "v0.1",
  "confidence": 0.9,
  "human_reviewed": false,
  "position_size": 1.0,
  "indicators": [
    {"id": "sma50", "type": "SMA", "params": {"period": 50, "source": "Close"}},
    {"id": "sma200", "type": "SMA", "params": {"period": 200, "source": "Close"}},
    {"id": "rsi14", "type": "RSI", "params": {"period": 14, "source": "Close"}}
  ],
  "entry_rules": {
    "logic": "AND",
    "conditions": [
      {"op": "crosses_above", "left": "sma50", "right": "sma200"},
      {"op": ">", "left": "rsi14", "right": 50}
    ]
  },
  "exit_rules": {
    "logic": "OR",
    "conditions": [
      {"op": "crosses_below", "left": "sma50", "right": "sma200"}
    ]
  },
  "notes": "RSI 조건은 스크립트에 '과매수 진입 방지'라고 표현되어 있었음."
}
7. 백테스트 엔진
프로토타입: backtesting.py로 간단 전략 검증.

프로덕션: Backtrader (현실성·다종목 처리), 필요시 VectorBT(속도·대량 파라미터 튜닝) 병행.

8. 체결 규칙 & 자본배분
체결 규칙: 신호일(T) 종가 기준 → T+1 시가 체결.

자본 배분: 연구단계는 100% 투입 고정. 단, JSON 스키마에 position_size 옵션으로 민감도 실험 허용.

9. 성과 측정 지표
수익성: 총수익률, CAGR.

안정성: MDD, 변동성.

위험조정: 샤프지수, (옵션) 소르티노.

거래단위 성과: 승률, 손익비, 프로핏팩터.

기간별 성과: 연도별/분기별 수익률.

10. 산출물과 시각화
개별 종목: 에쿼티 커브, 매수·매도 마커, 거래 로그.

집계 보고서: 종목별 성과표, 전략별 성과 분포, 연도별 결과.

시각화 도구: Plotly, QuantStats 대시보드.

11. 프로젝트 구조
Phase-1 단순화 구조
bash
코드 복사
Endeavour/
  src/           # 엔진 코드
  strategies/    # 전략 JSON
  data/          # 캐시 데이터
  reports/       # 리포트 산출물
  universe.csv   # 테스트 유니버스 정의
12. Git 운영
최소형 Git Flow(main / dev / feat/*).

원칙 강화: 한 변경축 = 한 커밋, 실패 시 즉시 롤백.

주요 마일스톤마다 커밋 요청: JSON 스키마 확정, 프로토타입 백테스트 성공, Backtrader 파서 작동 등.

13. 단계별 로드맵
Phase-1 단순화 구조 확정: 불필요한 세분화 제거, 5개 축 유지.

킥오프: SMA 크로스 예제 JSON으로 스모크 테스트.

데이터 확보: yfinance 파이프라인, pykrx 보조 설계.

전략 JSON/룰엔진: 스키마와 파서 구현.

프로토타입 엔진: backtesting.py 검증.

프로덕션 엔진: Backtrader 전환, 수수료/슬리피지 반영.

확장: VectorBT로 대량 파라미터 실험, 전략군 확대.
