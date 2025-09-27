# 🗂️ Endeavour 프로젝트 인수인계 패키지

## 1. 현재 프로젝트 구조
Endeavour/
├─ src/
│ └─ endeavour/
│ └─ utils/
│ └─ data_handler.py # T-1 영업일 적용, yfinance+pykrx 안정화 버전 (~300 lines)
├─ docs/
│ ├─ 프로젝트청사진.md # Phase별 청사진 & 진행현황
│ ├─ IPD.md # Initial Project Document
│ ├─ CHANGE_LOG.md # 변경 이력
│ └─ README.md # Root에서 링크됨
├─ data/
│ ├─ cache/ # 종목별 CSV 캐시
│ └─ logs/ # 실행 로그
└─ README.md (root) # docs/ 문서 모음으로 리다이렉션

markdown
코드 복사

## 2. 핵심 코드
- **`src/endeavour/utils/data_handler.py`**
  - 기능: 주가 데이터 로딩 (yfinance + pykrx), 캐시 저장, 데이터 검증, 로그 기록
  - 특징: 
    - T-1 영업일 자동 적용 (주말/공휴일 고려)
    - 캐시 구조: `data/cache/{ticker}_{start}_{end}.csv`
    - 로그 저장: `data/logs/data_handler.log`
  - 현재 안정화 버전 (~300 lines)

## 3. 핵심 문서
- **프로젝트청사진.md** → Phase별 계획 & 진행 현황
- **IPD.md** → 초기 설계 문서
- **CHANGE_LOG.md** → 날짜별 변경 이력
- **README.md (root)** → `docs/` 폴더 문서로 링크

## 4. 외부 공유 리소스
- Google Drive 공유 폴더 (문서 백업 & 레퍼런스)
  - 🔗 https://drive.google.com/drive/folders/1PoOdQS3BzKvY0zfHfmo1bABzRbuFHf0f?usp=sharing

## 5. 다음 단계 권장 과업
1. **Iteration 2 시작 준비**  
   - 병렬 백테스트 엔진 (`src/engines/parallel_runner.py`) 정비  
   - `Iteration_1_WorkOrder.md` 완료사항 기반 후속 설계

2. **데이터 품질 개선**  
   - 캐시 유효성 검증 자동화  
   - 결측치 처리 및 리포트 고도화

3. **CI/CD 파이프라인 준비**  
   - GitHub Actions로 테스트 자동화  
   - requirements.txt / pyproject.toml 정리

## 🌟 Vision & Target Deliverable

### 1. 최종 목표 (Vision)
- 상용 백테스팅/리서치 엔진 이상 수준
- 모듈형, 확장성, 해외주식 확장 고려
- Git/GDrive/Docs 일체형 관리

### 2. 중간 산출물 (Milestones)
- 안정적인 데이터 핸들러 (~300줄, yfinance+pykrx, 캐싱, T-1 영업일 적용)
- 병렬 백테스트 프로토타입 (Phase 1)
- 문서 체계 (IPD, CHANGE_LOG, 청사진, Migration_pack)

### 3. 최종 산출물 (Deliverables)
- 백테스팅 엔진 패키지 (pip 배포 가능 수준)
- 자동화된 Git+Docs 파이프라인
- 금융 데이터 연구용 RAG-세컨브레인 연동

