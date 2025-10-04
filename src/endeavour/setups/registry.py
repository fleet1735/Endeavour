# -*- coding: utf-8 -*-
\"""지표/룰 레지스트리 v1 (미니멀):
- indicators: SMA, EMA(단순), RSI(간이)
- rule eval helpers: cmp(lhs, op, rhs)
노트: 실제 구현은 pandas 기반으로 확장 예정.
\"""

from typing import List, Dict, Any
import math

def sma(series: List[float], n: int) -> List[float]:
    out = []
    s = 0.0
    for i, v in enumerate(series):
        s += v
        if i >= n: s -= series[i-n]
        out.append(s / min(i+1, n))
    return out

def ema(series: List[float], n: int) -> List[float]:
    out = []
    k = 2 / (n + 1.0)
    prev = None
    for v in series:
        prev = v if prev is None else (v - prev) * k + prev
        out.append(prev)
    return out

def rsi(series: List[float], n: int = 14) -> List[float]:
    gains, losses = [], []
    for i in range(1, len(series)):
        ch = series[i] - series[i-1]
        gains.append(max(ch, 0.0))
        losses.append(abs(min(ch, 0.0)))
    def roll_avg(x, n):
        out=[]; s=0.0
        for i,v in enumerate(x):
            s += v
            if i >= n: s -= x[i-n]
            out.append(s / min(i+1, n))
        return out
    ag = roll_avg(gains, n)
    al = roll_avg(losses, n)
    rs = [(ag[i] / al[i]) if al[i] != 0 else math.inf for i in range(len(al))]
    rsi = [100 - (100 / (1 + r)) for r in rs]
    return [None]*(len(series)-len(rsi)) + rsi

INDICATORS = {
    "SMA": lambda series, **p: sma(series, int(p.get("n", 10))),
    "EMA": lambda series, **p: ema(series, int(p.get("n", 10))),
    "RSI": lambda series, **p: rsi(series, int(p.get("n", 14))),
}

def cmp(lhs: float, op: str, rhs: float) -> bool:
    if op == ">":  return lhs > rhs
    if op == "<":  return lhs < rhs
    if op == ">=": return lhs >= rhs
    if op == "<=": return lhs <= rhs
    if op == "==": return lhs == rhs
    if op == "!=": return lhs != rhs
    raise ValueError(f"Unsupported op: {op}")
