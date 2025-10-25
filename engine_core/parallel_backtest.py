"""
Endeavour Engine Core — Parallel Backtest Skeleton (Sprint 3, audit path fixed)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
import json, hashlib, os, time, random

try:
    import vectorbt as vbt
except Exception:
    vbt = None

@dataclass(frozen=True)
class BacktestSpec:
    name: str
    params: Dict[str, Any]
    cv: Dict[str, Any]
    seed: int = 42

def _summary_hash(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _run_single(spec: BacktestSpec) -> Dict[str, Any]:
    random.seed(spec.seed)
    equity=[100.0]
    for _ in range(252): equity.append(equity[-1]*(1.0+random.uniform(-0.01,0.01)))
    result={"name":spec.name,"params":spec.params,"cv":spec.cv,"seed":spec.seed,"equity_len":len(equity)}
    result["summary_hash"]=_summary_hash(result)
    return result

def run_batch(specs: List[BacktestSpec]) -> List[Dict[str,Any]]:
    return [_run_single(s) for s in specs]

def save_ledger(results: List[Dict[str,Any]], out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts=time.strftime("%Y%m%d_%H%M%S")
    p=os.path.join(out_dir,f"ledger_{ts}.json")
    with open(p,"w",encoding="utf-8") as f:
        json.dump(results,f,ensure_ascii=False,indent=2)
    return p

if __name__=="__main__":
    demo=[
        BacktestSpec("GC_Swing",{"ma_fast":50,"ma_slow":200},{"cvstamp":"v2"}),
        BacktestSpec("RSI_MR",{"rsi":14},{"cvstamp":"v2"})
    ]
    out=run_batch(demo)
    path=save_ledger(out,os.path.join(r"D:\GoogleDrive\Endeavour_Gov\audit","ledgers"))
    print(f"[engine] ledger saved → {path}")
