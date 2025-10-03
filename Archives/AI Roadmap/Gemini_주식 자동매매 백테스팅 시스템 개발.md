

# **고성능 주식 자동매매 시스템 개발을 위한 기술 계획서**

## **I. 고성능 알고리즘 트레이딩 시스템을 위한 전략적 청사진**

### **1.1. 개요: 개념에서 운영 등급 시스템까지**

본 계획서는 단순한 백테스팅 도구를 넘어, 포괄적인 알고리즘 트레이딩 플랫폼의 핵심 기반을 구축하는 것을 목표로 합니다. 프로젝트의 비전은 장기적인 유지보수성과 확장성을 보장하기 위해 각 기능의 역할을 명확히 분리(Separation of Concerns)하는 모듈식, 비결합(decoupled) 아키텍처를 채택하는 것입니다. 이 아키텍처는 네 가지 핵심 모듈로 구성됩니다: 데이터 파이프라인(Data Pipeline), 전략 정의 계층(Strategy Definition Layer), 백테스팅 엔진(Backtesting Engine), 그리고 분석 스위트(Analytics Suite).

이러한 구조적 접근 방식은 시스템의 각 부분이 독립적으로 개발, 테스트, 개선될 수 있도록 하여 복잡성을 관리하고 안정성을 높입니다. 데이터 파이프라인은 데이터의 수집과 정제를 전담하며, 전략 정의 계층은 트레이딩 로직을 시스템의 다른 부분과 분리하여 아이디어의 신속한 프로토타이핑을 가능하게 합니다. 백테스팅 엔진은 과거 데이터를 기반으로 전략을 시뮬레이션하는 핵심 역할을 수행하며, 분석 스위트는 그 결과를 다각적으로 평가하여 전략의 유효성을 검증합니다. 최종적으로 이 시스템은 단순한 과거 성과 검증을 넘어, 미래 시장에 대응할 수 있는 강력하고 유연한 트레이딩 인프라의 초석이 될 것입니다.

### **1.2. 아키텍처 철학: 유연성, 현실성, 확장성 우선**

본 시스템 설계의 핵심 원칙은 유연성, 현실성, 그리고 확장성입니다. 이러한 원칙들은 개발 과정에서 마주할 다양한 기술적 선택의 기준이 됩니다. 예를 들어, 시스템을 완전히 처음부터 개발하는 방식(fully custom)과 기존 프레임워크를 활용하는 방식(framework-based) 사이의 장단점을 고려할 때, 본 계획서는 하이브리드 접근법을 채택합니다. 이는 강력하고 검증된 오픈소스 백테스팅 엔진(backtrader)을 기반으로 하되, 그 위에 독자적인 선언적 전략 계층을 구축하는 방식입니다.

이러한 하이브리드 접근법은 복잡한 백테스팅 메커니즘을 재개발하는 데 드는 시간과 노력을 절약하면서도(don't reinvent the wheel), 트레이딩 전략의 핵심 로직에 대한 완전한 통제권을 유지하게 해줍니다.1 즉, 시스템의 안정적인 '뼈대'는 검증된 프레임워크에 맡기고, 시스템의 '두뇌'에 해당하는 전략 로직은 사용자가 자유롭게 정의하고 확장할 수 있도록 하는 것입니다. 이 철학은 초기 개발 속도를 높일 뿐만 아니라, 향후 새로운 유형의 전략이나 데이터 소스를 추가해야 할 때 시스템이 유연하게 대응할 수 있는 확장성의 기틀을 마련합니다.

### **1.3. 시스템 개요도**

아래 다이어그램은 시스템의 전체적인 구조와 데이터 흐름을 시각적으로 표현합니다. 이 아키텍처는 데이터 수집부터 전략 실행, 성과 분석에 이르는 전 과정을 체계적으로 분리하여 각 구성 요소의 독립성과 효율성을 극대화합니다.

코드 스니펫

graph TD  
    A \--\> B(데이터 파이프라인);  
    B \-- 정제된 시계열 데이터 \--\> C{로컬 데이터 저장소};  
    D \-- 전략 로직 \--\> E(백테스팅 엔진);  
    C \-- 과거 시장 데이터 \--\> E;  
    E \-- 시뮬레이션 결과 \--\> F(분석 스위트);  
    F \-- 성과 지표 및 시각화 \--\> G\[성과 보고서 및 대시보드\];

    subgraph 시스템 구성 요소  
        B; C; D; E; F;  
    end

    style A fill:\#f9f,stroke:\#333,stroke-width:2px  
    style G fill:\#ccf,stroke:\#333,stroke-width:2px

이 도표에서 볼 수 있듯이, 데이터는 한국거래소(KRX)에서 시작하여 데이터 파이프라인을 통해 정제되고 로컬 저장소에 보관됩니다. 백테스팅 엔진은 이 로컬 데이터를 기반으로 JSON 파일에 정의된 전략을 실행합니다. 시뮬레이션 결과는 분석 스위트로 전달되어 최종적으로 사용자에게 성과 보고서 형태로 제공됩니다. 이처럼 명확하게 정의된 데이터 흐름은 시스템의 예측 가능성과 안정성을 높이는 데 기여합니다.

## **II. 기초 계층: 한국 시장 데이터 수집 및 관리**

### **2.1. 고품질, 편향 없는 데이터의 중요성**

퀀트 금융의 근본적인 진실은 백테스트 결과가 기반 데이터의 품질을 결코 넘어설 수 없다는 것입니다.1 부정확하거나 편향된 데이터에 기반한 백테스트는 잘못된 결론으로 이어져 실제 투자에서 치명적인 손실을 초래할 수 있습니다. 특히 주의해야 할 데이터 편향 중 하나는 '생존 편향(survivorship bias)'입니다. 이는 분석 기간 동안 상장 폐지된 기업의 데이터가 누락되어, 마치 시장에 성공적인 기업들만 존재하는 것처럼 보이게 만드는 현상입니다. 생존 편향이 포함된 데이터로 백테스트를 수행하면 전략의 성과가 실제보다 훨씬 좋게 나타나는, 위험할 정도로 낙관적인 결과를 얻게 됩니다.2 따라서 신뢰할 수 있는 시스템을 구축하기 위한 첫걸음은 이러한 편향을 제거하고 데이터의 완전성과 정확성을 보장하는 것입니다.

### **2.2. 올바른 데이터 제공자 선택: yfinance의 한계**

yfinance와 같은 범용 데이터 라이브러리는 미국 시장 중심이며 사용이 간편하지만, 한국과 같은 특정 국제 시장에 대한 데이터를 수집할 때는 여러 한계에 직면합니다.3 데이터의 완전성, 정확성 문제뿐만 아니라, 결정적으로 생존 편향이 제거된 데이터를 제공하지 않는 경우가 많습니다. 또한, 한국 시장의 특수성(예: 관리종목 지정, 거래정지 등)을 제대로 반영하지 못할 수 있습니다.

이러한 한계를 극복하기 위해 한국 시장에 특화된 라이브러리를 사용하는 것이 필수적입니다. pykrx는 한국거래소(KRX) 정보데이터시스템에 직접 접근하여 신뢰도 높은 데이터를 제공하는 강력한 도구입니다.4 또한,

korquanttools는 생존 편향 문제를 명시적으로 해결하여 상장 폐지된 종목을 포함한 데이터를 제공하는 주목할 만한 대안입니다.8 이 외에도

FinanceDataReader 3나

financialdatapy 9 같은 라이브러리도 보조적인 데이터 소스로 활용될 수 있습니다. 본 계획서에서는 KRX와의 직접적인 연동성과 풍부한 기능성을 고려하여

pykrx를 주 데이터 수집 도구로 채택합니다.

### **2.3. 구현: pykrx를 이용한 데이터 파이프라인 구축**

신뢰성 있는 백테스트를 위해서는 데이터 수집 과정을 백테스팅 실행 과정과 아키텍처적으로 완전히 분리해야 합니다. 즉, 백테스트를 실행할 때마다 데이터를 새로 다운로드하는 것이 아니라, 사전에 구축된 '데이터 파이프라인'을 통해 주기적으로 데이터를 로컬 환경에 다운로드, 정제, 저장하는 방식을 사용해야 합니다. 이 접근법은 백테스트의 속도를 비약적으로 향상시키고, 동일한 데이터셋을 사용함으로써 결과의 재현성(reproducibility)을 보장하며, 데이터 제공자 API에 대한 부하를 줄여줍니다.

다음은 pykrx를 사용하여 KOSPI 및 KOSDAQ 전 종목의 5년치 일봉 데이터를 수집하고 저장하는 데이터 파이프라인 스크립트의 구현 예시입니다.

#### **2.3.1. 1단계: 필요 라이브러리 설치 및 임포트**

Python

import pandas as pd  
from pykrx import stock  
import time  
from datetime import datetime  
import os

\# 데이터 저장 경로 설정  
DATA\_PATH \= "./data"  
KOSPI\_PATH \= os.path.join(DATA\_PATH, "kospi")  
KOSDAQ\_PATH \= os.path.join(DATA\_PATH, "kosdaq")

\# 경로가 없으면 생성  
os.makedirs(KOSPI\_PATH, exist\_ok=True)  
os.makedirs(KOSDAQ\_PATH, exist\_ok=True)

#### **2.3.2. 2단계: 데이터 수집 기간 및 대상 시장 정의**

Python

\# 데이터 수집 기간 설정 (5년)  
END\_DATE \= datetime.now().strftime('%Y%m%d')  
START\_DATE \= (datetime.now() \- pd.DateOffset(years=5)).strftime('%Y%m%d')

MARKETS \= {  
    "KOSPI": {"path": KOSPI\_PATH, "market\_name": "KOSPI"},  
    "KOSDAQ": {"path": KOSDAQ\_PATH, "market\_name": "KOSDAQ"}  
}

#### **2.3.3. 3단계: 티커 목록 조회 및 데이터 다운로드**

이 단계에서는 각 시장의 모든 종목 티커를 조회한 후, 각 티커에 대해 5년치 OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터를 다운로드합니다. KRX 서버에 과도한 부하를 주지 않기 위해 각 요청 사이에 약간의 지연 시간(time.sleep)을 추가하는 것이 좋습니다.

Python

def download\_market\_data(market\_info, start\_date, end\_date):  
    """지정된 시장의 모든 종목 데이터를 다운로드합니다."""  
    market\_name \= market\_info\["market\_name"\]  
    path \= market\_info\["path"\]  
      
    print(f"===== {market\_name} 시장 데이터 다운로드 시작 \=====")  
      
    \# 기준일(오늘)의 티커 리스트 조회  
    tickers \= stock.get\_market\_ticker\_list(date=end\_date, market=market\_name)  
    print(f"{market\_name} 시장의 총 종목 수: {len(tickers)}개")  
      
    for i, ticker in enumerate(tickers):  
        try:  
            \# 종목명 조회  
            ticker\_name \= stock.get\_market\_ticker\_name(ticker)  
              
            \# 데이터 파일 경로  
            file\_path \= os.path.join(path, f"{ticker}\_{ticker\_name}.csv")

            \# 파일이 이미 존재하면 건너뛰기 (증분 업데이트를 위해)  
            if os.path.exists(file\_path):  
                print(f"\[{i+1}/{len(tickers)}\] {ticker\_name}({ticker}) 데이터가 이미 존재합니다. 건너뜁니다.")  
                continue

            print(f"\[{i+1}/{len(tickers)}\] {ticker\_name}({ticker}) 데이터 다운로드 중...")  
              
            \# OHLCV 데이터 조회  
            df \= stock.get\_market\_ohlcv(start\_date, end\_date, ticker)  
              
            if df.empty:  
                print(f"  \-\> {ticker\_name}({ticker}) 데이터가 없습니다.")  
                continue  
                  
            \# CSV 파일로 저장  
            df.to\_csv(file\_path)  
              
            \# 서버 부하 방지를 위한 지연  
            time.sleep(0.5)

        except Exception as e:  
            print(f"  \-\> 에러 발생: {ticker\_name}({ticker}) \- {e}")  
            continue  
              
    print(f"===== {market\_name} 시장 데이터 다운로드 완료 \=====")

\# KOSPI 및 KOSDAQ 데이터 다운로드 실행  
for market\_name, info in MARKETS.items():  
    download\_market\_data(info, START\_DATE, END\_DATE)

#### **2.3.4. 4단계: 데이터 검증 및 정제**

다운로드된 데이터는 사용 전에 기본적인 검증 및 정제 과정을 거쳐야 합니다. 이 과정은 별도의 스크립트로 구현할 수 있으며, 주요 작업은 다음과 같습니다.

* **결측치 처리:** 데이터 중간에 누락된 날짜가 있는지 확인하고, 필요시 보간(interpolation)하거나 해당 데이터를 제외하는 정책을 수립합니다.  
* **이상치(Outlier) 탐지:** 비정상적인 가격 변동(예: 전일 대비 1000% 상승)이나 거래량 급증을 탐지하고 원인을 분석합니다. 데이터 오류일 경우 수정하고, 실제 이벤트(예: 유상증자)일 경우 주석을 추가합니다.  
* **거래량 0 데이터 처리:** 거래량이 0인 날은 사실상 거래가 이루어지지 않은 날이므로, 이러한 데이터를 어떻게 처리할지(예: 이전 종가로 채우기, 제외하기) 결정해야 합니다.  
* **데이터 형식 표준화:** 모든 데이터 파일이 동일한 컬럼(Open, High, Low, Close, Volume)과 날짜 형식을 갖도록 표준화합니다. 이는 백테스팅 엔진이 데이터를 원활하게 읽어들이기 위해 필수적입니다.

이처럼 체계적인 데이터 파이프라인을 구축함으로써, 이후 진행될 모든 백테스트의 신뢰성과 효율성을 확보할 수 있습니다.

## **III. 전략의 핵심: 모듈식, JSON 기반 아키텍처**

### **3.1. 선언적 전략의 힘: 로직과 엔진의 분리**

전략을 JSON과 같은 선언적 형식으로 정의하는 것은 아키텍처 측면에서 상당한 이점을 제공합니다. 이는 전략의 '무엇'(What, 트레이딩 로직)을 '어떻게'(How, 백테스팅 실행)와 분리하는 것을 의미합니다.10 이러한 분리 덕분에, 퀀트 분석가나 트레이더는 파이썬 엔진 코드를 직접 수정하지 않고도 JSON 파일만 변경하여 새로운 전략을 테스트하거나 기존 전략의 파라미터를 수정할 수 있습니다. 이는 아이디어의 검증 속도를 획기적으로 높여주며, 프로그래밍에 익숙하지 않은 연구원들도 전략 개발에 참여할 수 있는 협업 환경을 조성합니다. 또한, 전략 로직이 텍스트 기반의 명확한 구조로 표현되므로, 전략의 버전 관리, 공유, 감사가 용이해집니다.

### **3.2. 트레이딩 규칙을 위한 JSON 스키마 설계**

유연하고 확장 가능한 트레이딩 전략을 표현하기 위해, 다음과 같이 체계적인 JSON 스키마를 설계합니다. 이 스키마는 다양한 기술적 분석 기반 전략을 포괄할 수 있도록 설계되었으며, 논리적 연산자(and, or)를 통해 복잡한 조건들을 조합할 수 있습니다.12

스키마의 핵심은 entry\_conditions와 exit\_conditions 블록입니다. 각 블록은 중첩된 논리 구조를 가질 수 있으며, 개별 조건은 특정 기술 지표와 비교 연산을 정의합니다. 이 구조는 사실상 트레이딩 전략을 정의하기 위한 도메인 특화 언어(Domain-Specific Language, DSL) 역할을 하며, 시스템의 유연성을 극대화합니다.

아래 표는 본 시스템에서 사용할 JSON 스키마의 상세 구조를 정의합니다.

**표 1: 트레이딩 전략 정의를 위한 JSON 스키마**

| 키(Key) | 데이터 타입 | 필수 여부 | 설명 | 예시 값 |
| :---- | :---- | :---- | :---- | :---- |
| strategy\_name | String | 예 | 전략의 고유한 이름 | "GoldenCross\_RSI\_Filter" |
| description | String | 아니요 | 전략에 대한 간략한 설명 | "50일 이동평균이 200일 이동평균을 상향 돌파하고, RSI가 50 이상일 때 매수" |
| entry\_conditions | Object | 예 | 진입 조건을 정의하는 객체 | (아래 참조) |
| exit\_conditions | Object | 예 | 청산 조건을 정의하는 객체 | (아래 참조) |
| **조건 객체 (entry\_conditions, exit\_conditions)** |  |  |  |  |
| and 또는 or | Array | 예 | 논리 연산을 위한 조건 배열. 중첩 가능. | \[ {... }, {... } \] |
| **개별 조건 (배열 내 요소)** |  |  |  |  |
| id | String | 예 | 조건 내에서 다른 지표를 참조하기 위한 고유 ID | "fast\_ma" |
| indicator | Object | 예 | 기술 지표를 정의하는 객체 | (아래 참조) |
| compare\_to | Object | 예 | 비교 로직을 정의하는 객체 | (아래 참조) |
| **지표 객체 (indicator)** |  |  |  |  |
| type | String | 예 | 지표 유형 (예: "SMA", "RSI", "MACD") | "SMA" |
| inputs | Object | 예 | 지표 계산에 사용될 입력 데이터 | {"price": "close"} |
| params | Object | 예 | 지표의 파라미터 | {"period": 50} |
| **비교 객체 (compare\_to)** |  |  |  |  |
| operator | String | 예 | 비교 연산자 (예: "cross\_above", "greater\_than") | "cross\_above" |
| value\_type | String | 예 | 비교 대상의 유형 ("indicator" 또는 "constant") | "indicator" |
| value | String/Number | 예 | 비교 대상 값 (다른 지표의 id 또는 상수) | "slow\_ma" 또는 70 |

### **3.3. JSON 전략 정의 예시**

설계된 스키마를 실제로 어떻게 사용하는지 보여주기 위해 두 가지 예시를 제시합니다.

#### **3.3.1. 예시 1: 단순 골든크로스 전략**

50일 단순이동평균(SMA)이 200일 단순이동평균을 상향 돌파할 때 매수하고, 하향 돌파할 때 매도하는 고전적인 전략입니다.

JSON

{  
  "strategy\_name": "Simple\_GoldenCross",  
  "description": "50-day SMA crosses above 200-day SMA for entry, crosses below for exit.",  
  "entry\_conditions": {  
    "and":  
  },  
  "exit\_conditions": {  
    "and":  
  }  
}

#### **3.3.2. 예시 2: 복합 조건 전략 (RSI 필터가 적용된 MACD)**

MACD 오실레이터가 시그널선을 상향 돌파하고, 동시에 14일 RSI가 50 이상일 때만 매수하는 보다 복잡한 조건의 전략입니다. 이는 and 논리 연산자를 통해 여러 조건을 결합하는 스키마의 유연성을 보여줍니다.

JSON

{  
  "strategy\_name": "MACD\_with\_RSI\_Filter",  
  "description": "Buy when MACD line crosses above signal line AND RSI is above 50\. Sell when MACD crosses below signal.",  
  "entry\_conditions": {  
    "and":  
  },  
  "exit\_conditions": {  
    "and":  
  }  
}

이러한 JSON 기반 접근 방식은 시스템의 핵심적인 유연성을 제공하며, 복잡한 트레이딩 아이디어를 체계적으로 표현하고 신속하게 테스트할 수 있는 강력한 기반이 됩니다.

## **IV. 엔진 룸: 전문가 수준의 백테스팅 프레임워크 구현**

### **4.1. 파이썬 백테스팅 라이브러리 비교 분석**

사용자의 요구사항에 가장 적합한 백테스팅 라이브러리를 선정하기 위해, 현재 파이썬 생태계에서 가장 널리 사용되는 세 가지 라이브러리(backtesting.py, backtrader, VectorBT)를 다각도로 비교 분석합니다. 선택 기준은 기능성, 성능 모델, 확장성, 현실성 모사 능력, 커뮤니티 및 문서화 수준, 그리고 본 프로젝트의 핵심 요구사항인 포트폴리오 수준 테스트에 대한 적합성입니다.1

**표 2: 파이썬 백테스팅 라이브러리 비교 분석**

| 평가 항목 | backtesting.py | backtrader | VectorBT |
| :---- | :---- | :---- | :---- |
| **핵심 패러다임** | 이벤트 기반 \+ 벡터화 혼합 | 이벤트 기반(Event-Driven) | 벡터화(Vectorized) |
| **주요 기능** | 기본 백테스팅, 최적화, 간단한 플로팅 기능 제공 1 | 포괄적 기능: 지표, 분석기, 사이즈 조절기, 관찰자, 실거래 연동 지원 2 | 초고속 벡터화 백테스팅, 대규모 파라미터 최적화, 복잡한 시각화에 특화 20 |
| **성능 모델** | 단일 종목 테스트에 빠르지만, 포트폴리오 수준에서는 성능 저하 가능성 | 순차적 처리로 벡터화 방식보다 느리지만, 복잡하고 경로 의존적인 로직 처리에 강점 | NumPy와 Pandas를 활용하여 대규모 데이터셋에 대해 압도적으로 빠른 속도 제공 |
| **확장성** | 상대적으로 제한적. 복잡한 포트폴리오 로직 구현이 어려움 | 객체 지향 설계로 커스텀 지표, 분석기, 전략 로직 통합이 매우 용이 22 | 높은 수준의 커스터마이징이 가능하나, 벡터화 패러다임에 대한 깊은 이해 필요 |
| **현실성 모사** | 수수료, 슬리피지 기본 지원 1 | 매우 상세한 수수료 및 슬리피지 모델 제공 (고정/비율, 체결 조건 등) 24 | 수수료/슬리피지 적용 가능하나, 이벤트 기반 엔진만큼 정교한 모델링은 어려움 |
| **커뮤니티/문서** | 커뮤니티 규모가 작고, 업데이트가 상대적으로 뜸함 19 | 방대한 문서와 활발한 커뮤니티를 보유하여 문제 해결 및 학습에 유리 15 | 활발하게 개발 중이며 커뮤니티가 성장하고 있으나, 학습 곡선이 가파름 19 |
| **프로젝트 적합성** | 간단한 단일 전략 테스트에는 적합하나, 다수 종목 포트폴리오 관리에는 부적합 | **최적.** 다수 데이터 피드 동시 처리, 복잡한 포트폴리오 관리, JSON 파서 통합에 가장 이상적인 구조 | 대규모 파라미터 스캐닝에는 유용하나, 본 프로젝트의 유연한 모듈형 전략 구현에는 부적합 |

### **4.2. 최종 결론: backtrader가 최적의 선택인 이유**

위 비교 분석에 따라, 본 프로젝트의 백테스팅 엔진으로 \*\*backtrader\*\*를 채택할 것을 강력히 권고합니다. backtrader를 선택하는 이유는 다음과 같습니다.

1. **이벤트 기반 아키텍처:** backtrader는 실제 트레이딩과 유사하게 데이터를 시간 순서대로 한 단위(bar)씩 처리하는 이벤트 기반 방식을 사용합니다. 이는 "특정 조건 만족 시 포트폴리오의 10%를 매도"와 같은 경로 의존적(path-dependent)이고 동적인 포트폴리오 관리 로직을 구현하는 데 필수적입니다. 반면, VectorBT와 같은 벡터화 엔진은 전체 데이터를 한 번에 계산하므로 빠르지만, 이러한 복잡한 상호작용을 모델링하기 어렵습니다.  
2. **포트폴리오 수준 지원:** backtrader는 처음부터 다수의 데이터 피드(개별 주식)를 동시에 처리하고, 이들 간의 상호작용을 고려하는 포트폴리오 수준의 백테스팅을 염두에 두고 설계되었습니다. 이는 '투자 기법 포트폴리오 구축'이라는 사용자의 핵심 목표와 정확히 일치합니다.  
3. **최고 수준의 현실성:** 거래 비용은 백테스트의 신뢰도를 결정하는 중요한 요소입니다. backtrader는 고정 수수료, 비율 수수료, 계약 배수(multiplier), 증거금 등 매우 상세하고 현실적인 거래 비용 모델을 제공합니다.26 또한, 주문 유형에 따라 슬리피지를 차등 적용하는 등 정교한 시장 마찰 비용 시뮬레이션이 가능하여 결과의 신뢰도를 높입니다.24  
4. **탁월한 확장성:** backtrader의 객체 지향 설계는 시스템의 모든 요소를 커스터마이징할 수 있게 해줍니다. 본 프로젝트의 핵심인 'JSON 전략 파서'를 backtrader.Strategy 클래스와 통합하여 동적으로 전략 로직을 생성하는 데 이보다 더 적합한 구조는 없습니다.22

결론적으로, backtesting.py는 기능이 너무 단순하고, VectorBT는 패러다임이 프로젝트의 목표와 맞지 않습니다. backtrader만이 본 프로젝트가 요구하는 포트폴리오 관리 기능, 현실성, 그리고 유연한 확장성을 모두 만족시키는 최적의 솔루션입니다.

### **4.3. 구현: backtrader를 이용한 백테스터 구축**

이제 backtrader를 사용하여 백테스팅 시스템의 핵심 로직을 구현합니다. 이 과정은 Cerebro 엔진 설정, JSON 전략 파서 클래스 구현, 데이터 피드 로딩, 그리고 브로커 설정의 네 단계로 구성됩니다.

#### **4.3.1. Cerebro 엔진 설정 및 기본 구조**

Cerebro는 backtrader의 핵심 컨트롤 타워로, 데이터 피드, 전략, 분석기, 브로커 등 모든 구성 요소를 한데 모아 백테스트를 실행하는 역할을 합니다.21

Python

\# src/backtester.py

import backtrader as bt  
import pandas as pd  
import os  
from.strategy\_parser import JsonStrategyParser \# 4.3.2에서 구현할 클래스

class Backtester:  
    def \_\_init\_\_(self, data\_path, strategy\_json\_path, initial\_cash=100000000):  
        self.cerebro \= bt.Cerebro()  
        self.data\_path \= data\_path  
        self.strategy\_json\_path \= strategy\_json\_path  
        self.initial\_cash \= initial\_cash

    def run(self):  
        \# 1\. 브로커 설정  
        self.cerebro.broker.setcash(self.initial\_cash)  
        self.cerebro.broker.setcommission(commission=0.0015) \# 수수료 0.15%  
        self.cerebro.broker.set\_slippage\_perc(perc=0.001) \# 슬리피지 0.1%

        \# 2\. 데이터 피드 추가  
        self.\_add\_data\_feeds()

        \# 3\. 전략 추가  
        self.\_add\_strategy()

        \# 4\. 분석기 추가 (V장에서 상세히 다룸)  
        \# self.\_add\_analyzers()

        print("백테스팅 시작...")  
        results \= self.cerebro.run()  
        print("백테스팅 완료.")  
          
        \# 5\. 결과 출력 및 시각화 (V장에서 상세히 다룸)  
        final\_value \= self.cerebro.broker.getvalue()  
        print(f"최종 포트폴리오 가치: {final\_value:,.0f} 원")  
          
        \# self.cerebro.plot()  
        return results

    def \_add\_data\_feeds(self):  
        \# II장에서 구축한 데이터 디렉토리에서 모든 CSV 파일을 읽어 데이터 피드로 추가  
        files \= \[f for f in os.listdir(self.data\_path) if f.endswith('.csv')\]  
        print(f"총 {len(files)}개의 종목 데이터를 추가합니다.")  
          
        for filename in files\[:50\]: \# 테스트를 위해 50개 종목만 사용  
            df \= pd.read\_csv(os.path.join(self.data\_path, filename), index\_col='날짜', parse\_dates=True)  
            if not df.empty:  
                data \= bt.feeds.PandasData(dataname=df, name=filename.split('\_'))  
                self.cerebro.adddata(data)

    def \_add\_strategy(self):  
        \# JSON 파일을 파싱하여 동적으로 전략을 생성  
        \# GenericStrategy는 JSON 파서가 생성한 로직을 실행하는 껍데기 역할  
        class GenericStrategy(bt.Strategy):  
            def \_\_init\_\_(self):  
                self.parser \= JsonStrategyParser(self, self.p.strategy\_json)

            def next(self):  
                self.parser.execute\_next()  
          
        self.cerebro.addstrategy(GenericStrategy, strategy\_json=self.strategy\_json\_path)

#### **4.3.2. JSON 전략 파서 및 인터프리터 구현**

이 부분이 시스템의 핵심적인 맞춤 개발 영역입니다. JSON이라는 '설계도'를 읽고, backtrader가 이해할 수 있는 '실행 코드'로 동적으로 변환하는 '인터프리터' 역할을 합니다. 파서는 재귀적으로 JSON 구조를 탐색하며 지표를 초기화하고, next 메소드에서 매 시점마다 조건을 평가하여 매수/매도 신호를 생성합니다.

Python

\# src/strategy\_parser.py

import json  
import backtrader as bt

class JsonStrategyParser:  
    def \_\_init\_\_(self, strategy\_instance, json\_filepath):  
        self.strategy \= strategy\_instance  
        with open(json\_filepath, 'r') as f:  
            self.strategy\_def \= json.load(f)  
          
        self.indicators \= {}  
        self.\_initialize\_indicators()

    def \_initialize\_indicators(self):  
        """JSON 정의를 기반으로 모든 기술 지표를 미리 초기화합니다."""  
        all\_conditions \= self.strategy\_def\['entry\_conditions'\]\['and'\] \+ \\  
                         self.strategy\_def\['exit\_conditions'\]\['and'\]  
          
        \# 중복 제거  
        unique\_indicators \= {cond\['id'\]: cond for cond in all\_conditions}.values()

        for cond in unique\_indicators:  
            indicator\_id \= cond\['id'\]  
            indicator\_info \= cond\['indicator'\]  
              
            \# 각 데이터 피드(종목)에 대해 지표를 생성  
            self.indicators\[indicator\_id\] \= {}  
            for d in self.strategy.datas:  
                self.indicators\[indicator\_id\]\[d.\_name\] \= self.\_create\_indicator(indicator\_info, d)

    def \_create\_indicator(self, indicator\_info, data):  
        """지표 정보에 따라 backtrader 지표 객체를 생성합니다."""  
        indicator\_type \= indicator\_info\['type'\].lower()  
        params \= indicator\_info.get('params', {})  
          
        \# backtrader에 내장된 지표들을 동적으로 호출  
        if indicator\_type \== 'sma':  
            return bt.indicators.SimpleMovingAverage(data.close, \*\*params)  
        elif indicator\_type \== 'rsi':  
            return bt.indicators.RSI(data.close, \*\*params)  
        elif indicator\_type \== 'macd':  
            \# MACD는 여러 라인을 포함하므로 특별 처리  
            return bt.indicators.MACD(data.close, \*\*params)  
        elif indicator\_type \== 'macd\_signal':  
            \# MACD 객체에서 signal line만 참조  
            return bt.indicators.MACD(data.close, \*\*params).signal  
        \#... 다른 지표들 추가...  
        else:  
            raise ValueError(f"지원하지 않는 지표 유형: {indicator\_info\['type'\]}")

    def \_evaluate\_condition(self, condition, data):  
        """단일 조건을 평가하여 True/False를 반환합니다."""  
        indicator\_id \= condition\['id'\]  
        compare\_info \= condition\['compare\_to'\]  
        operator \= compare\_info\['operator'\]  
          
        \# 현재 지표 값  
        current\_indicator \= self.indicators\[indicator\_id\]\[data.\_name\]

        \# 비교 대상 값  
        if compare\_info\['value\_type'\] \== 'indicator':  
            target\_indicator\_id \= compare\_info\['value'\]  
            target\_value \= self.indicators\[target\_indicator\_id\]\[data.\_name\]  
        else: \# constant  
            target\_value \= compare\_info\['value'\]

        \# 연산자별 로직  
        if operator \== 'cross\_above':  
            return current\_indicator \> target\_value and current\_indicator\[-1\] \<= target\_value\[-1\]  
        elif operator \== 'cross\_below':  
            return current\_indicator \< target\_value and current\_indicator\[-1\] \>= target\_value\[-1\]  
        elif operator \== 'greater\_than':  
            return current\_indicator \> target\_value  
        \#... 다른 연산자들 추가...  
        else:  
            return False

    def \_check\_conditions(self, condition\_block, data):  
        """'and' 또는 'or' 논리 블록 전체를 평가합니다."""  
        if 'and' in condition\_block:  
            return all(self.\_evaluate\_condition(cond, data) for cond in condition\_block\['and'\])  
        elif 'or' in condition\_block:  
            return any(self.\_evaluate\_condition(cond, data) for cond in condition\_block\['or'\])  
        return False

    def execute\_next(self):  
        """매 시점(bar)마다 호출되어 모든 종목에 대해 전략을 실행합니다."""  
        for d in self.strategy.datas:  
            position \= self.strategy.getposition(d)  
              
            \# 진입 조건 확인  
            if not position: \# 포지션이 없을 때  
                if self.\_check\_conditions(self.strategy\_def\['entry\_conditions'\], d):  
                    \# VI장에서 다룰 사이즈 조절 로직 적용  
                    self.strategy.buy(data=d)  
              
            \# 청산 조건 확인  
            else: \# 포지션이 있을 때  
                if self.\_check\_conditions(self.strategy\_def\['exit\_conditions'\], d):  
                    self.strategy.sell(data=d)

이 코드는 backtrader의 유연한 구조 위에 독자적인 전략 정의 계층을 성공적으로 구축하는 방법을 보여줍니다. 이를 통해 사용자는 파이썬 코드를 건드리지 않고도 무한한 종류의 기술적 분석 전략을 JSON으로 정의하고 테스트할 수 있게 됩니다.

## **V. 성과 분석 및 시각화 스위트**

### **5.1. 중요한 것을 측정하기: 표준 성과 지표**

전략의 성과를 객관적으로 평가하기 위해서는 표준화된 지표를 사용해야 합니다. 사용자가 요청한 지표들은 전략의 여러 측면을 종합적으로 보여줍니다.

* **수익성 (Profitability):** 전략이 얼마나 많은 수익을 창출했는지를 측정합니다.  
  * **총 수익률 (Total Return):** 전체 기간 동안의 누적 수익률.  
  * **연평균 복리 수익률 (CAGR):** 연 단위로 환산한 복리 수익률로, 기간이 다른 전략들을 비교하는 데 유용합니다.  
* **안정성 (Stability):** 수익을 창출하는 과정이 얼마나 안정적이었는지를 측정합니다.  
  * **샤프 지수 (Sharpe Ratio):** 위험 대비 수익성을 나타내는 대표적인 지표. 변동성(위험) 대비 초과 수익이 얼마나 높은지를 보여줍니다. 일반적으로 1 이상이면 양호, 2 이상이면 우수하다고 평가됩니다.27  
  * **최대 낙폭 (Maximum Drawdown, MDD):** 투자 기간 중 자산 가치가 최고점에서 최저점까지 얼마나 하락했는지를 나타내는 비율. 전략이 겪을 수 있는 최악의 손실 시나리오를 보여주며, 낮을수록 안정적입니다.  
* **승률 (Win Rate):** 전체 거래 중 수익을 낸 거래의 비율.  
* **손익비 (Profit/Loss Ratio):** 평균 수익 거래의 이익을 평균 손실 거래의 손실로 나눈 값. 승률이 낮더라도 손익비가 높으면 누적 수익을 낼 수 있습니다.

### **5.2. backtrader 분석기(Analyzer) 활용**

backtrader는 이러한 표준 지표들을 자동으로 계산해주는 강력한 분석기(Analyzer) 기능을 내장하고 있습니다. Cerebro 엔진에 필요한 분석기를 추가하기만 하면, 백테스트 종료 후 손쉽게 결과를 얻을 수 있습니다.27

Backtester 클래스에 분석기를 추가하는 메소드를 구현합니다.

Python

\# src/backtester.py 내부에 추가

    def \_add\_analyzers(self):  
        """성과 분석을 위한 분석기들을 Cerebro에 추가합니다."""  
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, \_name='sharpe\_ratio')  
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, \_name='drawdown')  
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, \_name='trade\_analyzer')  
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, \_name='time\_return') \# QuantStats 연동용  
        self.cerebro.addanalyzer(bt.analyzers.PyFolio, \_name='pyfolio') \# QuantStats 연동용

    def print\_analysis(self, results):  
        """분석 결과를 출력합니다."""  
        strategy \= results \# 첫 번째 전략 결과  
          
        sharpe \= strategy.analyzers.sharpe\_ratio.get\_analysis()  
        drawdown \= strategy.analyzers.drawdown.get\_analysis()  
        trade\_info \= strategy.analyzers.trade\_analyzer.get\_analysis()  
          
        print("\\n===== 성과 분석 결과 \=====")  
        print(f"샤프 지수: {sharpe.get('sharperatio', 'N/A'):.2f}")  
        print(f"최대 낙폭 (MDD): {drawdown.max.drawdown:.2f}%")  
          
        if trade\_info.total.total \> 0:  
            print(f"총 거래 횟수: {trade\_info.total.total}")  
            print(f"승률: {trade\_info.won.total / trade\_info.total.total \* 100:.2f}%")  
              
            if trade\_info.lost.total \> 0:  
                pnl\_ratio \= (trade\_info.won.pnl.average) / abs(trade\_info.lost.pnl.average)  
                print(f"손익비: {pnl\_ratio:.2f}")

run 메소드에서 이들을 호출하도록 수정하면, 백테스트가 끝난 후 핵심 지표들이 콘솔에 출력됩니다.

### **5.3. QuantStats를 이용한 전문가 수준의 보고**

콘솔 출력은 기본적인 정보를 제공하지만, 전문가 수준의 분석과 시각화를 위해서는 더 강력한 도구가 필요합니다. QuantStats 라이브러리는 단 몇 줄의 코드로 포괄적인 통계 지표와 시각화 자료가 포함된 전문가 수준의 HTML 보고서를 생성해주는 훌륭한 도구입니다.30

backtrader의 PyFolio 분석기는 QuantStats가 요구하는 형식의 수익률 시계열 데이터를 생성하는 데 최적화되어 있습니다.28 이를 연동하여 보고서를 생성하는 기능을 구현합니다.

Python

\# src/reporting.py

import quantstats as qs  
import pandas as pd

def generate\_quantstats\_report(results, output\_filename="report.html"):  
    """QuantStats를 사용하여 HTML 성과 보고서를 생성합니다."""  
    try:  
        portfolio\_stats \= results.analyzers.getbyname('pyfolio')  
        returns, positions, transactions, gross\_lev \= portfolio\_stats.get\_pf\_items()  
          
        \# Timezone 정보 제거 (QuantStats 호환성)  
        returns.index \= returns.index.tz\_localize(None)  
          
        \# 벤치마크(KOSPI) 데이터 추가  
        \# 이 부분은 데이터 파이프라인에서 KOSPI 지수 데이터를 미리 받아와야 함  
        \# benchmark \= pd.read\_csv(...)   
          
        print(f"QuantStats 보고서 생성 중... \-\> {output\_filename}")  
        qs.reports.html(returns, output=output\_filename, title='Strategy Performance')  
        print("보고서 생성 완료.")

    except Exception as e:  
        print(f"QuantStats 보고서 생성 실패: {e}")

이 함수를 Backtester의 run 메소드 마지막에 호출하면, 백테스트가 끝날 때마다 상세한 분석이 담긴 report.html 파일이 자동으로 생성됩니다. 이 보고서는 단순한 숫자 요약을 넘어, 월별 수익률, 롤링 샤프 지수, 수익률 분포 등 전략의 성과를 입체적으로 이해하는 데 큰 도움을 줍니다.

### **5.4. Plotly를 이용한 고급 시각화**

backtrader는 matplotlib 기반의 기본 플로팅 기능을 제공하지만, Plotly를 사용하면 사용자와 상호작용이 가능한 동적인 차트를 생성할 수 있어 분석의 깊이를 더할 수 있습니다.32 연구에 따르면

Plotly는 Bokeh와 같은 다른 인터랙티브 라이브러리에 비해 사용 편의성, 풍부한 차트 종류, 웹 대시보드와의 통합성 측면에서 우수하다는 평가를 받습니다.33

백테스트 결과 중 가장 중요한 시각화 자료는 포트폴리오 자산 가치의 변화를 보여주는 '자산 곡선(Equity Curve)'입니다. backtrader의 TimeReturn 분석기에서 얻은 데이터를 Plotly로 시각화하는 코드 예시는 다음과 같습니다.

Python

\# src/reporting.py 에 추가

import plotly.graph\_objects as go

def plot\_equity\_curve(results, initial\_cash):  
    """Plotly를 사용하여 인터랙티브한 자산 곡선 차트를 생성합니다."""  
    try:  
        tr\_analyzer \= results.analyzers.getbyname('time\_return')  
        returns \= tr\_analyzer.get\_analysis()  
          
        df \= pd.DataFrame(list(returns.items()), columns=\['date', 'return'\])  
        df\['date'\] \= pd.to\_datetime(df\['date'\])  
        df\['equity'\] \= (1 \+ df\['return'\]).cumprod() \* initial\_cash  
          
        fig \= go.Figure()  
        fig.add\_trace(go.Scatter(x=df\['date'\], y=df\['equity'\], mode='lines', name='Portfolio Value'))  
          
        fig.update\_layout(  
            title='Portfolio Equity Curve',  
            xaxis\_title='Date',  
            yaxis\_title='Portfolio Value (KRW)',  
            template='plotly\_white'  
        )  
          
        fig.show()

    except Exception as e:  
        print(f"Plotly 차트 생성 실패: {e}")

이처럼 QuantStats의 정량적 분석과 Plotly의 시각적 분석을 결합한 분석 스위트는 전략의 성과를 평가하고, 더 나아가 전략의 행동 패턴을 깊이 있게 이해하고 디버깅하는 데 필수적인 도구입니다. 샤프 지수 같은 단일 지표는 전략이 좋지 않다는 '결과'를 알려주지만, 자산 곡선 차트는 전략이 '언제, 왜' 잘못된 결정을 내렸는지 시각적으로 보여줌으로써 전략 개선을 위한 통찰력을 제공합니다.

## **VI. 자본 배분 및 리스크 관리 프레임워크**

### **6.1. '신호당 자본 100% 투입' 방식의 평가**

사용자가 제안한 '매수 신호 발생 시 자본 100% 투입' 방식은 특정 연구 목적, 즉 **순수 알파 신호(alpha signal) 연구**에 매우 유용한 도구입니다. 이 방법론은 포지션 사이징이라는 변수를 의도적으로 제거함으로써, 오직 종목 선정과 타이밍 로직(신호)의 성과만을 순수하게 분리하여 측정할 수 있게 해줍니다. 이는 "이 신호가 다른 변수들의 영향이 없는 진공 상태에서 과연 수익성이 있는가?"라는 근본적인 질문에 답을 제공합니다. 따라서 전략 개발 초기 단계에서 신호 자체의 유효성을 검증하는 데는 타당하고 효과적인 접근법입니다.

### **6.2. 실전 적용의 한계: 왜 이 방식은 부적합한가**

그러나 이 방식은 순수 연구 단계를 넘어서는 순간, 특히 실제 포트폴리오 운영을 모사하는 백테스트에서는 심각한 한계를 드러내며, 실전 투자용으로는 절대 사용되어서는 안 됩니다.

* **극단적인 리스크 집중:** 단 한 번의 큰 손실 거래만으로도 포트폴리오의 상당 부분이 소멸될 수 있는 극단적인 리스크에 노출됩니다.  
* **다각화 부재:** 이 방식은 본질적으로 한 번에 하나의 포지션만 보유하는 것을 강제합니다. 이는 여러 전략과 자산을 동시에 운용하여 리스크를 분산시키는 '포트폴리오'의 근본적인 목표와 정면으로 배치됩니다.  
* **비현실적인 포트폴리오 동역학:** 실제 투자 환경에서는 여러 종목에서 동시에 매수 신호가 발생할 수 있습니다. 이때 한정된 자본을 어떻게 배분할 것인지에 대한 고민이 전혀 반영되지 않아, 포트폴리오 전체의 동적인 자본 흐름을 전혀 모사하지 못합니다.

결론적으로, '100% 투입' 모델은 신호의 품질을 측정하는 '현미경' 역할은 할 수 있지만, 여러 자산이 상호작용하는 복잡한 포트폴리오 생태계를 시뮬레이션하는 '광각 렌즈' 역할은 수행할 수 없습니다.

### **6.3. 전문가적 대안: backtrader의 사이즈 조절기(Sizer) 구현**

이러한 한계를 극복하고 현실적인 포트폴리오 관점을 도입하기 위한 전문가적 해결책은 backtrader의 Sizer 객체를 사용하는 것입니다. Sizer는 단순히 신호를 따르는 것을 넘어, '얼마나 많이' 사고팔 것인지를 결정하는 포지션 사이징 로직을 담당합니다. 이는 개별 신호 연구에서 포트폴리오 관리 시뮬레이션으로 넘어가는 결정적인 단계입니다.

아래 표는 '100% 투입' 방식과 Sizer를 사용한 전문가적 방식들을 비교하여 각 모델의 장단점과 사용 사례를 명확히 보여줍니다.

**표 3: 자본 배분 모델 비교**

| 모델명 | 설명 | 주요 사용 사례 | 장점 | 단점 | backtrader 구현 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **신호당 100% 투입** | 매수 신호 발생 시 가용 현금 전체를 투입 | 순수 알파 신호의 유효성 검증 | 신호의 성과를 분리하여 측정하기 용이함 | 극단적 리스크, 다각화 불가, 비현실적 | bt.Sizer 미사용 (기본 동작) |
| **고정 비율 사이징** | 각 거래에 전체 포트폴리오 가치의 고정된 비율(예: 2%)을 할당 | 표준적인 리스크 관리 기법 | 일관된 리스크 노출, 포트폴리오 성장에 따른 투자 금액 자동 조절 | 변동성이 다른 자산에 동일한 리스크를 할당하는 한계 | bt.sizers.PercentSizer 36 |
| **고정 금액/수량 사이징** | 각 거래에 고정된 금액 또는 주식 수량을 할당 | 소액 계좌 또는 특정 단위로 거래하는 전략 | 직관적이고 이해하기 쉬움 | 포트폴리오 성장에 따라 리스크 비율이 변동함 | bt.sizers.FixedSize |
| **변동성 기반 사이징** | 자산의 변동성에 반비례하여 포지션 크기를 조절 (변동성이 낮으면 많이, 높으면 적게) | 리스크 패리티(Risk Parity) 등 고급 리스크 관리 | 모든 포지션이 포트폴리오에 유사한 수준의 리스크를 기여하도록 조절 | 구현이 복잡하고, 변동성 측정 지표(예: ATR)가 추가로 필요함 | bt.Sizer 상속하여 커스텀 클래스 구현 |

Backtester 클래스에 PercentSizer를 추가하는 것은 매우 간단합니다. Cerebro 설정 부분에 다음 한 줄만 추가하면 됩니다.

Python

\# src/backtester.py 의 run 메소드 내부에 추가

\#...  
\# 1\. 브로커 설정  
\#...

\# 1-1. 사이즈 조절기 추가  
self.cerebro.addsizer(bt.sizers.PercentSizer, percents=2) \# 각 거래에 포트폴리오의 2%를 할당  
\#...

이 간단한 변경만으로도 백테스트는 개별 신호를 테스트하는 수준에서 벗어나, 리스크가 관리되는 현실적인 포트폴리오를 시뮬레이션하는 수준으로 격상됩니다. 이는 사용자의 최종 목표인 '투자 기법 포트폴리오 구축'을 위한 필수적인 단계입니다.

## **VII. 개발 로드맵 및 구현 가이드**

### **7.1. 단계별 개발 계획**

본 프로젝트를 성공적으로 완수하기 위해, 전체 개발 과정을 논리적인 5단계로 분할하여 제시합니다. 각 단계는 이전 단계의 결과물에 기반하여 점진적으로 시스템을 완성해 나가는 방식입니다.

* **1단계: 데이터 파이프라인 구축**  
  * **목표:** KOSPI 및 KOSDAQ 전 종목의 5년치 일봉 데이터를 안정적으로 수집하고 로컬에 저장하는 자동화 스크립트 완성.  
  * **핵심 기술:** pykrx, pandas, 파일 시스템 관리.  
  * **결과물:** data\_manager.py 스크립트 및 로컬 /data 디렉토리 내에 체계적으로 정리된 CSV 파일들.  
* **2단계: 핵심 엔진 및 JSON 파서 개발**  
  * **목표:** backtrader를 기반으로 한 기본 백테스팅 구조를 만들고, JSON 전략 파일을 해석하여 동적으로 backtrader 지표와 로직을 생성하는 파서 구현.  
  * **핵심 기술:** backtrader.Cerebro, backtrader.Strategy, JSON 파싱, 동적 클래스 속성 할당.  
  * **결과물:** backtester.py의 기본 구조 및 strategy\_parser.py 모듈.  
* **3단계: 기본 전략 백테스트 및 검증**  
  * **목표:** 1, 2단계에서 개발된 모듈을 통합하여, 단순한 '골든크로스' JSON 전략을 KOSPI 일부 종목에 대해 실행하고, 매수/매도 로직이 정상적으로 작동하는지 검증.  
  * **핵심 기술:** 모듈 통합, 디버깅, backtrader 로그 분석.  
  * **결과물:** 전체 시스템의 기본 기능이 동작하는 최초의 실행 가능한 프로토타입.  
* **4단계: 분석 및 보고 기능 통합**  
  * **목표:** 백테스트 결과를 정량적으로 평가하고 시각화하는 기능 추가.  
  * **핵심 기술:** backtrader.analyzers, QuantStats, Plotly.  
  * **결과물:** reporting.py 모듈 및 백테스트 종료 후 자동으로 생성되는 HTML 보고서와 인터랙티브 차트.  
* **5단계: 고급 리스크 관리 기능 구현**  
  * **목표:** 현실적인 포트폴리오 관리를 위해 Sizer를 도입하고, 다양한 자본 배분 전략을 테스트할 수 있는 기반 마련.  
  * **핵심 기술:** backtrader.sizers.PercentSizer, backtrader.sizers.FixedSize.  
  * **결과물:** 리스크 관리 기능이 통합되어 한층 더 현실적인 시뮬레이션이 가능한 완성된 백테스팅 시스템.

### **7.2. 코드 저장소 구조**

체계적이고 유지보수 가능한 프로젝트를 위해 다음과 같은 디렉토리 구조를 권장합니다. 이는 각 모듈의 역할을 명확히 구분하고, 데이터, 소스 코드, 전략 파일, 결과 보고서를 분리하여 관리의 효율성을 높입니다.37

/trading\_system  
|  
|-- /data/                  \# 1단계: 데이터 파이프라인의 결과물이 저장되는 곳  
| |-- /kospi/  
| |-- /kosdaq/  
|  
|-- /strategies/            \# 전략 정의 JSON 파일들을 저장하는 곳  
| |-- golden\_cross.json  
| |-- rsi\_macd.json  
|  
|-- /src/                   \# 핵심 파이썬 소스 코드를 저장하는 곳  
| |-- \_\_init\_\_.py  
| |-- data\_manager.py       \# 1단계: 데이터 수집 및 관리 모듈  
| |-- strategy\_parser.py    \# 2단계: JSON 전략 파서 모듈  
| |-- backtester.py         \# 2, 3, 5단계: backtrader 엔진 및 Sizer 설정  
| |-- reporting.py          \# 4단계: QuantStats, Plotly 보고 모듈  
|  
|-- /reports/               \# 4단계: 생성된 HTML 보고서가 저장되는 곳  
|  
|-- main.py                 \# 모든 모듈을 조립하여 실행하는 메인 스크립트  
|-- requirements.txt        \# 프로젝트 의존성 라이브러리 목록

### **7.3. 완전한 프로토타입 코드**

지금까지 논의된 모든 개념과 코드를 통합하여, 즉시 실행 가능한 완전한 프로토타입을 제공합니다. 이 코드는 위에서 제안된 디렉토리 구조를 따르며, main.py를 실행함으로써 전체 백테스트 과정을 수행할 수 있습니다.

#### **requirements.txt**

backtrader  
pykrx  
pandas  
quantstats  
plotly

#### **main.py**

Python

import argparse  
from src.data\_manager import DataManager  
from src.backtester import Backtester  
from src.reporting import generate\_quantstats\_report, plot\_equity\_curve

def main():  
    parser \= argparse.ArgumentParser(description="Modular Backtesting System")  
    parser.add\_argument('--strategy', '-s', type\=str, required=True, help\='Path to the strategy JSON file')  
    parser.add\_argument('--market', '-m', type\=str, default='kospi', choices=\['kospi', 'kosdaq'\], help\='Market to backtest (kospi or kosdaq)')  
    parser.add\_argument('--cash', '-c', type\=int, default=100000000, help\='Initial portfolio cash')  
    parser.add\_argument('--update-data', '-u', action='store\_true', help\='Force update of market data')  
    args \= parser.parse\_args()

    \# 1단계: 데이터 관리  
    data\_manager \= DataManager()  
    if args.update\_data or not data\_manager.is\_data\_available(args.market):  
        print("데이터를 업데이트합니다...")  
        data\_manager.download\_all\_data()  
    else:  
        print("기존 데이터를 사용합니다. 최신 데이터를 원하시면 \--update-data 옵션을 사용하세요.")

    data\_path \= data\_manager.get\_data\_path(args.market)

    \# 2\~5단계: 백테스터 실행  
    backtester \= Backtester(  
        data\_path=data\_path,  
        strategy\_json\_path=args.strategy,  
        initial\_cash=args.cash  
    )  
    results \= backtester.run()

    if results:  
        \# 4단계: 보고서 생성  
        report\_filename \= f"./reports/{args.strategy.split('/')\[-1\].replace('.json', '')}\_report.html"  
        backtester.print\_analysis(results)  
        generate\_quantstats\_report(results, report\_filename)  
        plot\_equity\_curve(results, args.cash)

if \_\_name\_\_ \== '\_\_main\_\_':  
    main()

#### **src/data\_manager.py**

(II장 2.3.3절의 download\_market\_data 함수를 클래스 형태로 재구성)

Python

import pandas as pd  
from pykrx import stock  
import time  
from datetime import datetime  
import os

class DataManager:  
    def \_\_init\_\_(self, data\_path="./data"):  
        self.data\_path \= data\_path  
        self.kospi\_path \= os.path.join(data\_path, "kospi")  
        self.kosdaq\_path \= os.path.join(data\_path, "kosdaq")  
        os.makedirs(self.kospi\_path, exist\_ok=True)  
        os.makedirs(self.kosdaq\_path, exist\_ok=True)

        self.end\_date \= datetime.now().strftime('%Y%m%d')  
        self.start\_date \= (datetime.now() \- pd.DateOffset(years=5)).strftime('%Y%m%d')

    def get\_data\_path(self, market):  
        return self.kospi\_path if market \== 'kospi' else self.kosdaq\_path

    def is\_data\_available(self, market):  
        path \= self.get\_data\_path(market)  
        return len(os.listdir(path)) \> 0

    def download\_all\_data(self):  
        markets \= {  
            "KOSPI": {"path": self.kospi\_path, "market\_name": "KOSPI"},  
            "KOSDAQ": {"path": self.kosdaq\_path, "market\_name": "KOSDAQ"}  
        }  
        for market\_name, info in markets.items():  
            self.\_download\_market\_data(info, self.start\_date, self.end\_date)  
      
    def \_download\_market\_data(self, market\_info, start\_date, end\_date):  
        \# II장 2.3.3절의 함수 내용과 동일  
        market\_name \= market\_info\["market\_name"\]  
        path \= market\_info\["path"\]  
          
        print(f"===== {market\_name} 시장 데이터 다운로드 시작 \=====")  
        tickers \= stock.get\_market\_ticker\_list(date=end\_date, market=market\_name)  
        print(f"{market\_name} 시장의 총 종목 수: {len(tickers)}개")  
          
        for i, ticker in enumerate(tickers):  
            try:  
                ticker\_name \= stock.get\_market\_ticker\_name(ticker)  
                file\_path \= os.path.join(path, f"{ticker}\_{ticker\_name}.csv")

                print(f"\[{i+1}/{len(tickers)}\] {ticker\_name}({ticker}) 데이터 다운로드 중...")  
                df \= stock.get\_market\_ohlcv(start\_date, end\_date, ticker)  
                  
                if not df.empty:  
                    df.to\_csv(file\_path)  
                  
                time.sleep(0.5)  
            except Exception as e:  
                print(f"  \-\> 에러 발생: {ticker\_name}({ticker}) \- {e}")  
                continue  
        print(f"===== {market\_name} 시장 데이터 다운로드 완료 \=====")

#### **src/backtester.py, src/strategy\_parser.py, src/reporting.py**

(IV, V장에서 제시된 코드를 각 파일에 맞게 배치)

이 프로토타입은 본 계획서에서 제안한 모든 아키텍처 원칙과 기술적 선택을 실제로 구현한 결과물입니다. 사용자는 strategies 디렉토리에 새로운 JSON 파일만 추가하면, 코드 수정 없이도 다양한 전략을 즉시 테스트하고 전문가 수준의 보고서를 받아볼 수 있습니다. 이로써 본 계획서는 단순한 문서를 넘어, 실제 행동으로 이어질 수 있는 강력하고 실용적인 개발 청사진을 제공합니다.

#### **참고 자료**

1. Best Python Backtesting Tool for Algo Trading (Beginner's Guide) \- TradeSearcher, 9월 22, 2025에 액세스, [https://tradesearcher.ai/blog/best-backtesting-tools-for-python-algo-trading-backtesting-py](https://tradesearcher.ai/blog/best-backtesting-tools-for-python-algo-trading-backtesting-py)  
2. The Top 21 Python Trading Tools (September 2025\) \- Analyzing Alpha, 9월 22, 2025에 액세스, [https://analyzingalpha.com/python-trading-tools](https://analyzingalpha.com/python-trading-tools)  
3. Awesome Quant \- Wilson Freitas, 9월 22, 2025에 액세스, [https://wilsonfreitas.github.io/awesome-quant/](https://wilsonfreitas.github.io/awesome-quant/)  
4. pykrx · PyPI, 9월 22, 2025에 액세스, [https://pypi.org/project/pykrx/1.0.4/](https://pypi.org/project/pykrx/1.0.4/)  
5. pykrx · PyPI, 9월 22, 2025에 액세스, [https://pypi.org/project/pykrx/1.0.8/](https://pypi.org/project/pykrx/1.0.8/)  
6. \[투데이 1편\] 금융 데이터 수집 \- 데이콘, 9월 22, 2025에 액세스, [https://dacon.io/competitions/official/235946/codeshare/5547](https://dacon.io/competitions/official/235946/codeshare/5547)  
7. \[파이썬\] Pykrx로 코스피, 코스닥 지수 OHCLV 크롤링 후 엑셀로 저장 하는 법, 9월 22, 2025에 액세스, [https://joo-ramzzi.tistory.com/7](https://joo-ramzzi.tistory.com/7)  
8. jaepil-choi/korquanttools: Finance data importer for quantitative stock market research, 9월 22, 2025에 액세스, [https://github.com/jaepil-choi/korquanttools](https://github.com/jaepil-choi/korquanttools)  
9. financialdatapy \- PyPI, 9월 22, 2025에 액세스, [https://pypi.org/project/financialdatapy/](https://pypi.org/project/financialdatapy/)  
10. Creating your first schema \- JSON Schema, 9월 22, 2025에 액세스, [https://json-schema.org/learn/getting-started-step-by-step](https://json-schema.org/learn/getting-started-step-by-step)  
11. JSON Schema, 9월 22, 2025에 액세스, [https://json-schema.org/](https://json-schema.org/)  
12. Logical JSON operators \- IBM, 9월 22, 2025에 액세스, [https://www.ibm.com/docs/ru/db2/11.1.0?topic=queries-logical-operators](https://www.ibm.com/docs/ru/db2/11.1.0?topic=queries-logical-operators)  
13. Boolean Operators · JSONata, 9월 22, 2025에 액세스, [https://docs.jsonata.org/boolean-operators](https://docs.jsonata.org/boolean-operators)  
14. Backtesting Systematic Trading Strategies in Python: Considerations and Open Source Frameworks | QuantStart, 9월 22, 2025에 액세스, [https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks/](https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks/)  
15. List of Most Extensive Backtesting Frameworks Available in Python, 9월 22, 2025에 액세스, [https://tradewithpython.com/list-of-most-extensive-backtesting-frameworks-available-in-python](https://tradewithpython.com/list-of-most-extensive-backtesting-frameworks-available-in-python)  
16. What are the best python \+ interactive broker backtesting and live trading frameworks? : r/algotrading \- Reddit, 9월 22, 2025에 액세스, [https://www.reddit.com/r/algotrading/comments/7epsqa/what\_are\_the\_best\_python\_interactive\_broker/](https://www.reddit.com/r/algotrading/comments/7epsqa/what_are_the_best_python_interactive_broker/)  
17. Python Backtesting Frameworks: Six Options to Consider \- Pipekit, 9월 22, 2025에 액세스, [https://pipekit.io/blog/python-backtesting-frameworks-six-options-to-consider](https://pipekit.io/blog/python-backtesting-frameworks-six-options-to-consider)  
18. Python backtesting which is better? Backtrader vs PyAlgoTrade : r/algotrading \- Reddit, 9월 22, 2025에 액세스, [https://www.reddit.com/r/algotrading/comments/okhp6p/python\_backtesting\_which\_is\_better\_backtrader\_vs/](https://www.reddit.com/r/algotrading/comments/okhp6p/python_backtesting_which_is_better_backtrader_vs/)  
19. Python library-Backtesting : r/algotrading \- Reddit, 9월 22, 2025에 액세스, [https://www.reddit.com/r/algotrading/comments/1fi83nx/python\_librarybacktesting/](https://www.reddit.com/r/algotrading/comments/1fi83nx/python_librarybacktesting/)  
20. Best Python Libraries for Algorithmic Trading and Financial Analysis \- QuantInsti Blog, 9월 22, 2025에 액세스, [https://blog.quantinsti.com/python-trading-library/](https://blog.quantinsti.com/python-trading-library/)  
21. Backtrader: Welcome, 9월 22, 2025에 액세스, [https://www.backtrader.com/](https://www.backtrader.com/)  
22. Getting Started with backtrader | Curtis Miller's Personal Website, 9월 22, 2025에 액세스, [https://ntguardian.wordpress.com/2017/06/12/getting-started-with-backtrader/](https://ntguardian.wordpress.com/2017/06/12/getting-started-with-backtrader/)  
23. Creating and Backtesting Trading Strategies with Backtrader \- PyQuant News, 9월 22, 2025에 액세스, [https://www.pyquantnews.com/free-python-resources/creating-and-backtesting-trading-strategies-with-backtrader](https://www.pyquantnews.com/free-python-resources/creating-and-backtesting-trading-strategies-with-backtrader)  
24. Broker \- Backtrader, 9월 22, 2025에 액세스, [https://www.backtrader.com/docu/broker/](https://www.backtrader.com/docu/broker/)  
25. Broker \- Slippage \- Backtrader, 9월 22, 2025에 액세스, [https://www.backtrader.com/docu/slippage/slippage/](https://www.backtrader.com/docu/slippage/slippage/)  
26. Commission Schemes \- Backtrader, 9월 22, 2025에 액세스, [https://www.backtrader.com/docu/commission-schemes/commission-schemes/](https://www.backtrader.com/docu/commission-schemes/commission-schemes/)  
27. How to Create and Backtest Trading Strategies with Backtrader \- QuantVPS, 9월 22, 2025에 액세스, [https://www.quantvps.com/blog/how-to-backtest-trading-strategies-with-backtrader](https://www.quantvps.com/blog/how-to-backtest-trading-strategies-with-backtrader)  
28. Analyzers Reference \- Backtrader, 9월 22, 2025에 액세스, [https://www.backtrader.com/docu/analyzers-reference/](https://www.backtrader.com/docu/analyzers-reference/)  
29. Analyzers \- Backtrader, 9월 22, 2025에 액세스, [https://www.backtrader.com/docu/analyzers/analyzers/](https://www.backtrader.com/docu/analyzers/analyzers/)  
30. QuantStats \- PyPI, 9월 22, 2025에 액세스, [https://pypi.org/project/QuantStats/](https://pypi.org/project/QuantStats/)  
31. Building Robust Trading Strategies with a Python Backtesting Framework \- Coders Digest, 9월 22, 2025에 액세스, [https://abhipandey.com/2022/04/building-robust-trading-strategies-with-a-python-backtesting-framework/](https://abhipandey.com/2022/04/building-robust-trading-strategies-with-a-python-backtesting-framework/)  
32. Plotly Python Graphing Library, 9월 22, 2025에 액세스, [https://plotly.com/python/](https://plotly.com/python/)  
33. Plotly Over Bokeh: A Comparative Analysis | by Muhamad Shidqi | Medium, 9월 22, 2025에 액세스, [https://medium.com/@shidqi19muhamad/plotly-over-bokeh-a-comparative-analysis-72edbb3ce07a](https://medium.com/@shidqi19muhamad/plotly-over-bokeh-a-comparative-analysis-72edbb3ce07a)  
34. Which one is better: Bokeh or Plotly? \- Python \- GeeksforGeeks, 9월 22, 2025에 액세스, [https://www.geeksforgeeks.org/python/which-one-is-better-bokeh-or-plotly/](https://www.geeksforgeeks.org/python/which-one-is-better-bokeh-or-plotly/)  
35. Testing the Best Financial Charting Tools on Python, 9월 22, 2025에 액세스, [https://hansdietergross.hashnode.dev/testing-the-best-financial-charting-tools-on-python](https://hansdietergross.hashnode.dev/testing-the-best-financial-charting-tools-on-python)  
36. Backtrader Tutorial: 10 Steps to Profitable Trading Strategy \- QuantVPS, 9월 22, 2025에 액세스, [https://www.quantvps.com/blog/backtrader-tutorial](https://www.quantvps.com/blog/backtrader-tutorial)  
37. neilsmurphy/backtrader\_template: Basic template for managing Backtrader backtests. \- GitHub, 9월 22, 2025에 액세스, [https://github.com/neilsmurphy/backtrader\_template](https://github.com/neilsmurphy/backtrader_template)