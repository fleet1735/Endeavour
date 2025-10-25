# encoding: utf-8
# SSOT v8.2 LOCK: metrics precision (float6), money (float2), NaN→0
import numpy as np
import pandas as pd

_EPS = 1e-12

def _to_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def _ann_factor(freq="D"):
    return {"D":252, "H":252*6.5, "M":12}.get(freq, 252)

def cagr(equity: pd.Series, freq="D"):
    s = equity.dropna()
    if len(s) < 2: return 0.0
    years = len(s)/_ann_factor(freq)
    ret = (s.iloc[-1]/max(s.iloc[0], _EPS)) ** (1/max(years, _EPS)) - 1
    return round(_to_float(ret), 6)

def mdd_positive(equity: pd.Series):
    s = equity.dropna()
    if s.empty: return 0.0
    roll_max = s.cummax()
    dd = (roll_max - s) / roll_max.replace(0, np.nan)
    val = dd.max()
    return round(_to_float(val if np.isfinite(val) else 0.0), 6)

def profit_factor(gross_profit: float, gross_loss: float):
    gp = _to_float(gross_profit); gl = abs(_to_float(gross_loss))
    if gl < _EPS: return round(0.0 if gp < _EPS else 999999.0, 6)
    return round(gp / gl, 6)

def win_rate(wins: int, trades: int):
    t = max(int(trades), 0)
    if t <= 0: return 0.0
    return round(_to_float(int(wins)/t), 6)

def trades_count(trades_df: pd.DataFrame):
    return int(len(trades_df) if trades_df is not None else 0)

def sharpe_annualized(returns: pd.Series, rf: float=0.0, freq="D"):
    r = returns.dropna().astype(float)
    if r.empty: return 0.0
    ex = r - rf/_ann_factor(freq)
    mu = ex.mean(); sd = ex.std(ddof=1)
    if sd < _EPS: return 0.0
    sh = (mu/sd) * np.sqrt(_ann_factor(freq))
    return round(_to_float(sh), 6)

def sortino_annualized(returns: pd.Series, rf: float=0.0, freq="D"):
    r = returns.dropna().astype(float)
    if r.empty: return 0.0
    ex = r - rf/_ann_factor(freq)
    downside = ex.copy()
    downside[downside>0] = 0
    dd = np.sqrt((downside**2).mean())
    if dd < _EPS: return 0.0
    so = (ex.mean()/dd) * np.sqrt(_ann_factor(freq))
    return round(_to_float(so), 6)

def calmar(equity: pd.Series, freq="D"):
    c = cagr(equity, freq=freq)
    m = mdd_positive(equity)
    if m <= _EPS: return 0.0
    return round(_to_float(c/m), 6)
