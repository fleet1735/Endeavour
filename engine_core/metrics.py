\"\"\"engine_core/metrics.py — precision rules & safe metrics
Rules:
- Ratios: round(..., 6)
- Amounts: round(..., 2)  # reserved
- NaN -> 0.0 and record code 'E-METRIC-101' upstream
\"\"\"
from __future__ import annotations
from typing import Dict, Any
import math

def r6(x: float) -> float:
    try:
        v=float(x)
        if math.isnan(v) or math.isinf(v): return 0.0
        return round(v, 6)
    except Exception:
        return 0.0

def basic_summary(pnl: float=0.0, trades: int=0) -> Dict[str, Any]:
    # Placeholder summary for smoke; real impl must receive arrays/series
    out = {
        "CAGR": r6(0.0),
        "MDD":  r6(0.0),
        "PF":   r6(1.0),
        "WinRate": r6(0.5),
        "Trades": int(trades),
        "Sharpe": r6(0.0),
        "Sortino": r6(0.0),
        "Calmar": r6(0.0),
    }
    return out
