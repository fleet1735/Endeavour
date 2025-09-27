# src/utils/data_handler.py
# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Endeavour Project - Phase 1 Data Handler (FINAL FULL VERSION)
# ------------------------------------------------------------
# 실행: 프로젝트 루트에서
#   python -m src.utils.data_handler
#
# 특징:
#  - yfinance 기본 → 실패/결측 시 pykrx 폴백
#  - CSV 캐시: 04_data/cache/{ticker}_{start}_{end}.csv
#  - 검증 게이트 (스키마 / 영업일 커버리지 경고 / NaN 비율 / 연속 NaN)
#  - 로깅: 콘솔(INFO) + 파일(DEBUG, cp949 인코딩)
#  - ASCII-only (한글 리터럴 없음, 깨짐 방지)
# ------------------------------------------------------------

import os
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

import pandas as pd
import yfinance as yf

try:
    from pykrx import stock as krx_stock
except Exception:
    krx_stock = None

VERSION = "data_handler FINAL FULL | 2025-09-27"

# ============================================================
# 로깅 설정
# ============================================================
LOG_DIR = os.path.join("04_data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_logger = logging.getLogger("DataHandler")
_logger.setLevel(logging.DEBUG)

if not _logger.handlers:
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    # 콘솔
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    _logger.addHandler(ch)

    # 파일 (Windows 호환 cp949)
    fh = RotatingFileHandler(
        os.path.join(LOG_DIR, "data_handler.log"),
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="cp949",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    _logger.addHandler(fh)

log = _logger

# ============================================================
# 유틸 함수
# ============================================================
def _today() -> date:
    return datetime.now().date()

def _last_business_day(d: Optional[date] = None) -> date:
    d = d or _today()
    while d.weekday() >= 5:  # 토/일
        d -= timedelta(days=1)
    return d

def _fmt_ymd(d: date) -> str:
    return d.strftime("%Y%m%d")

def _parse_ymd(s: str) -> date:
    return datetime.strptime(s, "%Y%m%d").date()

def _ensure_dirs():
    os.makedirs(os.path.join("04_data", "cache"), exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

def _cache_path(ticker: str, start: str, end: str) -> str:
    return os.path.join("04_data", "cache", f"{ticker}_{start}_{end}.csv")

def _krx_code_from(ticker: str) -> Optional[str]:
    base = (ticker or "").split(".")[0]
    return base if len(base) == 6 and base.isdigit() else None

def _expected_bdays(start: str, end: str) -> pd.DatetimeIndex:
    return pd.date_range(start=start, end=end, freq="B")

def _run_length_max(series_bool: pd.Series) -> int:
    max_run = cur = 0
    for v in series_bool.astype(bool).tolist():
        if v:
            cur += 1
            if cur > max_run:
                max_run = cur
        else:
            cur = 0
    return max_run

# ============================================================
# 검증 로직
# ============================================================
def _validate_df(df: pd.DataFrame, start: str, end: str) -> Tuple[bool, str]:
    required = ["Date", "Open", "High", "Low", "Close", "Volume"]
    if not all(c in df.columns for c in required):
        return False, f"schema mismatch {df.columns.tolist()}"

    dfx = df.copy()
    dfx["Date"] = pd.to_datetime(dfx["Date"])
    dfx = dfx.drop_duplicates(subset=["Date"]).sort_values("Date")
    dfx.set_index("Date", inplace=True)

    # 영업일 커버리지 (경고)
    exp_bdays = _expected_bdays(start, end)
    missing = exp_bdays.difference(dfx.index.normalize())
    if len(missing) > 0:
        log.warning("영업일 누락 %d일 (경고) 예:%s ...",
                    len(missing), missing[:3].strftime("%Y-%m-%d").tolist())

    # NaN 비율
    nan_ratio = dfx[["Open", "High", "Low", "Close", "Volume"]].isna().mean().mean()
    if nan_ratio > 0.05:
        return False, f"nan>{nan_ratio:.2%}"

    # 연속 NaN
    any_nan = dfx[["Open", "High", "Low", "Close", "Volume"]].isna().any(axis=1)
    max_consec = _run_length_max(any_nan)
    if max_consec >= 5:
        return False, f"consec_nan={max_consec}"

    return True, "OK"

# ============================================================
# 수집 함수
# ============================================================
def _fetch_yf(ticker: str, start: str, end: str) -> pd.DataFrame:
    log.info("yfinance 수집: %s (%s~%s)", ticker, start, end)
    try:
        start_fmt = pd.to_datetime(start).strftime("%Y-%m-%d")
        end_exc = (pd.to_datetime(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        df = yf.download(
            ticker,
            start=start_fmt,
            end=end_exc,
            progress=False,
            auto_adjust=False,
        )

        if isinstance(df, tuple):
            df = df[0]

        if df is None or df.empty:
            log.warning("yfinance 빈 결과: %s", ticker)
            return pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"])

        df = df.reset_index()

        rename_map = {}
        for c in df.columns:
            if isinstance(c, str):
                lc = c.lower()
                if lc in {"date", "open", "high", "low", "close", "volume"}:
                    rename_map[c] = c.capitalize()
        df = df.rename(columns=rename_map)

        if "Date" not in df.columns:
            df = df.rename(columns={df.columns[0]: "Date"})

        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
        out = df[["Date","Open","High","Low","Close","Volume"]].copy()
        out = out[out["Date"] <= pd.to_datetime(end)]
        return out.reset_index(drop=True)
    except Exception as e:
        log.error("yfinance 예외: %s", e)
        return pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"])

def _fetch_krx(ticker: str, start: str, end: str) -> pd.DataFrame:
    if krx_stock is None:
        log.error("pykrx 불가: %s", ticker)
        return pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"])
    code = _krx_code_from(ticker)
    if not code:
        log.error("pykrx 코드 변환 실패: %s", ticker)
        return pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"])
    try:
        df = krx_stock.get_market_ohlcv_by_date(start, end, code)
        if df is None or df.empty:
            log.warning("pykrx 빈 결과: %s", code)
            return pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"])
        df = df.reset_index()

        cols = list(df.columns)
        rename = {}
        if len(cols) >= 1: rename[cols[0]] = "Date"
        if len(cols) >= 5:
            rename[cols[1]] = "Open"; rename[cols[2]] = "High"
            rename[cols[3]] = "Low";  rename[cols[4]] = "Close"
        if len(cols) >= 6: rename[cols[5]] = "Volume"

        df = df.rename(columns=rename, errors="ignore")

        for need in ["Date","Open","High","Low","Close","Volume"]:
            if need not in df.columns:
                df[need] = pd.NA

        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
        return df[["Date","Open","High","Low","Close","Volume"]].copy().reset_index(drop=True)
    except Exception as e:
        log.error("pykrx 예외: %s", e)
        return pd.DataFrame(columns=["Date","Open","High","Low","Close","Volume"])

# ============================================================
# API
# ============================================================
@dataclass
class LoadResult:
    ticker: str
    source: str
    df: pd.DataFrame
    message: str=""

def load_price_data(ticker: str, start: str, end: str, force_refresh: bool=False) -> LoadResult:
    _ensure_dirs()
    cache_fp = _cache_path(ticker, start, end)

    if not force_refresh and os.path.exists(cache_fp):
        try:
            df = pd.read_csv(cache_fp)
            ok, msg = _validate_df(df, start, end)
            if ok:
                log.info("캐시 적중: %s", cache_fp)
                return LoadResult(ticker,"cache",df,"cache hit")
            else:
                log.warning("캐시 검증 실패 → 재수집: %s | %s", cache_fp, msg)
        except Exception as e:
            log.warning("캐시 로드 예외: %s", e)

    df = _fetch_yf(ticker, start, end)
    ok, msg = _validate_df(df, start, end)
    if ok and not df.empty:
        df.to_csv(cache_fp,index=False,encoding="utf-8-sig")
        log.info("yfinance 성공 → 캐시 저장: %s", cache_fp)
        return LoadResult(ticker,"yfinance",df,"yf ok")

    df = _fetch_krx(ticker, start, end)
    ok, msg = _validate_df(df, start, end)
    if ok and not df.empty:
        df.to_csv(cache_fp,index=False,encoding="utf-8-sig")
        log.info("pykrx 성공 → 캐시 저장: %s", cache_fp)
        return LoadResult(ticker,"pykrx",df,"krx ok")

    log.error("데이터 로드 실패: %s", ticker)
    return LoadResult(ticker,"failed",pd.DataFrame(),"failed")

# ============================================================
# Main
# ============================================================
def main():
    log.info("=== Data Handler 실행 (버전 %s) ===", VERSION)

    end_d = _last_business_day()
    start_d = end_d - timedelta(days=365*5)
    start = _fmt_ymd(start_d)
    end = _fmt_ymd(end_d)

    tickers = ["005930.KS","000660.KS","035720.KS"]
    log.info("대상 티커: %s", ", ".join(tickers))
    log.info("기간: %s ~ %s", start, end)

    ok_cnt = 0
    for t in tickers:
        r = load_price_data(t,start,end)
        if r.source != "failed" and not r.df.empty:
            ok_cnt += 1
        log.info("[%s] %s rows=%d", r.source, t, len(r.df))

    log.info("완료: %d/%d 성공", ok_cnt, len(tickers))

if __name__ == "__main__":
    main()
