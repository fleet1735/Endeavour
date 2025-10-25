# encoding: utf-8
# SSOT v8.2 LOCK: CVStampV2 literal & schema-aligned helpers
import math, pandas as pd

def make_cv_stamp(folds=5, embargo_days=10, windows=3, seed=42):
    return {
        "purged_kfold": {"folds": int(folds)},
        "embargo_days": int(embargo_days),
        "nested_wf": {"windows": int(windows)},
        "seed": int(seed),
    }

def _adjust_for_length(n_bars, folds, windows, embargo_days):
    # Exception policy (SSOT): folds := max(2, floor(len/250)), windows := max(1, floor(len/(folds*250))), embargo_days >= 5
    adj_folds = max(2, int(math.floor(n_bars/250))) if n_bars>0 else max(2, folds)
    adj_windows = max(1, int(math.floor(n_bars / max(adj_folds*250,1)))) if n_bars>0 else max(1, windows)
    adj_embargo = max(5, int(embargo_days))
    return adj_folds, adj_windows, adj_embargo

def split_purged_kfold(index: pd.Index, folds=5, embargo_days=10):
    n = len(index)
    folds, _, embargo_days = _adjust_for_length(n, folds, 1, embargo_days)
    fold_size = max(1, n // folds)
    for k in range(folds):
        start = k*fold_size
        end = (k+1)*fold_size if k < folds-1 else n
        test_idx = index[start:end]
        left = max(0, start - embargo_days)
        right = min(n, end + embargo_days)
        train_idx = index[0:left].append(index[right:n])
        yield train_idx, test_idx

def split_nested_walkforward(index: pd.Index, windows=3, folds=5, embargo_days=10):
    n = len(index)
    folds, windows, embargo_days = _adjust_for_length(n, folds, windows, embargo_days)
    wf_size = max(1, n // windows)
    for w in range(windows):
        start = w*wf_size
        end = (w+1)*wf_size if w < windows-1 else n
        wf_idx = index[start:end]
        # inside each WF window, do purged k-fold on the segment
        for tr, te in split_purged_kfold(wf_idx, folds=folds, embargo_days=embargo_days):
            yield tr, te
