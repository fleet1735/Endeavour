# encoding: utf-8
# SSOT v8.2 LOCK: Excel Export (Params 5+1, MDD positive, precision)
import json, pandas as pd

def _normalize(df, price_cols=None, money_cols=None):
    df = (df or pd.DataFrame()).copy().fillna(0)
    if price_cols:
        for c in price_cols:
            if c in df.columns: df[c]=df[c].astype(float).round(6)
    if money_cols:
        for c in money_cols:
            if c in df.columns: df[c]=df[c].astype(float).round(2)
    sort_cols=[c for c in ["symbol","date","datetime"] if c in df.columns]
    return df.sort_values(by=sort_cols) if sort_cols else df

def export_to_excel(summary_df, equity_df, trades_df, params_dict, cv_stamp, hashes, path="report.xlsx"):
    params = dict(params_dict or {})
    params["cv_stamp"]      = json.dumps(cv_stamp, ensure_ascii=False)
    params["data_hash"]     = (hashes or {}).get("data_hash","")
    params["code_hash"]     = (hashes or {}).get("code_hash","")
    params["param_hash"]    = (hashes or {}).get("param_hash","")
    params["universe_hash"] = (hashes or {}).get("universe_hash","")
    if "seed" in (hashes or {}):
        params["seed"] = (hashes or {}).get("seed")

    s = _normalize(summary_df, money_cols=["EquityFinal"])
    e = _normalize(equity_df,  money_cols=list((equity_df or pd.DataFrame()).columns))
    t = _normalize(trades_df,  money_cols=["price","fee","slippage"])
    p = pd.DataFrame([params])

    with pd.ExcelWriter(path) as xw:
        s.to_excel(xw,"Summary",index=False)
        e.to_excel(xw,"EquityCurve")
        t.to_excel(xw,"Trades",index=False)
        p.to_excel(xw,"Params",index=False)
