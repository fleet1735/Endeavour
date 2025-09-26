# 01_src/utils/data_handler.py

import os
import pandas as pd
import yfinance as yf

# 📂 절대 경로 기반
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UNIVERSE_CSV = os.path.join(BASE_DIR, "02_docs", "universe", "target_tickers.csv")
CACHE_DIR = os.path.join(BASE_DIR, "04_data", "cache")

os.makedirs(CACHE_DIR, exist_ok=True)


def load_universe() -> list:
    """CSV에서 티커 리스트 로드"""
    df = pd.read_csv(UNIVERSE_CSV)
    return df["Ticker"].dropna().tolist()


def fetch_ohlcv(ticker: str, start: str = None, end: str = None, use_cache: bool = True) -> pd.DataFrame:
    """Yahoo Finance에서 OHLCV 데이터 가져오기 (캐싱 지원, MultiIndex 제거)"""
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{start}_{end}.csv")

    # 캐시 우선 로드
    if use_cache and os.path.exists(cache_file):
        try:
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        except Exception:
            print(f"[WARN] 캐시 로드 실패. 새로 다운로드합니다: {cache_file}")

    # 새로 다운로드
    df = yf.download(ticker, start=start, end=end, progress=False)

    if df is None or df.empty:
        print(f"[WARN] {ticker}: 데이터 없음")
        return pd.DataFrame()

    # ✅ MultiIndex 제거
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ✅ 컬럼 표준화
    rename_map = {
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "Adj Close",
        "Volume": "Volume",
    }
    df = df.rename(columns=rename_map)

    # 캐시 저장
    df.to_csv(cache_file, encoding="utf-8-sig")
    return df


def save_to_cache(df: pd.DataFrame, ticker: str, start: str, end: str):
    """데이터를 캐시에 저장"""
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{start}_{end}.csv")
    df.to_csv(cache_file, encoding="utf-8-sig")


def load_cached_csv(ticker: str, start: str, end: str) -> pd.DataFrame:
    """캐시된 CSV 불러오기"""
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{start}_{end}.csv")
    if os.path.exists(cache_file):
        return pd.read_csv(cache_file, index_col=0, parse_dates=True)
    return pd.DataFrame()
