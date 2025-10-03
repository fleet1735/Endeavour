"""
data_quality.py
- 비파괴(읽기 전용) 데이터 클린 유틸
- 기능: (1) 거래일 아님(OHLC 전부 NaN) 행 제거, (2) 인덱스 정렬·중복 제거, (3) 로그 기록
- 캐시 파일은 수정하지 않음 (리스크 0)
"""
from __future__ import annotations

import os
import logging
from typing import Tuple, Dict
import pandas as pd

LOG_PATH = os.path.join("data", "logs", "data_quality.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

_logger = logging.getLogger("data_quality")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    _fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    _fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    _fh.setFormatter(_fmt)
    _logger.addHandler(_fh)

def clean_missing_values(df: pd.DataFrame, ticker: str = "UNKNOWN") -> Tuple[pd.DataFrame, Dict]:
    """
    비파괴 클린: 캐시를 건드리지 않고 메모리 내에서만 정리.
    규칙:
      - 거래일 아님 = OHLC 모두 NaN 인 행 → 제거
      - 인덱스 정렬, 중복 인덱스 제거
    반환:
      - (정리된 df, 리포트 dict)
    """
    rep: Dict = {}
    before = len(df)

    # 인덱스 datetime 보장
    if not isinstance(df.index, pd.DatetimeIndex):
        if "Date" in df.columns:
            df = df.set_index(pd.to_datetime(df["Date"]))
            df = df.drop(columns=["Date"])
        else:
            df.index = pd.to_datetime(df.index, errors="coerce")

    # 거래일 아님(OHLC 전부 NaN) 마스크
    ohlc_cols = [c for c in ["Open", "High", "Low", "Close"] if c in df.columns]
    dropped_non_trading = 0
    if ohlc_cols:
        non_trading = df[ohlc_cols].isna().all(axis=1)
        dropped_non_trading = int(non_trading.sum())
        if dropped_non_trading:
            df = df.loc[~non_trading].copy()
    else:
        _logger.warning("No OHLC columns found for %s", ticker)

    # 인덱스 정렬 및 중복 제거
    sorted_flag = False
    if not df.index.is_monotonic_increasing:
        df = df.sort_index()
        sorted_flag = True

    dup_count = int(df.index.duplicated().sum())
    if dup_count:
        df = df[~df.index.duplicated(keep="last")]

    after = len(df)
    rep.update({
        "ticker": ticker,
        "rows_before": before,
        "rows_after": after,
        "dropped_non_trading_rows": dropped_non_trading,
        "dropped_duplicate_index": dup_count,
        "sorted_index": sorted_flag,
    })
    if after > 0:
        rep["first_date"] = df.index.min().strftime("%Y-%m-%d")
        rep["last_date"] = df.index.max().strftime("%Y-%m-%d")

    _logger.info(
        "CLEAN[%s]: before=%d after=%d drop_non_trading=%d dup_idx=%d sorted=%s",
        ticker, before, after, dropped_non_trading, dup_count, sorted_flag
    )
    return df, rep
