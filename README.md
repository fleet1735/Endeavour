# 🚀 Endeavour – 멀티 전략 백테스팅 엔진

## 개요
Endeavour는 KOSPI/KOSDAQ 종목을 대상으로 하는 유연한 멀티-전략 백테스팅 엔진입니다.
전략은 JSON 기반으로 정의되며, 엔진은 이를 해석·검증·실행합니다.

## 주요 특징
- 데이터 소스: 1차 yfinance, 2차 pykrx 폴백
- 캐시/로그/리포트: data/cache, data/logs, reports/data_quality
- 전략 정의: JSON 스키마 기반 entry/exit 규칙

## 운영 원칙 (요약)
- repoRoot 기반 절대경로 저장 (System32 등 오염 방지)
- Here-Doc 규칙: 내부에 코드블럭 태그 금지, UTF-8 No BOM
- 소통*.txt: 로컬 컨텍스트 확장용, Git 무시
- 일회성 스크립트는 Archives/ 이동
- CHANGE_LOG는 기존 기록 보존 + 상단 Append 방식으로 관리

## 문서 관리 체계 (docs/)
- IPD.md – 비전·철학·운영 원칙
- Migration_pack.md – 인수인계 전용
- 프로젝트청사진.md – 로드맵/개요
- CHANGE_LOG.md – 변경 내역
- GPT5_Routing_v2.md / Note.md – 라우팅 프롬프트와 지침

## 설치 및 실행
1) 저장소 클론: git clone https://github.com/fleet1735/Endeavour.git
2) 이동: cd Endeavour
3) 의존성 설치: pip install -r requirements.txt
4) 실행: python main.py

## 폴더 구조
src/endeavour/utils/    # 엔진 유틸
data/cache/             # 캐시
data/logs/              # 실행 로그
reports/data_quality/   # 검증 리포트
docs/                   # 문서 (IPD, Migration_pack, CHANGE_LOG, 프로젝트청사진 등)
Archives/               # 일회성 스크립트/보관 자료



