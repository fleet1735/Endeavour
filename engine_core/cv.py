# encoding: utf-8
# SSOT v8.2 LOCK-aligned CV helpers
# - CVStampV2 literal maker
# - Exception policy adjustment for short series
# - effective_cv_stamp(): stamp reflecting ACTUAL applied values (traceability)
# - Splitters: purged k-fold, nested walk-forward (pandas 2.x compliant)

import math
import numpy as np
import pandas as pd
from typing import Dict, Iterator, Tuple

def make_cv_stamp(folds: int = 5, embargo_days: int = 10, windows: int = 3, seed: int = 42) -> Dict:
    """Return base CVStampV2 literal (may be adjusted by effective_cv_stamp for actual use)."""
    return {
        "purged_kfold": {"folds": int(folds)},
        "embargo_days": int(embargo_days),
        "nested_wf": {"windows": int(windows)},
        "seed": int(seed),
    }

def _adjust_for_length(n_bars: int, folds: int, windows: int, embargo_days: int):
    """
    SSOT 예외정책:
      - folds := max(2, floor(len/250))
      - windows := max(1, floor(len / (folds*250)))
      - embargo_days >= 5
    """
    adj_folds = max(2, int(math.floor(n_bars/250))) if n_bars > 0 else max(2, folds)
    denom = max(adj_folds * 250, 1)
    adj_windows = max(1, int(math.floor(n_bars / denom))) if n_bars > 0 else max(1, windows)
    adj_embargo = max(5, int(embargo_days))
    return adj_folds, adj_windows, adj_embargo

def effective_cv_stamp(index: pd.Index, base_stamp: Dict) -> Dict:
    """
    Data index 길이에 기반하여 실제 적용될 folds/windows/embargo를 계산해 반환.
    이 값을 Excel Params / Ledger / 로그에 기록해야 추적성 보장.
    """
    n = len(index)
    base_folds = int(base_stamp.get("purged_kfold", {}).get("folds", 5))
    base_windows = int(base_stamp.get("nested_wf", {}).get("windows", 3))
    base_embargo = int(base_stamp.get("embargo_days", 10))
    seed = int(base_stamp.get("seed", 42))

    folds, windows, embargo = _adjust_for_length(n, base_folds, base_windows, base_embargo)
    return {
        "purged_kfold": {"folds": folds},
        "embargo_days": embargo,
        "nested_wf": {"windows": windows},
        "seed": seed,
    }

def _concat_index(a: pd.Index, b: pd.Index) -> pd.Index:
    """pandas 2.x에서 Index.append 대체: 값 배열을 이어 붙여 동일 dtype의 Index 생성."""
    if len(a) == 0: 
        return pd.Index(b, dtype=b.dtype)
    if len(b) == 0:
        return pd.Index(a, dtype=a.dtype)
    return pd.Index(np.concatenate([a.values, b.values]))

def split_purged_kfold(index: pd.Index, folds: int = 5, embargo_days: int = 10) -> Iterator[Tuple[pd.Index, pd.Index]]:
    """
    Purged K-Fold splitter with embargo around test windows.
    NOTE: 예외정책을 적용하여 folds/embargo를 보정한다.
    """
    n = len(index)
    folds, _, embargo_days = _adjust_for_length(n, folds, 1, embargo_days)
    fold_size = max(1, n // folds)
    for k in range(folds):
        start = k * fold_size
        end = (k + 1) * fold_size if k < folds - 1 else n
        test_idx = index[start:end]
        left = max(0, start - embargo_days)
        right = min(n, end + embargo_days)
        train_prefix = index[0:left]
        train_suffix = index[right:n]
        train_idx = _concat_index(train_prefix, train_suffix)
        yield train_idx, test_idx

def split_nested_walkforward(index: pd.Index, windows: int = 3, folds: int = 5, embargo_days: int = 10) -> Iterator[Tuple[pd.Index, pd.Index]]:
    """
    Nested Walk-Forward: 외곽을 windows로 분할 후 각 윈도우에서 purged k-fold 수행.
    예외정책으로 windows/folds/embargo를 보정한다.
    """
    n = len(index)
    folds, windows, embargo_days = _adjust_for_length(n, folds, windows, embargo_days)
    wf_size = max(1, n // windows)
    for w in range(windows):
        start = w * wf_size
        end = (w + 1) * wf_size if w < windows - 1 else n
        wf_idx = index[start:end]
        for tr, te in split_purged_kfold(wf_idx, folds=folds, embargo_days=embargo_days):
            yield tr, te
