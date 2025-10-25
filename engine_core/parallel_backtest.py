\"\"\"engine_core/parallel_backtest.py — minimal smoke runner
- load two DSL samples
- produce minimal in-memory results and return summary dict
NOTE: vectorbt/dask integration will be added later.
\"\"\"
from __future__ import annotations
from typing import Dict, Any, Tuple
import json, os
from .metrics import basic_summary
from .cv import parse_cvstamp, make_splits

def load_json(p): 
    with open(p, 'r', encoding='utf-8') as f: 
        return json.load(f)

def run_smoke(samples_dir: str, cvstamp: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    a = load_json(os.path.join(samples_dir, 'GoldenCross_Swing.json'))
    b = load_json(os.path.join(samples_dir, 'RSI_MeanReversion.json'))
    # Stub dataset length
    n=100
    _splits = make_splits(n, parse_cvstamp(cvstamp))
    # Use placeholder summary for smoke
    summary = {
        a['name']: basic_summary(0.0, trades=10),
        b['name']: basic_summary(0.0, trades=8)
    }
    meta = {"splits": len(_splits), "n": n}
    return summary, meta
