\"\"\"engine_core/cv.py — CVStampV2 protocol (SSOT v8.2)
- parse_cvstamp: dict -> normalized stamp
- make_splits: dataset meta + stamp -> (train_idx, test_idx) tuples
NOTE: Purged K-Fold + Embargo + (stub) Nested WF; full logic to be filled.
\"\"\"
from __future__ import annotations
from typing import Dict, Any, List, Tuple

def parse_cvstamp(stamp: Dict[str, Any]) -> Dict[str, Any]:
    # Expected minimal keys (literal orientation kept)
    out = {
        "purged_kfold": dict(stamp.get("purged_kfold", {})),
        "embargo_days": int(stamp.get("embargo_days", 0)),
        "nested_wf": dict(stamp.get("nested_wf", {})),
        "seed": int(stamp.get("seed", 42)),
    }
    return out

def make_splits(n: int, stamp: Dict[str, Any]) -> List[Tuple[List[int], List[int]]]:
    # Minimal stub: 2-fold split without leakage (placeholder; replace with PurgedKFold+Embargo)
    k = max(2, int(stamp.get("purged_kfold", {}).get("folds", 2)))
    fold = n // k
    splits=[]
    for i in range(k):
        test_start=i*fold
        test_end = n if i==k-1 else (i+1)*fold
        test_idx=list(range(test_start, test_end))
        train_idx=list(range(0, test_start)) + list(range(test_end, n))
        # embargo stub (no-op)
        splits.append((train_idx, test_idx))
    return splits
