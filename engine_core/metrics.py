# -*- coding: utf-8 -*-
"""
metrics.py — Minimal metrics without external deps.
Rules (SSOT/DeepResearch):
- 비율·계수: 소수 6자리 반올림
- 금액: 소수 2자리
- NaN/불능: 0 출력 (error_codes에 E-METRIC-101 기록은 호출부 선택)
"""
from math import sqrt, isnan
from statistics import mean, stdev

def _r6(x: float) -> float:
    try:
        if x is None or (isinstance(x, float) and isnan(x)): return 0.0
        return round(float(x), 6)
    except Exception:
        return 0.0

def _m2(x: float) -> float:
    try:
        if x is None or (isinstance(x, float) and isnan(x)): return 0.0
        return round(float(x), 2)
    except Exception:
        return 0.0

def _safe_mean(xs):
    try:
        if not xs: return 0.0
        return mean(xs)
    except Exception:
        return 0.0

def _safe_stdev(xs):
    try:
        if len(xs) < 2: return 0.0
        return stdev(xs)
    except Exception:
        return 0.0

def compute_core_metrics(daily_returns: list[float], pnl_series: list[float], trades: list[float], periods_per_year: int = 252):
    """
    daily_returns: 일일 수익률 (e.g., 0.001 = 0.1%)
    pnl_series: 누적 PnL(통화단위)
    trades: 각 트레이드의 PnL (통화단위, 손익 혼재)
    """
    errs = []

    # CAGR (연율화): (1+R)^n - 1 근사(단순 평균 기반)
    avg_r = _safe_mean(daily_returns)
    cagr = (1 + avg_r) ** periods_per_year - 1 if avg_r != 0 else 0.0

    # Max Drawdown (MDD) — PnL equity 기준
    mdd = 0.0
    try:
        peak = float('-inf')
        dd = 0.0
        for x in pnl_series:
            if x > peak: peak = x
            dd = min(dd, (x - peak))
        # dd는 음수(낙폭), 비율 대신 절대금액을 비율화 없이 "비율 지표"로 간주: 0~1 scale이 필요하면 수정
        # 여기서는 손실 비율을 근사하려면 peak!=0일 때 abs(dd/peak)
        if peak != 0 and peak != float('-inf'):
            mdd = abs(dd/peak)
        else:
            mdd = 0.0
    except Exception:
        errs.append("E-METRIC-101")
        mdd = 0.0

    # Profit Factor (총익/총손)
    pf = 0.0
    try:
        gains = sum(x for x in trades if x > 0)
        losses = abs(sum(x for x in trades if x < 0))
        pf = (gains / losses) if losses > 0 else (0.0 if gains == 0 else float('inf'))
        if pf == float('inf'): pf = 0.0  # 무한대는 0으로 강등(표준화 출력)
    except Exception:
        errs.append("E-METRIC-101")
        pf = 0.0

    # Win Rate
    wr = 0.0
    try:
        n = len(trades)
        wins = len([x for x in trades if x > 0])
        wr = wins / n if n > 0 else 0.0
    except Exception:
        errs.append("E-METRIC-101")
        wr = 0.0

    # Sharpe (연율화, rf=0)
    sharpe = 0.0
    try:
        mu = _safe_mean(daily_returns)
        sd = _safe_stdev(daily_returns)
        if sd > 0:
            sharpe = (mu / sd) * sqrt(periods_per_year)
        else:
            sharpe = 0.0
    except Exception:
        errs.append("E-METRIC-101")
        sharpe = 0.0

    # Sortino (연율화, rf=0, 하방편차)
    sortino = 0.0
    try:
        neg = [x for x in daily_returns if x < 0]
        dn = _safe_stdev(neg)
        if dn > 0:
            sortino = (avg_r / dn) * sqrt(periods_per_year)
        else:
            sortino = 0.0
    except Exception:
        errs.append("E-METRIC-101")
        sortino = 0.0

    # Calmar (CAGR / MDD)
    calmar = (cagr / mdd) if mdd > 0 else 0.0

    # Trades (count), 금액 라운딩은 출력부에서 필요 시 적용
    out = {
        "CAGR": _r6(cagr),
        "MDD": _r6(mdd),
        "PF": _r6(pf),
        "WinRate": _r6(wr),
        "Trades": len(trades),
        "Sharpe": _r6(sharpe),
        "Sortino": _r6(sortino),
        "Calmar": _r6(calmar),
        "error_codes": errs
    }
    return out
