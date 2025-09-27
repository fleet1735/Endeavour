# -*- coding: utf-8 -*-
"""
스크립트: update_tickers.py
설명: pykrx 라이브러리를 사용하여 코스피 시가총액 상위 20개, 
     코스닥 시가총액 상위 10개 종목의 티커를 자동으로 가져와 
     config.json 파일을 생성하거나 업데이트합니다.
"""

import json
from pykrx import stock
from datetime import datetime, timedelta
import time

def get_most_recent_business_day():
    """가장 최근의 영업일을 YYYYMMDD 형식으로 반환합니다."""
    today = datetime.now()
    offset = 0
    # 주말이거나 장 시작 전일 경우를 대비해 하루 전부터 확인
    if today.weekday() >= 5: # 토요일(5) 또는 일요일(6)
        offset = today.weekday() - 4
    elif today.hour < 9: # 장 시작 전
        offset = 1

    while True:
        check_date = today - timedelta(days=offset)
        date_str = check_date.strftime("%Y%m%d")
        try:
            # 해당 날짜에 데이터가 있는지 KOSPI 지수로 확인
            df_test = stock.get_index_ohlcv(date_str, date_str, "1001")
            if not df_test.empty:
                return date_str
        except Exception:
            pass # 데이터가 없으면 이전 날짜로 계속 시도
        
        offset += 1
        if offset > 10: # 최대 10일 전까지만 시도
            raise ConnectionError("최근 10일간의 시장 데이터를 찾을 수 없습니다.")
        time.sleep(0.1) # 짧은 딜레이

def get_top_market_cap_tickers(market, n, date_str):
    """지정된 시장에서 시가총액 상위 n개 종목의 티커를 반환합니다."""
    print(f"Fetching market data for {market} on {date_str}...")
    df = stock.get_market_cap_by_ticker(date_str, market=market)
    df_sorted = df.sort_values(by='시가총액', ascending=False)
    top_tickers = df_sorted.head(n).index.tolist()
    
    # yfinance에서 사용 가능하도록 접미사 추가
    suffix = ".KS" if market == "KOSPI" else ".KQ"
    return [f"{ticker}{suffix}" for ticker in top_tickers]

def main():
    """메인 실행 함수"""
    try:
        print("최신 시가총액 순위로 종목 리스트 업데이트를 시작합니다.")
        
        # 1. 가장 최신 영업일 조회
        latest_bday = get_most_recent_business_day()
        print(f"기준일: {latest_bday}")

        # 2. KOSPI, KOSDAQ 상위 종목 티커 가져오기
        kospi_tickers = get_top_market_cap_tickers("KOSPI", 20, latest_bday)
        kosdaq_tickers = get_top_market_cap_tickers("KOSDAQ", 10, latest_bday)

        # 3. 티커 리스트 통합 (중복 제거)
        all_tickers = list(dict.fromkeys(kospi_tickers + kosdaq_tickers))

        # 4. config.json 파일 생성
        config_data = {
            "start_date": "5_years_ago",
            "end_date": "today",
            "tickers": all_tickers
        }

        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)

        print("\n--- KOSPI Top 20 ---")
        print(kospi_tickers)
        print("\n--- KOSDAQ Top 10 ---")
        print(kosdaq_tickers)
        print(f"\n성공: 'config.json' 파일이 총 {len(all_tickers)}개 종목으로 업데이트되었습니다.")

    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("config.json 파일 업데이트에 실패했습니다.")

if __name__ == "__main__":
    main()
