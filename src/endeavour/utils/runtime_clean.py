"""
runtime_clean.py
- 런타임에서만 데이터 정리 적용 (캐시 불변)
- 사용법:
    from endeavour.utils.runtime_clean import runtime_clean
    df = runtime_clean(df, ticker)
"""
from __future__ import annotations
from typing import Optional
import pandas as pd
from .data_quality import clean_missing_values

def runtime_clean(df: pd.DataFrame, ticker: Optional[str] = "UNKNOWN") -> pd.DataFrame:
    cleaned, report = clean_missing_values(df, ticker or "UNKNOWN")
    return cleaned
