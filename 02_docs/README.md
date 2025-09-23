# Endeavour Project

이 저장소는 개인 프로젝트 **Endeavour**의 소스 코드, 문서, 보고서를 포함합니다.

---

## 개요

Endeavour 프로젝트는 **투자기법 포트폴리오** 구축을 목표로 하며, 여러 매매 기법들을 JSON 기반 선언형 구조로 정의하고, 백테스팅을 통해 수익성과 안정성을 검증합니다. 최종적으로는 자동매매 실행까지 확장하는 것을 비전으로 합니다.

## 주요 문서

* **IPD.md**: 프로젝트 목표, 구조, 전략, 규칙을 정의한 통합 설계 문서.
* **CHANGE\_LOG.md**: 모든 변경 이력 추적.
* **README.md**: 프로젝트 개요와 저장소 설명.

## 시스템 구성

* **데이터**: yfinance (MVP), pykrx (보강용)으로 KOSPI/KOSDAQ 종목 5년치 일봉 확보.
* **전략 정의**: JSON 파일 기반, 지표·룰·논리를 모듈식 선언.
* **백테스트 엔진**: backtesting.py(프로토타입) → Backtrader(프로덕션), 필요시 VectorBT.
* **체결 규칙**: 신호일 종가 판단, T+1 시가 체결.
* **자본 배분**: 연구단계 100% 투입, JSON에서 `position_size`로 조정 가능.

## 성과 지표

* 수익성: 총수익률, CAGR.
* 안정성: MDD, 변동성.
* 위험조정: 샤프지수.
* 거래 단위: 승률, 손익비, 프로핏팩터.
* 기간별: 연도/분기 수익률.

## 프로젝트 구조

```
Endeavour/
  data/
  strategies/
  src/
  reports/
  tests/
```

## Git Flow

* 최소형 흐름: `main` / `dev` / `feat/*`
* 주요 마일스톤마다 커밋 기록: JSON 스키마, 프로토타입 성공, Backtrader 파서 구현 등.

## 로드맵

1. 킥오프: 폴더/requirements 세팅, SMA 크로스 JSON.
2. 데이터 확보: yfinance, pykrx 보조 설계.
3. JSON/룰엔진 구축.
4. 프로토타입(backtesting.py).
5. 프로덕션(Backtrader).
6. 확장(VectorBT, 전략군 확대).
