import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional
import pandas as pd
# ?? ?? ?????
try:
    import yfinance as yf
except Exception:
    yf = None  # yfinance ???/?? ? None ??
try:
    from pykrx import stock
except Exception:
    stock = None  # pykrx ???/?? ? None ??
# -----------------------------
# ?? ??
# -----------------------------
VERSION = "data_handler FINAL FULL | 2025-09-27 (data path + schema hardening)"
# ???? (04_data ? data)
CACHE_DIR = Path("data/cache")
LOG_DIR   = Path("data/logs")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
# ??: ?? + ??
_log_fmt = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    filename=LOG_DIR / "data_handler.log",
    level=logging.INFO,
    format=_log_fmt,
    encoding="utf-8"
)
_console = logging.StreamHandler(sys.stdout)
_console.setLevel(logging.INFO)
_console.setFormatter(logging.Formatter(_log_fmt))
logging.getLogger().addHandler(_console)
REQUIRED_COLS = ["Date", "Open", "High", "Low", "Close", "Volume"]
# -----------------------------
# ??
# -----------------------------
def _today(fmt: str = "%Y-%m-%d") -> str:
    return datetime.now().strftime(fmt)
def _date_str(dt: datetime, fmt: str = "%Y-%m-%d") -> str:
    return dt.strftime(fmt)
def _krx_fmt(date_str: str) -> str:
    # 'YYYY-MM-DD' ? 'YYYYMMDD'
    return date_str.replace("-", "")
def _ticker_to_krx(ticker: str) -> str:
    # '005930.KS' ? '005930'
    # '000660'    ? '000660'
    return ticker.split(".")[0]
def _cache_path(ticker: str, start: str, end: str) -> Path:
    return CACHE_DIR / f"{ticker}_{start}_{end}.csv"
def _ensure_date_col(df: pd.DataFrame) -> pd.DataFrame:
    # Date ??? ??, ???? ????? ???? ??
    if "Date" not in df.columns:
        if isinstance(df.index, (pd.DatetimeIndex, pd.core.indexes.numeric.Int64Index, pd.RangeIndex)):
            df = df.reset_index()
            # reset_index ? 'index'? ?? ????? Date ??? ?? ??? ??
            # ???: datetime dtype ? ??? Date? ??
            dt_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
            if dt_cols:
                src = dt_cols[0]
                if src != "Date":
                    df = df.rename(columns={src: "Date"})
            elif "Date" in df.columns:
                pass
            else:
                # ??? ??: ? ??? Date? ??(????? ?? ????? ??)
                first = df.columns[0]
                if first != "Date":
                    df = df.rename(columns={first: "Date"})
        else:
            # ?? ? ?? Date ??? ??(?? ???)
            df["Date"] = pd.NaT
    # Date dtype ??
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df
def _standardize_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    # ??: ? ??? REQUIRED_COLS ? ????? ?? ??
    cols = [str(c).strip() for c in df.columns]
    df.columns = cols
    # yfinance ??: Open,High,Low,Close,Adj Close,Volume
    # pykrx ??: (reset_index ?) Date, (??,??,??,??,???) ? ??? ?? ?? ?? ?? ?? ??? ??
    lower = {c.lower(): c for c in cols}
    mapping = {}
    if "open" in lower and "high" in lower and "low" in lower and "close" in lower and ("volume" in lower or "vol" in lower):
        mapping[lower["open"]] = "Open"
        mapping[lower["high"]] = "High"
        mapping[lower["low"]]  = "Low"
        mapping[lower["close"]] = "Close"
        if "volume" in lower:
            mapping[lower["volume"]] = "Volume"
        else:
            mapping[lower["vol"]] = "Volume"
    else:
        # ?? ??(?: pykrx ?? 5?: ??,??,??,??,???)
        # Date ??? ?? _ensure_date_col ?? ??
        # ??? ?? ?? ??? ????? OHLCV? ???
        non_date_cols = [c for c in cols if c != "Date"]
        if len(non_date_cols) >= 5:
            # ? 5?? OHLCV? ??
            mapping[non_date_cols[0]] = "Open"
            mapping[non_date_cols[1]] = "High"
            mapping[non_date_cols[2]] = "Low"
            mapping[non_date_cols[3]] = "Close"
            mapping[non_date_cols[4]] = "Volume"
    # Date ?? ??
    if "Date" not in cols:
        # _ensure_date_col ? ?? ????? ????? ??
        # ??? ??? ??? NaT
        df["Date"] = pd.NaT
    # ?? ??
    if mapping:
        df = df.rename(columns=mapping)
    # ??? ??? ??
    keep = ["Date", "Open", "High", "Low", "Close", "Volume"]
    # ?? ?? ? ??(? ?? ??)
    for k in keep:
        if k not in df.columns:
            df[k] = pd.NA
    df = df[keep]
    # ?? ??
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # ??/?? ??
    df = df.drop_duplicates(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df
def _missing_business_days(df: pd.DataFrame, start: str, end: str) -> Tuple[int, list]:
    # ?? ??(bdate_range)?? ??? ??(???? ??? ? ??)
    all_bdays = pd.bdate_range(start=start, end=end, inclusive="both")
    df_days = pd.to_datetime(df["Date"].dt.date)
    df_days = pd.DatetimeIndex(df_days.unique())
    missing = [d.date().isoformat() for d in all_bdays if d.normalize() not in df_days]
    return len(missing), (missing[:3] if missing else [])
# -----------------------------
# ??? ??
# -----------------------------
def _fetch_yfinance(ticker: str, start: str, end: str) -> pd.DataFrame:
    if yf is None:
        raise RuntimeError("yfinance is not available")
    # yfinance: end ? exclusive ?? ? ?? ?
    end_plus = (pd.to_datetime(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.download(ticker, start=start, end=end_plus, auto_adjust=False, progress=False, threads=False)
    if df is None or len(df) == 0:
        raise RuntimeError("yfinance returned empty dataframe")
    # ??? ? Date ??
    df = df.reset_index()
    # ???
    df = _ensure_date_col(df)
    df = _standardize_ohlcv(df)
    return df
def _fetch_pykrx(ticker: str, start: str, end: str) -> pd.DataFrame:
    if stock is None:
        raise RuntimeError("pykrx is not available")
    code = _ticker_to_krx(ticker)
    df = stock.get_market_ohlcv_by_date(_krx_fmt(start), _krx_fmt(end), code)
    if df is None or len(df) == 0:
        raise RuntimeError("pykrx returned empty dataframe")
    # ??? ? Date ??
    df = df.reset_index()
    # ???(??? ????? ?? ???? ???)
    df = _ensure_date_col(df)
    df = _standardize_ohlcv(df)
    return df
# -----------------------------
# ?? + ??
# -----------------------------
def load_price_data(ticker: str, start: str, end: str, source: str = "auto",
                    use_cache: bool = True, force_refresh: bool = False) -> Tuple[bool, Optional[pd.DataFrame], str]:
    path = _cache_path(ticker, start, end)
    try:
        if use_cache and not force_refresh and path.exists():
            df = pd.read_csv(path, encoding="utf-8")
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            ok, msg = _validate_df(df, start, end)
            if ok:
                logging.info(f"[cache] {ticker} rows={len(df)}")
                return True, df, "cache"
            else:
                logging.warning(f"Cache invalid ? refresh: {msg}")
    except Exception as e:
        logging.warning(f"Cache read failed ? refresh: {e}")
    # ?? ??
    last_err = None
    if source in ("auto", "yfinance"):
        try:
            logging.info(f"yfinance ??: {ticker} ({start}~{end})")
            df = _fetch_yfinance(ticker, start, end)
            _save_cache(df, path)
            return True, df, "yfinance"
        except Exception as e:
            last_err = e
            logging.error(f"yfinance ??: {e}")
    if source in ("auto", "pykrx"):
        try:
            logging.info(f"pykrx ?? ??: {ticker.split('.')[0]} ({start}~{end})")
            df = _fetch_pykrx(ticker, start, end)
            _save_cache(df, path)
            return True, df, "pykrx"
        except Exception as e:
            last_err = e
            logging.error(f"pykrx ??: {e}")
    return False, None, f"load failed: {last_err}"
def _save_cache(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    logging.info(f"?? ??: {path}")
# -----------------------------
# ??
# -----------------------------
def _validate_df(df: pd.DataFrame, start: str, end: str) -> Tuple[bool, str]:
    # ?? ??
    for c in REQUIRED_COLS:
        if c not in df.columns:
            return False, f"missing column: {c}"
    if df["Date"].isna().all():
        return False, "all Date are NaT"
    # ?? ? ???? 1? ????
    mask = (df["Date"] >= pd.to_datetime(start)) & (df["Date"] <= pd.to_datetime(end))
    dfx = df.loc[mask].copy()
    if dfx.empty:
        return False, "no rows in requested range"
    # ?? ? ?? ??
    dfx = dfx.drop_duplicates(subset=["Date"]).sort_values("Date")
    # ??? ??(?? ??) ??
    miss_n, miss_samples = _missing_business_days(dfx, start, end)
    if miss_n > 0:
        logging.warning(f"??? ?? {miss_n}?(??): ?:{miss_samples} ...")
    return True, "ok"
# -----------------------------
# ??
# -----------------------------
def main():
    logging.info(f"=== Data Handler ?? (?? {VERSION}) ===")
    # ?? ????
    end = _today("%Y-%m-%d")
    start_dt = pd.to_datetime(end) - pd.DateOffset(years=5) + pd.Timedelta(days= -1)
    start = _date_str(start_dt.to_pydatetime(), "%Y-%m-%d")
    tickers = ["005930.KS", "000660.KS", "035720.KS"]
    source = "auto"
    use_cache = True
    force_refresh = False
    ok_cnt = 0
    for t in tickers:
        ok, df, src = load_price_data(t, start, end, source=source, use_cache=use_cache, force_refresh=force_refresh)
        if ok:
            ok_cnt += 1
            logging.info(f"[{src:7}] {t} rows={len(df)}")
        else:
            logging.error(f"[fail   ] {t} : {df}")
    logging.info(f"??: {ok_cnt}/{len(tickers)} ??")
    print(f"??: {ok_cnt}/{len(tickers)} ??")
if __name__ == "__main__":
    main()
