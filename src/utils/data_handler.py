import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
import pandas as pd
try:
    import yfinance as yf
except Exception:
    yf = None
try:
    from pykrx import stock
except Exception:
    stock = None
VERSION = "data_handler FIXED | 2025-09-27 (yfinance multirow + Date fix)"
CACHE_DIR = Path("data/cache")
LOG_DIR   = Path("data/logs")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "data_handler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)
_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(_console)
REQUIRED_COLS = ["Date", "Open", "High", "Low", "Close", "Volume"]
def _cache_path(ticker: str, start: str, end: str) -> Path:
    return CACHE_DIR / f"{ticker}_{start}_{end}.csv"
def _ensure_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()
    if "Date" not in df.columns:
        if "index" in df.columns:
            df = df.rename(columns={"index": "Date"})
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df
def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    cols = [c.lower() for c in df.columns]
    if "open" in cols: mapping[df.columns[cols.index("open")]] = "Open"
    if "high" in cols: mapping[df.columns[cols.index("high")]] = "High"
    if "low" in cols:  mapping[df.columns[cols.index("low")]]  = "Low"
    if "close" in cols: mapping[df.columns[cols.index("close")]] = "Close"
    if "volume" in cols: mapping[df.columns[cols.index("volume")]] = "Volume"
    df = df.rename(columns=mapping)
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[REQUIRED_COLS]
    df = df.drop_duplicates(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df
def _fetch_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    if yf is None:
        raise RuntimeError("yfinance not available")
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df is None or len(df) == 0:
        raise RuntimeError("empty dataframe")
    df = _ensure_date(df)
    df = _standardize(df)
    if len(df) <= 5:
        raise RuntimeError(f"too few rows from yfinance: {len(df)}")
    return df
def _fetch_pykrx(ticker: str, start: str, end: str) -> pd.DataFrame:
    if stock is None:
        raise RuntimeError("pykrx not available")
    code = ticker.split(".")[0]
    df = stock.get_market_ohlcv_by_date(start.replace("-",""), end.replace("-",""), code)
    if df is None or len(df) == 0:
        raise RuntimeError("empty dataframe")
    df = _ensure_date(df)
    df = _standardize(df)
    return df
def load_price_data(ticker: str, start: str, end: str, source: str="auto") -> Tuple[bool, Optional[pd.DataFrame], str]:
    path = _cache_path(ticker, start, end)
    if path.exists():
        try:
            df = pd.read_csv(path, encoding="utf-8")
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            return True, df, "cache"
        except Exception as e:
            logging.warning(f"Cache read failed: {e}")
    last_err = None
    if source in ("auto","yfinance"):
        try:
            df = _fetch_yfinance(ticker, start, end)
            df.to_csv(path, index=False, encoding="utf-8")
            logging.info(f"[yfinance] {ticker} rows={len(df)}")
            return True, df, "yfinance"
        except Exception as e:
            last_err = e
            logging.error(f"yfinance error: {e}")
    if source in ("auto","pykrx"):
        try:
            df = _fetch_pykrx(ticker, start, end)
            df.to_csv(path, index=False, encoding="utf-8")
            logging.info(f"[pykrx] {ticker} rows={len(df)}")
            return True, df, "pykrx"
        except Exception as e:
            last_err = e
            logging.error(f"pykrx error: {e}")
    return False, None, str(last_err)
def main():
    logging.info(f"=== Data Handler ?? (?? {VERSION}) ===")
    end = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - pd.DateOffset(years=5)).strftime("%Y-%m-%d")
    tickers = ["005930.KS","000660.KS","035720.KS"]
    for t in tickers:
        ok, df, src = load_price_data(t,start,end)
        if ok:
            logging.info(f"[{src}] {t} success rows={len(df)}")
        else:
            logging.error(f"[fail] {t}")
if __name__ == "__main__":
    main()
