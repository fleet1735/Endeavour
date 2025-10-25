# encoding: utf-8
# SSOT v8.2 LOCK: content-hash standard (sort & rounding) → SHA-256
import hashlib, pandas as pd
from io import StringIO

def _normalize_df(df: pd.DataFrame, price_cols=None, money_cols=None):
    if df is None: 
        return pd.DataFrame()
    x = df.copy().fillna(0)
    if price_cols:
        for c in price_cols:
            if c in x.columns: x[c] = x[c].astype(float).round(6)
    if money_cols:
        for c in money_cols:
            if c in x.columns: x[c] = x[c].astype(float).round(2)
    sort_cols = [c for c in ["symbol","date","datetime"] if c in x.columns]
    if sort_cols:
        x = x.sort_values(by=sort_cols)
    return x

def csv_sha256_from_df(df: pd.DataFrame, price_cols=None, money_cols=None):
    x = _normalize_df(df, price_cols=price_cols, money_cols=money_cols)
    csv = x.to_csv(index=False, encoding="utf-8")
    return hashlib.sha256(csv.encode("utf-8")).hexdigest()

def summary_hash_from_df(summary_df: pd.DataFrame):
    # Summary sheet spec: includes symbol/date and metric rounding (6)
    return csv_sha256_from_df(summary_df, price_cols=None, money_cols=["EquityFinal"])
