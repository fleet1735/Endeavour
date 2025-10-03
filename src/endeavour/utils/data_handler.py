# === data_handler.py (FINAL FULL FORCE REPLACE) ===
import os
import logging
from pathlib import Path
from datetime import date, timedelta
import yfinance as yf
from pykrx import stock
import pandas as pd
import holidays

# 버전 정보
VERSION = "data_handler FINAL FULL | 2025-09-27 (FORCE REPLACE, yfinance+pykrx fixed, T-1 business day)"

# 디렉토리 설정
CACHE_DIR = Path("data/cache")
LOG_DIR   = Path("data/logs")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    filename=LOG_DIR / "data_handler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

def get_last_business_day_from_yesterday():
    """어제를 기준으로, 어제가 휴일(주말 또는 공휴일)이면 직전 영업일 반환"""
    check_date = date.today() - timedelta(days=1)
    kr_holidays = holidays.KR(years=[check_date.year, check_date.year - 1])
    while True:
        is_weekend = check_date.isoweekday() in [6, 7]  # 토=6, 일=7
        is_holiday = check_date in kr_holidays
        if not is_weekend and not is_holiday:
            return check_date
        check_date -= timedelta(days=1)

def get_cache_path(ticker, start, end):
    return CACHE_DIR / f"{ticker}_{start}_{end}.csv"

def fetch_yfinance(ticker, start, end):
    try:
        df = yf.download(str(ticker), start=start, end=end, progress=False)
        if df.empty:
            raise ValueError("No data from yfinance")
        df.reset_index(inplace=True)
        df = df.rename(columns={
            "Date": "Date",
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Adj Close": "Close",
            "Volume": "Volume"
        })[["Date","Open","High","Low","Close","Volume"]]
        return df
    except Exception as e:
        logging.error(f"[yfinance error] {ticker}: {e}")
        return None

def fetch_pykrx(ticker, start, end):
    try:
        code = ticker.replace(".KS","").replace(".KQ","")
        df = stock.get_market_ohlcv_by_date(start.replace("-",""), end.replace("-",""), code)
        if df.empty:
            raise ValueError("No data from pykrx")
        df.reset_index(inplace=True)
        df = df.rename(columns={
            "날짜": "Date",
            "시가": "Open",
            "고가": "High",
            "저가": "Low",
            "종가": "Close",
            "거래량": "Volume"
        })[["Date","Open","High","Low","Close","Volume"]]
        return df
    except Exception as e:
        logging.error(f"[pykrx error] {ticker}: {e}")
        return None

def load_price_data(ticker, start, end):
    cache_file = get_cache_path(ticker, start, end)
    if cache_file.exists():
        logging.info(f"[CACHE] hit: {cache_file}")
        return pd.read_csv(cache_file, parse_dates=["Date"])

    # 1차: yfinance
    df = fetch_yfinance(ticker, start, end)
    if df is None:
        # 2차: pykrx
        df = fetch_pykrx(ticker, start, end)

    if df is not None:
        df.to_csv(cache_file, index=False, encoding="utf-8-sig")
        logging.info(f"[CACHE] saved: {cache_file}")
        return df
    else:
        logging.error(f"[FAIL] {ticker}")
        return None

def main():
    last_bday = get_last_business_day_from_yesterday()
    start = "2020-01-01"
    end   = last_bday.strftime("%Y-%m-%d")
    tickers = ["005930.KS", "000660.KS", "035720.KS"]

    logging.info(f"=== Data Handler 실행 (버전 {VERSION}) ===")
    logging.info(f"기간: {start} ~ {end}")
    print(f"[INFO] Data Handler 실행 (버전 {VERSION})")
    print(f"[INFO] 기간: {start} ~ {end}")

    for t in tickers:
        df = load_price_data(t, start, end)
        if df is not None:
            print(f"[OK] {t} rows={len(df)}")
        else:
            print(f"[FAIL] {t}")

if __name__ == "__main__":
    main()
