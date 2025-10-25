"""
Endeavour Engine Core — Parallel Backtest Skeleton (Sprint 3)
- Goal: vectorized, optionally parallel backtesting harness
- SSOT refs: CVStampV2, summary_hash, immutable ledger
- Safe import: vectorbt / dask are optional at runtime
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import json, hashlib, os, time, math, random

# Optional deps (graceful fallback)
try:
    import vectorbt as vbt  # type: ignore
except Exception:
    vbt = None

try:
    import dask
    from dask import delayed, compute  # type: ignore
except Exception:
    dask = None
    delayed = lambda f: f
    def compute(*args, **kwargs): return args

@dataclass(frozen=True)
class BacktestSpec:
    name: str
    params: Dict[str, Any]
    cv: Dict[str, Any]  # CVStampV2 literal dict
    seed: int = 42

def _summary_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _metric_pack(equity_curve: List[float]) -> Dict[str, float]:
    if not equity_curve:
        return {"CAGR":0.0,"MDD":0.0,"PF":0.0,"Sharpe":0.0}
    # Minimal placeholders; real formulas implemented in metrics.py
    return {"CAGR":0.0,"MDD":0.0,"PF":1.0,"Sharpe":0.0}

def _run_single_backtest(spec: BacktestSpec) -> Dict[str, Any]:
    random.seed(spec.seed)
    # Placeholder equity curve (replace with vectorbt pipeline)
    equity = [100.0]
    for _ in range(252):
        equity.append(equity[-1] * (1.0 + random.uniform(-0.01, 0.01)))
    metrics = _metric_pack(equity)
    result = {
        "name": spec.name,
        "params": spec.params,
        "cv": spec.cv,
        "seed": spec.seed,
        "metrics": metrics,
        "equity_len": len(equity),
    }
    result["summary_hash"] = _summary_hash({
        "name": spec.name,
        "params": spec.params,
        "cv": spec.cv,
        "seed": spec.seed,
        "metrics": metrics,
    })
    return result

def run_batch(specs: List[BacktestSpec], parallel: bool = False) -> List[Dict[str, Any]]:
    if parallel and dask is not None:
        tasks = [delayed(_run_single_backtest)(s) for s in specs]
        results, = compute(tasks)
        return list(results)
    else:
        return [_run_single_backtest(s) for s in specs]

def save_ledger(results: List[Dict[str, Any]], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    p = os.path.join(out_dir, f"ledger_{ts}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return p

if __name__ == "__main__":
    # Minimal demo payload (replace by real setups)
    demo_specs = [
        BacktestSpec(name="GC_Swing", params={"ma_fast":50,"ma_slow":200}, cv={"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}),
        BacktestSpec(name="RSI_MR", params={"rsi":14,"th_low":30,"th_high":70}, cv={"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}),
    ]
    out = run_batch(demo_specs, parallel=False)
    path = save_ledger(out, os.path.join(os.getcwd(), "ledgers"))
    print(f"[engine] batch complete → {path} (n={len(out)})")
